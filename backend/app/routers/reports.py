"""
Reports API Router for CivicPulse AI.
Handles citizen report submissions, image uploads, AI classification,
duplicate checking, filtering, pagination, and upvoting.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from backend.app.database import get_db
from backend.app.models import Report, StatusUpdate
from backend.app.schemas import (
    ReportResponse, ReportListResponse, AIClassifyResponse,
    DuplicateCheckRequest, DuplicateCheckResponse, DuplicateItem,
    VALID_CATEGORIES, VALID_STATUSES, VALID_PRIORITIES
)
from backend.app.services.priority_engine import calculate_priority
from backend.app.services.ai_classifier import classify_issue_image
from backend.app.services.duplicate_detector import find_potential_duplicates
from backend.app.utils.image_handler import validate_and_save_image

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def generate_next_report_id(db: Session) -> str:
    """Generate sequential, human-friendly ID like CP-1007 by finding highest numeric suffix."""
    all_reports = db.query(Report.id).filter(Report.id.like("CP-%")).all()
    max_num = 1000
    for (r_id,) in all_reports:
        try:
            val = int(r_id.replace("CP-", ""))
            if val > max_num:
                max_num = val
        except ValueError:
            continue
    return f"CP-{max_num + 1}"


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    title: str = Form(..., min_length=3, max_length=200),
    description: str = Form(..., min_length=10),
    category: str = Form(...),
    latitude: float = Form(..., ge=-90.0, le=90.0),
    longitude: float = Form(..., ge=-180.0, le=180.0),
    address: str = Form(..., min_length=3, max_length=300),
    reporter_name: Optional[str] = Form("Anonymous Citizen"),
    reporter_contact: Optional[str] = Form(None),
    ai_classified: bool = Form(False),
    ai_confidence: Optional[float] = Form(None),
    ai_notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Submit a new civic complaint report.
    Accepts multipart/form-data with optional image file.
    Automatically scores issue priority using explainable hazard detection.
    """
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category '{category}'. Valid categories are: {', '.join(VALID_CATEGORIES)}"
        )

    # 1. Handle image upload if provided
    image_url = None
    if image and image.filename:
        image_url = validate_and_save_image(image)

    # 2. Run Explainable Smart Priority Scoring
    priority_label, priority_score, priority_reason = calculate_priority(
        category=category,
        title=title,
        description=description,
        has_image=bool(image_url),
        upvotes=0
    )

    # 3. Create Report Record
    report_id = generate_next_report_id(db)
    now = datetime.utcnow()

    new_report = Report(
        id=report_id,
        title=title.strip(),
        description=description.strip(),
        category=category,
        priority=priority_label,
        priority_score=priority_score,
        priority_reason=priority_reason,
        status="Reported",
        latitude=latitude,
        longitude=longitude,
        address=address.strip(),
        reporter_name=(reporter_name or "Anonymous Citizen").strip(),
        reporter_contact=(reporter_contact or "").strip() or None,
        image_url=image_url,
        ai_classified=ai_classified,
        ai_confidence=ai_confidence,
        ai_notes=ai_notes,
        is_demo=False,
        created_at=now,
        updated_at=now
    )
    db.add(new_report)
    db.flush()

    # 4. Create initial Status History record
    initial_status = StatusUpdate(
        report_id=new_report.id,
        old_status=None,
        new_status="Reported",
        changed_by="Citizen",
        remarks="Complaint registered into municipal public ledger.",
        created_at=now
    )
    db.add(initial_status)
    db.commit()
    db.refresh(new_report)

    return new_report


@router.get("", response_model=ReportListResponse)
def list_reports(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (Reported, Acknowledged, In Progress, Resolved)"),
    priority: Optional[str] = Query(None, description="Filter by priority (Low, Medium, High, Critical)"),
    search: Optional[str] = Query(None, description="Text search across title, description, address, or ID"),
    sort_by: str = Query("created_at", description="Field to sort by: created_at, priority_score, upvotes"),
    sort_order: str = Query("desc", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Retrieve paginated list of civic complaints with flexible search and filtering.
    """
    query = db.query(Report)

    # Filtering
    if category and category != "All":
        query = query.filter(Report.category == category)
    if status and status != "All":
        query = query.filter(Report.status == status)
    if priority and priority != "All":
        query = query.filter(Report.priority == priority)

    # Search
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Report.id.ilike(term),
                Report.title.ilike(term),
                Report.description.ilike(term),
                Report.address.ilike(term)
            )
        )

    # Sorting
    sort_col = Report.created_at
    if sort_by == "priority_score":
        sort_col = Report.priority_score
    elif sort_by == "upvotes":
        sort_col = Report.upvotes

    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    total = query.count()
    total_pages = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit
    reports = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "reports": reports
    }


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    """Retrieve full details of a specific civic complaint by its unique ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' was not found in the database."
        )
    return report


@router.post("/{report_id}/upvote", response_model=ReportResponse)
def upvote_report(report_id: str, db: Session = Depends(get_db)):
    """
    Citizen upvote / community affirmation.
    Increases issue urgency and recalculates priority score if needed.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found."
        )

    report.upvotes += 1
    
    # Recalculate priority with new upvotes
    priority_label, priority_score, priority_reason = calculate_priority(
        category=report.category,
        title=report.title,
        description=report.description,
        has_image=bool(report.image_url),
        upvotes=report.upvotes
    )
    report.priority = priority_label
    report.priority_score = priority_score
    report.priority_reason = priority_reason
    report.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(report)
    return report


@router.post("/ai-classify", response_model=AIClassifyResponse)
async def classify_image_endpoint(
    image: UploadFile = File(...),
    text_hint: Optional[str] = Form(None)
):
    """
    Analyze an uploaded image to predict the civic issue category.
    Uses Google Gemini Vision if API key is provided; otherwise uses transparent local fallback.
    """
    if image.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a JPEG, PNG, or WebP image."
        )

    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size exceeds 10MB limit."
        )

    result = await classify_issue_image(
        image_bytes=image_bytes,
        filename=image.filename,
        text_hint=text_hint
    )
    return result


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate_endpoint(
    req: DuplicateCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if a similar complaint already exists within geographic proximity (Haversine distance)
    and text similarity before citizen submits a duplicate ticket.
    """
    duplicates = find_potential_duplicates(
        db=db,
        category=req.category,
        title="",
        description=req.description,
        latitude=req.latitude,
        longitude=req.longitude,
        max_distance_meters=350.0,
        similarity_threshold=0.35
    )

    has_duplicates = len(duplicates) > 0
    message = (
        f"Found {len(duplicates)} similar reports nearby. You may upvote an existing report instead of creating a duplicate."
        if has_duplicates else "No similar nearby complaints detected. Safe to submit."
    )

    return {
        "has_duplicates": has_duplicates,
        "count": len(duplicates),
        "message": message,
        "duplicates": [DuplicateItem(**d) for d in duplicates]
    }

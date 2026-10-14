"""
Administrator API Router for CivicPulse AI.
Secures administrative workflows including authentication, official status transitions,
resolution notes, and resolution proof image uploads.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Report, StatusUpdate, AdminUser
from backend.app.schemas import (
    AdminLoginRequest, AdminLoginResponse, StatusUpdateCreate, ReportResponse, VALID_STATUSES
)
from backend.app.services.auth_service import (
    verify_password, create_access_token, get_current_admin
)
from backend.app.utils.image_handler import validate_and_save_image

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate municipal administrator credentials and issue a signed JWT session token.
    Default credentials for academic evaluation: admin / admin123
    """
    admin = db.query(AdminUser).filter(AdminUser.username == req.username.strip()).first()
    if not admin or not verify_password(req.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrator username or password."
        )

    token = create_access_token(data={"sub": admin.username, "role": admin.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_info": {
            "username": admin.username,
            "full_name": admin.full_name,
            "role": admin.role
        }
    }


@router.get("/me")
def get_admin_profile(current_admin: AdminUser = Depends(get_current_admin)):
    """Verify administrator JWT session and return profile info."""
    return {
        "username": current_admin.username,
        "full_name": current_admin.full_name,
        "role": current_admin.role
    }


@router.patch("/reports/{report_id}/status", response_model=ReportResponse)
def update_report_status(
    report_id: str,
    update_data: StatusUpdateCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Authorized municipal status transition.
    Logs transition into persistent status timeline with official remarks.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' was not found."
        )

    if update_data.new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{update_data.new_status}'. Allowed: {', '.join(VALID_STATUSES)}"
        )

    old_status = report.status
    now = datetime.utcnow()

    # Update report record
    report.status = update_data.new_status
    report.updated_at = now
    
    if update_data.new_status == "Resolved" and update_data.remarks:
        report.resolution_notes = update_data.remarks

    # Append to status history timeline
    timeline_entry = StatusUpdate(
        report_id=report.id,
        old_status=old_status,
        new_status=update_data.new_status,
        changed_by=f"{current_admin.full_name} ({current_admin.role})",
        remarks=update_data.remarks or f"Status transitioned from {old_status} to {update_data.new_status}.",
        created_at=now
    )
    db.add(timeline_entry)
    db.commit()
    db.refresh(report)

    return report


@router.post("/reports/{report_id}/resolve-with-proof", response_model=ReportResponse)
async def resolve_with_proof(
    report_id: str,
    remarks: str = Form(..., min_length=5),
    proof_image: Optional[UploadFile] = File(None),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Mark complaint as Resolved with mandatory official remarks and optional photographic proof.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' was not found."
        )

    resolution_img_url = None
    if proof_image and proof_image.filename:
        resolution_img_url = validate_and_save_image(proof_image, subfolder="resolutions")

    old_status = report.status
    now = datetime.utcnow()

    report.status = "Resolved"
    report.resolution_notes = remarks
    if resolution_img_url:
        report.resolution_image_url = resolution_img_url
    report.updated_at = now

    timeline_entry = StatusUpdate(
        report_id=report.id,
        old_status=old_status,
        new_status="Resolved",
        changed_by=f"{current_admin.full_name} ({current_admin.role})",
        remarks=f"Issue Resolved. Official notes: {remarks}",
        created_at=now
    )
    db.add(timeline_entry)
    db.commit()
    db.refresh(report)

    return report


@router.delete("/reports/{report_id}", status_code=status.HTTP_200_OK)
def delete_report(
    report_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete spam or invalid complaints (Admin only)."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        
    db.delete(report)
    db.commit()
    return {"message": f"Report '{report_id}' successfully deleted."}

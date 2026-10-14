"""
Analytics API Router for CivicPulse AI.
Computes real-time municipal health metrics, resolution KPIs, category distributions,
and historical trends directly from the SQLite database.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app.models import Report, StatusUpdate
from backend.app.schemas import AnalyticsResponse, VALID_CATEGORIES, VALID_STATUSES, VALID_PRIORITIES

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    """
    Compute comprehensive civic resolution analytics and trends directly from the database.
    Does NOT use hardcoded fake statistics.
    """
    total = db.query(Report).count()
    pending = db.query(Report).filter(Report.status == "Reported").count()
    acknowledged = db.query(Report).filter(Report.status == "Acknowledged").count()
    in_progress = db.query(Report).filter(Report.status == "In Progress").count()
    resolved = db.query(Report).filter(Report.status == "Resolved").count()
    
    active_in_progress = acknowledged + in_progress
    high_priority = db.query(Report).filter(Report.priority.in_(["High", "Critical"])).count()
    
    resolution_rate = round((resolved / total * 100.0), 1) if total > 0 else 0.0

    # 1. Category Distribution
    cat_rows = (
        db.query(Report.category, func.count(Report.id))
        .group_by(Report.category)
        .all()
    )
    category_breakdown = {cat: 0 for cat in VALID_CATEGORIES}
    for cat, count in cat_rows:
        category_breakdown[cat] = count

    # 2. Status Distribution
    status_rows = (
        db.query(Report.status, func.count(Report.id))
        .group_by(Report.status)
        .all()
    )
    status_breakdown = {st: 0 for st in VALID_STATUSES}
    for st, count in status_rows:
        status_breakdown[st] = count

    # 3. Priority Distribution
    priority_rows = (
        db.query(Report.priority, func.count(Report.id))
        .group_by(Report.priority)
        .all()
    )
    priority_breakdown = {pr: 0 for pr in VALID_PRIORITIES}
    for pr, count in priority_rows:
        priority_breakdown[pr] = count

    # 4. Daily Trends (Last 7 Days)
    today = datetime.utcnow().date()
    daily_trends = []
    
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        next_date = target_date + timedelta(days=1)
        
        # Reports created on that date
        reported_on_date = (
            db.query(Report)
            .filter(Report.created_at >= target_date, Report.created_at < next_date)
            .count()
        )
        
        # Reports resolved on that date
        resolved_on_date = (
            db.query(StatusUpdate)
            .filter(
                StatusUpdate.new_status == "Resolved",
                StatusUpdate.created_at >= target_date,
                StatusUpdate.created_at < next_date
            )
            .count()
        )

        daily_trends.append({
            "date": target_date.strftime("%b %d"),
            "full_date": str(target_date),
            "reported": reported_on_date,
            "resolved": resolved_on_date
        })

    return {
        "total_reports": total,
        "pending_reports": pending,
        "in_progress_reports": active_in_progress,
        "resolved_reports": resolved,
        "high_priority_reports": high_priority,
        "resolution_rate_percentage": resolution_rate,
        "category_breakdown": category_breakdown,
        "status_breakdown": status_breakdown,
        "priority_breakdown": priority_breakdown,
        "daily_trends": daily_trends
    }

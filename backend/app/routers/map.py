"""
Map API Router for CivicPulse AI.
Supplies map-ready geographic coordinates, marker styling properties,
and optional reverse-geocoding for Leaflet / OpenStreetMap integration.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import httpx

from backend.app.database import get_db
from backend.app.models import Report

router = APIRouter(prefix="/api/map", tags=["Map"])

PRIORITY_COLORS = {
    "Critical": "#EF4444",  # Crimson Red
    "High": "#F97316",      # Vivid Orange
    "Medium": "#F59E0B",    # Amber Yellow
    "Low": "#10B981"        # Emerald Green
}

STATUS_COLORS = {
    "Reported": "#6366F1",    # Indigo
    "Acknowledged": "#0EA5E9",# Sky Blue
    "In Progress": "#EAB308", # Amber
    "Resolved": "#10B981"     # Emerald
}


@router.get("/reports")
def get_map_reports(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Retrieve geographic points of all reported issues for Leaflet map markers.
    Includes visual color-coding for priority and status badges.
    """
    query = db.query(Report)

    if category and category != "All":
        query = query.filter(Report.category == category)
    if status and status != "All":
        query = query.filter(Report.status == status)
    if priority and priority != "All":
        query = query.filter(Report.priority == priority)

    reports = query.all()
    results = []

    for r in reports:
        results.append({
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "priority": r.priority,
            "priority_score": r.priority_score,
            "priority_color": PRIORITY_COLORS.get(r.priority, "#64748B"),
            "status": r.status,
            "status_color": STATUS_COLORS.get(r.status, "#64748B"),
            "latitude": r.latitude,
            "longitude": r.longitude,
            "address": r.address,
            "image_url": r.image_url,
            "upvotes": r.upvotes,
            "created_at": r.created_at.strftime("%b %d, %Y") if r.created_at else ""
        })

    return results


@router.get("/reverse-geocode")
async def reverse_geocode(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0)
) -> Dict[str, str]:
    """
    Reverse geocode coordinates to an address using OpenStreetMap Nominatim API,
    with a reliable fallback if external service is unreachable.
    """
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}"
    headers = {"User-Agent": "CivicPulseAI-CollegeProject/1.0 (academic-eval)"}

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                display_name = data.get("display_name")
                if display_name:
                    return {"address": display_name}
    except Exception:
        pass # Graceful fallback

    # Fallback to coordinate-based string
    return {"address": f"Location at {latitude:.5f}° N, {longitude:.5f}° E"}

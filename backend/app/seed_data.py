"""
Seed data generator for CivicPulse AI.
Populates realistic initial civic complaints on a fresh database
so that maps, dashboard metrics, and resolution charts can be immediately evaluated.

Note: All generated records are explicitly marked with `is_demo=True` 
to maintain clear distinction between academic demonstration data and actual citizen reports.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.models import Report, StatusUpdate, AdminUser
from backend.app.services.auth_service import hash_password
from backend.app.config import settings


DEMO_REPORTS = [
    {
        "id": "CP-1001",
        "title": "Deep Pothole on Main Arterial Avenue near Metro Station",
        "description": "Large dangerous pothole approximately 15cm deep causing severe two-wheeler skid hazards right outside the station entrance. Multiple bike commuters almost lost balance during peak morning traffic.",
        "category": "Roads & Potholes",
        "priority": "Critical",
        "priority_score": 88,
        "priority_reason": "Critical Priority (Score: 88/100) — Category risk baseline (30 pts); Critical safety triggers detected: accident, skid, hazard (+30 pts); Visual image evidence attached (+10 pts); Heavy traffic zone (+18 pts)",
        "status": "In Progress",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "address": "Opposite Metro Station Gate 2, Connaught Circus, New Delhi",
        "reporter_name": "Rohan Sharma",
        "reporter_contact": "rohan.sharma@example.com",
        "upvotes": 14,
        "image_url": "/uploads/sample_pothole.jpg",
        "ai_classified": True,
        "ai_confidence": 0.92,
        "ai_notes": "Detected deep roadway asphalt depression and road hazard.",
        "is_demo": True,
        "days_ago": 3,
        "status_timeline": [
            ("Reported", "Citizen submitted report with photo evidence.", 3),
            ("Acknowledged", "Roads & Highways Department verified location coordinates.", 2),
            ("In Progress", "Contractor crew deployed with cold-mix asphalt patch team.", 1)
        ]
    },
    {
        "id": "CP-1002",
        "title": "Overflowing Community Garbage Bin Spilling onto Sidewalk",
        "description": "Primary community waste bin has not been cleared for 4 days. Waste is spilling across the sidewalk and street, producing strong foul stench and attracting stray animals near primary school.",
        "category": "Overflowing Dustbins",
        "priority": "High",
        "priority_score": 68,
        "priority_reason": "High Priority (Score: 68/100) — Category risk baseline (16 pts); High-impact zone/safety keywords: school, stench, overflowing (+26 pts); Visual image evidence attached (+10 pts); Community confirmation (+16 pts)",
        "status": "Acknowledged",
        "latitude": 28.6219,
        "longitude": 77.2144,
        "address": "Sector 4 Market Corner, near Vidya Public School, New Delhi",
        "reporter_name": "Priya Patel",
        "reporter_contact": "priya.p@example.com",
        "upvotes": 8,
        "image_url": "/uploads/sample_garbage.jpg",
        "ai_classified": True,
        "ai_confidence": 0.88,
        "ai_notes": "Detected overflowing municipal solid waste dumpster.",
        "is_demo": True,
        "days_ago": 2,
        "status_timeline": [
            ("Reported", "Citizen reported sanitation issue.", 2),
            ("Acknowledged", "Sanitation division dispatched compactor truck schedule.", 1)
        ]
    },
    {
        "id": "CP-1003",
        "title": "Broken High-Intensity Streetlight creating Blind Spot",
        "description": "Streetlight pole #42 has been non-functional for a week. The entire pedestrian crosswalk and junction is pitch dark after 7 PM, creating safety concerns for women and evening pedestrians.",
        "category": "Street Lighting",
        "priority": "Medium",
        "priority_score": 52,
        "priority_reason": "Medium Priority (Score: 52/100) — Category risk baseline (24 pts); Environmental/nuisance triggers: dark street, pedestrian (+18 pts); Visual image evidence attached (+10 pts)",
        "status": "Resolved",
        "latitude": 28.6080,
        "longitude": 77.2190,
        "address": "Junction of 3rd Cross & Kasturba Gandhi Marg, New Delhi",
        "reporter_name": "Amit Verma",
        "reporter_contact": "amit.v@example.com",
        "upvotes": 5,
        "image_url": "/uploads/sample_light.jpg",
        "ai_classified": True,
        "ai_confidence": 0.85,
        "ai_notes": "Detected defective sodium-vapor street lamp fixture.",
        "is_demo": True,
        "days_ago": 6,
        "resolution_notes": "Municipal electrical division replaced burned-out 150W LED driver unit and inspected wiring. Illumination restored.",
        "status_timeline": [
            ("Reported", "Citizen submitted issue.", 6),
            ("Acknowledged", "Electrical department ticket generated #EL-491.", 5),
            ("In Progress", "Lineman assigned with hydraulic crane lift.", 3),
            ("Resolved", "Bulb and driver replaced successfully. Tested operational.", 1)
        ]
    },
    {
        "id": "CP-1004",
        "title": "Major Drinking Water Pipeline Leak Flooding Low-Lying Street",
        "description": "Underground potable water supply line burst under sidewalk. Clean drinking water is gushing out rapidly and flooding the road, water pressure in adjacent apartments has dropped to zero.",
        "category": "Water & Drainage",
        "priority": "Critical",
        "priority_score": 92,
        "priority_reason": "Critical Priority (Score: 92/100) — Category risk baseline (28 pts); Critical safety triggers detected: burst pipe, flooding, emergency (+34 pts); Visual image evidence attached (+10 pts); Heavy flow (+20 pts)",
        "status": "In Progress",
        "latitude": 28.6280,
        "longitude": 77.2050,
        "address": "Outer Ring Road service lane near Shanti Niketan, New Delhi",
        "reporter_name": "Sunita Roy",
        "reporter_contact": "sunita.roy@example.com",
        "upvotes": 22,
        "image_url": "/uploads/sample_water.jpg",
        "ai_classified": True,
        "ai_confidence": 0.91,
        "ai_notes": "Detected high-volume pressurized water main leak and road flooding.",
        "is_demo": True,
        "days_ago": 1,
        "status_timeline": [
            ("Reported", "Citizen reported active water leakage.", 1),
            ("Acknowledged", "Water Board emergency response unit dispatched valve shutoff team.", 1),
            ("In Progress", "Excavation crew repairing collar fracture on 12-inch main pipeline.", 0)
        ]
    },
    {
        "id": "CP-1005",
        "title": "Damaged Public Park Perimeter Railing and Broken Benches",
        "description": "Iron railing along children's play area is collapsed with rusted sharp edges exposed. Two concrete benches vandalized and broken. Children could sustain cuts.",
        "category": "Public Property Damage",
        "priority": "Medium",
        "priority_score": 48,
        "priority_reason": "Medium Priority (Score: 48/100) — Category risk baseline (20 pts); Environmental/safety triggers: children, park (+18 pts); Visual image attached (+10 pts)",
        "status": "Reported",
        "latitude": 28.6010,
        "longitude": 77.2250,
        "address": "Children Park Gate 3, India Gate circle lawns, New Delhi",
        "reporter_name": "Vikas Mehra",
        "reporter_contact": "vikas.m@example.com",
        "upvotes": 4,
        "image_url": "/uploads/sample_park.jpg",
        "ai_classified": True,
        "ai_confidence": 0.81,
        "ai_notes": "Detected structural railing displacement and park damage.",
        "is_demo": True,
        "days_ago": 1,
        "status_timeline": [
            ("Reported", "Citizen reported park equipment damage.", 1)
        ]
    },
    {
        "id": "CP-1006",
        "title": "Fallen Traffic Signpost Blocking Cyclist Lane",
        "description": "Speed limit and pedestrian crossing sign knocked down during heavy wind storm. Signpost is lying across the dedicated bicycle lane, forcing cyclists into rapid vehicle traffic.",
        "category": "Traffic & Signage",
        "priority": "High",
        "priority_score": 72,
        "priority_reason": "High Priority (Score: 72/100) — Category risk baseline (35 pts); High-impact zone/safety keywords: blocking, cyclist, traffic (+25 pts); Photo evidence attached (+10 pts); Detailed description (+2 pts)",
        "status": "Resolved",
        "latitude": 28.6185,
        "longitude": 77.2280,
        "address": "Barakhamba Road cycling corridor near Metro Pillar 18, New Delhi",
        "reporter_name": "Deepak Nair",
        "reporter_contact": "deepak.n@example.com",
        "upvotes": 7,
        "image_url": "/uploads/sample_traffic.jpg",
        "ai_classified": True,
        "ai_confidence": 0.89,
        "ai_notes": "Detected displaced metal traffic sign obstructing pathway.",
        "is_demo": True,
        "days_ago": 5,
        "resolution_notes": "Traffic police engineering team re-anchored post with new concrete base and high-tensile bolts.",
        "status_timeline": [
            ("Reported", "Cyclist submitted hazard complaint.", 5),
            ("Acknowledged", "Traffic control room dispatched patrolling unit.", 4),
            ("In Progress", "Field team removing obstruction and preparing foundation.", 3),
            ("Resolved", "Signpost re-erected and bicycle lane cleared.", 2)
        ]
    }
]


def seed_initial_data(db: Session):
    """Seed administrator user and demo civic reports if database is empty."""
    # 1. Seed default Admin User if not existing
    admin_exists = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
    if not admin_exists:
        admin = AdminUser(
            username=settings.ADMIN_USERNAME,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            full_name="Municipal Chief Administrator",
            role="Admin"
        )
        db.add(admin)
        db.commit()

    # 2. Check if reports already exist
    existing_count = db.query(Report).count()
    if existing_count > 0:
        return # Database already populated

    if not settings.SEED_DEMO_DATA:
        return

    now = datetime.utcnow()

    # 3. Insert realistic demo civic complaints
    for item in DEMO_REPORTS:
        created_time = now - timedelta(days=item["days_ago"], hours=item.get("days_ago", 1) * 2)
        updated_time = created_time + timedelta(hours=6)

        report = Report(
            id=item["id"],
            title=item["title"],
            description=item["description"],
            category=item["category"],
            priority=item["priority"],
            priority_score=item["priority_score"],
            priority_reason=item["priority_reason"],
            status=item["status"],
            latitude=item["latitude"],
            longitude=item["longitude"],
            address=item["address"],
            reporter_name=item["reporter_name"],
            reporter_contact=item["reporter_contact"],
            upvotes=item["upvotes"],
            image_url=item["image_url"],
            ai_classified=item["ai_classified"],
            ai_confidence=item["ai_confidence"],
            ai_notes=item["ai_notes"],
            resolution_notes=item.get("resolution_notes"),
            is_demo=True,
            created_at=created_time,
            updated_at=updated_time
        )
        db.add(report)
        db.flush() # Populate foreign key for status history

        # Add timeline steps
        for step_status, remark, days_offset in item.get("status_timeline", []):
            step_time = now - timedelta(days=days_offset)
            status_upd = StatusUpdate(
                report_id=report.id,
                old_status=None if step_status == "Reported" else "Reported",
                new_status=step_status,
                changed_by="Citizen" if step_status == "Reported" else "Municipal Authority",
                remarks=remark,
                created_at=step_time
            )
            db.add(status_upd)

    db.commit()

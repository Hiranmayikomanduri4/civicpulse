"""
SQLAlchemy Database Models for CivicPulse AI.
Includes models for Civic Reports, Status History, and Administrator Authentication.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Report(Base):
    __tablename__ = "reports"

    # Unique human-readable Report ID (e.g., 'CP-1001')
    id = Column(String(30), primary_key=True, index=True)
    
    # Core Issue Information
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    
    # Smart Priority Detection
    priority = Column(String(20), nullable=False, default="Medium", index=True) # Low, Medium, High, Critical
    priority_score = Column(Integer, default=50) # 1 to 100
    priority_reason = Column(Text, nullable=True) # Explainable breakdown
    
    # Workflow Status
    status = Column(String(50), nullable=False, default="Reported", index=True) # Reported, Acknowledged, In Progress, Resolved
    
    # Location Information (Leaflet / OpenStreetMap)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(300), nullable=False)
    
    # Media & AI Vision Verification
    image_url = Column(String(300), nullable=True)
    ai_classified = Column(Boolean, default=False)
    ai_confidence = Column(Float, nullable=True)
    ai_notes = Column(Text, nullable=True)
    
    # Reporter Information (Optional for Citizen Privacy)
    reporter_name = Column(String(100), nullable=True, default="Anonymous Citizen")
    reporter_contact = Column(String(100), nullable=True)
    
    # Community Engagement
    upvotes = Column(Integer, default=0)
    
    # Resolution Information (Logged by Administrator)
    resolution_notes = Column(Text, nullable=True)
    resolution_image_url = Column(String(300), nullable=True)
    
    # Metadata
    is_demo = Column(Boolean, default=False) # Transparent indicator for demo/sample records
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status Timeline Relationship
    status_history = relationship(
        "StatusUpdate",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="StatusUpdate.created_at.asc()"
    )

    def to_dict(self):
        """Serialize model to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "priority_score": self.priority_score,
            "priority_reason": self.priority_reason,
            "status": self.status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "image_url": self.image_url,
            "ai_classified": self.ai_classified,
            "ai_confidence": self.ai_confidence,
            "ai_notes": self.ai_notes,
            "reporter_name": self.reporter_name,
            "reporter_contact": self.reporter_contact,
            "upvotes": self.upvotes,
            "resolution_notes": self.resolution_notes,
            "resolution_image_url": self.resolution_image_url,
            "is_demo": self.is_demo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status_history": [sh.to_dict() for sh in self.status_history] if self.status_history else []
        }


class StatusUpdate(Base):
    __tablename__ = "status_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(30), ForeignKey("reports.id"), nullable=False, index=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by = Column(String(100), default="Administrator")
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    report = relationship("Report", back_populates="status_history")

    def to_dict(self):
        return {
            "id": self.id,
            "report_id": self.report_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.changed_by,
            "remarks": self.remarks,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), default="Municipal Administrator")
    role = Column(String(50), default="Admin")
    created_at = Column(DateTime, default=datetime.utcnow)

"""
Pydantic Schemas for Request Validation and Response Serialization.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


# Valid categories and statuses
VALID_CATEGORIES = [
    "Roads & Potholes",
    "Garbage & Sanitation",
    "Street Lighting",
    "Water & Drainage",
    "Public Property Damage",
    "Overflowing Dustbins",
    "Traffic & Signage",
    "Parks & Environment",
    "Other Infrastructure"
]

VALID_STATUSES = [
    "Reported",
    "Acknowledged",
    "In Progress",
    "Resolved"
]

VALID_PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]


# Status History Schema
class StatusUpdateSchema(BaseModel):
    id: int
    report_id: str
    old_status: Optional[str] = None
    new_status: str
    changed_by: str
    remarks: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusUpdateCreate(BaseModel):
    new_status: str = Field(..., description="New status: Reported, Acknowledged, In Progress, Resolved")
    remarks: Optional[str] = Field(None, description="Official administrative remark or resolution notes")
    changed_by: Optional[str] = Field("Municipal Administrator", description="Name/Role of official")

    @field_validator("new_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v


# Civic Report Base & Response Schemas
class ReportBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    category: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str = Field(..., min_length=3, max_length=300)
    reporter_name: Optional[str] = Field("Anonymous Citizen", max_length=100)
    reporter_contact: Optional[str] = Field(None, max_length=100)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return v


class ReportCreate(ReportBase):
    ai_classified: bool = False
    ai_confidence: Optional[float] = None
    ai_notes: Optional[str] = None


class ReportResponse(ReportBase):
    id: str
    priority: str
    priority_score: int
    priority_reason: Optional[str] = None
    status: str
    image_url: Optional[str] = None
    ai_classified: bool = False
    ai_confidence: Optional[float] = None
    ai_notes: Optional[str] = None
    upvotes: int = 0
    resolution_notes: Optional[str] = None
    resolution_image_url: Optional[str] = None
    is_demo: bool = False
    created_at: datetime
    updated_at: datetime
    status_history: List[StatusUpdateSchema] = []

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    reports: List[ReportResponse]


# AI Classification Schemas
class AIClassifyResponse(BaseModel):
    predicted_category: str
    confidence: float
    explanation: str
    is_ai_vision: bool = Field(..., description="True if real Gemini Vision AI was used, False if fallback classifier")
    alternative_categories: List[Dict[str, Any]] = []


# Duplicate Detection Schemas
class DuplicateCheckRequest(BaseModel):
    category: str
    description: str
    latitude: float
    longitude: float


class DuplicateItem(BaseModel):
    id: str
    title: str
    category: str
    status: str
    priority: str
    distance_meters: float
    similarity_score: float # 0.0 to 1.0
    created_at: datetime
    image_url: Optional[str] = None


class DuplicateCheckResponse(BaseModel):
    has_duplicates: bool
    count: int
    message: str
    duplicates: List[DuplicateItem] = []


# Analytics Schemas
class AnalyticsResponse(BaseModel):
    total_reports: int
    pending_reports: int
    in_progress_reports: int
    resolved_reports: int
    high_priority_reports: int
    resolution_rate_percentage: float
    category_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]
    priority_breakdown: Dict[str, int]
    daily_trends: List[Dict[str, Any]]


# Admin Authentication Schemas
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: Dict[str, Any]

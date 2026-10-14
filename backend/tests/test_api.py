"""
Automated Integration and Unit Test Suite for CivicPulse AI.
Tests backend endpoints, database persistence, priority scoring,
duplicate detection, analytics computations, and admin security.
"""
import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal, init_db
from backend.app.models import Report

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure database is seeded before running tests."""
    init_db()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CivicPulse AI"
    assert data["database"] == "connected"


def test_list_reports():
    """Test retrieving reports list with pagination and filtering."""
    response = client.get("/api/reports?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "reports" in data
    assert len(data["reports"]) <= 5
    assert data["total"] >= 6


def test_get_single_report():
    """Test retrieving a single report by ID."""
    response = client.get("/api/reports/CP-1001")
    assert response.status_code == 200
    report = response.json()
    assert report["id"] == "CP-1001"
    assert "status_history" in report
    assert len(report["status_history"]) >= 1


def test_get_nonexistent_report():
    """Test 404 for non-existent report ID."""
    response = client.get("/api/reports/CP-999999")
    assert response.status_code == 404


def test_create_report_validation():
    """Test validation errors on missing required fields."""
    response = client.post("/api/reports", data={"title": "Short"})
    assert response.status_code == 422 # Pydantic validation error


def test_create_report_success():
    """Test successfully creating a report with smart priority scoring."""
    form_data = {
        "title": "Severe Waterlogging and Blocked Storm Drain near City Hospital",
        "description": "Due to continuous rainfall, the storm drain is completely clogged with debris. Flooding is blocking emergency ambulance access to the hospital.",
        "category": "Water & Drainage",
        "latitude": 28.6150,
        "longitude": 77.2100,
        "address": "Hospital Road Sector 3, New Delhi",
        "reporter_name": "Test Citizen",
        "reporter_contact": "test@example.com"
    }
    response = client.post("/api/reports", data=form_data)
    assert response.status_code == 201
    created = response.json()
    assert created["id"].startswith("CP-")
    assert created["title"] == form_data["title"]
    assert created["status"] == "Reported"
    # Should detect high or critical priority because of 'hospital' and 'flooding'
    assert created["priority"] in ["High", "Critical"]
    assert created["priority_score"] >= 55
    assert "priority_reason" in created


def test_upvote_report():
    """Test citizen upvoting and urgency increase."""
    res_before = client.get("/api/reports/CP-1002")
    before_upvotes = res_before.json()["upvotes"]

    res_upvote = client.post("/api/reports/CP-1002/upvote")
    assert res_upvote.status_code == 200
    after_upvotes = res_upvote.json()["upvotes"]
    assert after_upvotes == before_upvotes + 1


def test_duplicate_detection():
    """Test spatial and textual duplicate check."""
    # Near CP-1001 coords (28.6139, 77.2090)
    req_data = {
        "category": "Roads & Potholes",
        "description": "Very big pothole right outside metro station causing bikes to fall",
        "latitude": 28.6140,
        "longitude": 77.2091
    }
    response = client.post("/api/reports/check-duplicate", json=req_data)
    assert response.status_code == 200
    data = response.json()
    assert data["has_duplicates"] is True
    assert len(data["duplicates"]) >= 1
    assert data["duplicates"][0]["distance_meters"] < 100


def test_analytics_calculation():
    """Test real-time analytics aggregation."""
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_reports"] >= 6
    assert "resolution_rate_percentage" in data
    assert "category_breakdown" in data
    assert "status_breakdown" in data
    assert "priority_breakdown" in data
    assert "daily_trends" in data
    assert len(data["daily_trends"]) == 7


def test_map_reports():
    """Test map marker endpoint returning color-coded geo points."""
    response = client.get("/api/map/reports")
    assert response.status_code == 200
    markers = response.json()
    assert isinstance(markers, list)
    assert len(markers) >= 6
    item = markers[0]
    assert "latitude" in item
    assert "longitude" in item
    assert "priority_color" in item
    assert "status_color" in item


def test_admin_authentication_and_status_update():
    """Test admin login, token retrieval, and secured status transitions."""
    # 1. Invalid credentials
    bad_login = client.post("/api/admin/login", json={"username": "admin", "password": "wrongpassword"})
    assert bad_login.status_code == 401

    # 2. Valid credentials (default admin / admin123)
    login_res = client.post("/api/admin/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Unauthorized status update without token
    unauth_patch = client.patch(
        "/api/admin/reports/CP-1005/status",
        json={"new_status": "In Progress", "remarks": "Team dispatched."}
    )
    assert unauth_patch.status_code == 401

    # 4. Authorized status update with token
    auth_patch = client.patch(
        "/api/admin/reports/CP-1005/status",
        headers=headers,
        json={"new_status": "In Progress", "remarks": "Welding and carpentry team dispatched."}
    )
    assert auth_patch.status_code == 200
    updated_report = auth_patch.json()
    assert updated_report["status"] == "In Progress"
    
    # Verify status history timeline
    assert len(updated_report["status_history"]) >= 2
    last_entry = updated_report["status_history"][-1]
    assert last_entry["new_status"] == "In Progress"
    assert "Welding" in last_entry["remarks"]

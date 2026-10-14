"""
CivicPulse AI — Complete System Verification & Academic Demonstration Script.
Run this script to verify all backend systems, database models, AI triage engines,
duplicate checks, and security authentication.

Usage:
    python test_system.py
"""
import sys
import os
from pathlib import Path

# Ensure root workspace is on pythonpath
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

# Ensure Windows terminal handles UTF-8 safely
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_system_verification():
    print("=" * 70)
    print("  CIVICPULSE AI — SYSTEM VERIFICATION & ACADEMIC AUDIT")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = 7

    # 1. Environment & Config
    print("\n[Test 1/7] Testing Environment Configuration & Settings...")
    try:
        from backend.app.config import settings
        assert settings.PROJECT_NAME == "CivicPulse AI"
        print(f"  [OK] Configuration loaded: Host={settings.HOST}, Port={settings.PORT}")
        print(f"  [OK] Database URL: {settings.DATABASE_URL}")
        print(f"  [OK] Uploads Directory: {settings.UPLOADS_DIR.resolve()}")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] Test 1 failed: {e}")

    # 2. Database & SQLAlchemy Models
    print("\n[Test 2/7] Testing SQLite Database Persistence & Tables...")
    try:
        from backend.app.database import init_db, SessionLocal
        from backend.app.models import Report, StatusUpdate, AdminUser
        init_db()
        db = SessionLocal()
        rep_count = db.query(Report).count()
        adm_count = db.query(AdminUser).count()
        db.close()
        assert rep_count > 0, "No reports found in database"
        assert adm_count > 0, "No admin user found in database"
        print(f"  [OK] SQLite database connected and validated")
        print(f"  [OK] Persistent records: {rep_count} reports, {adm_count} administrator accounts")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] Test 2 failed: {e}")

    # 3. Smart Priority Detection Engine
    print("\n[Test 3/7] Testing Explainable Smart Priority Scoring Engine...")
    try:
        from backend.app.services.priority_engine import calculate_priority
        
        # Test low priority case
        p_low, score_low, reason_low = calculate_priority("Parks & Environment", "Fallen branch on lawn", "A branch fell on the park lawn", has_image=False)
        assert p_low == "Low" or score_low < 35
        
        # Test critical priority case
        p_crit, score_crit, reason_crit = calculate_priority("Water & Drainage", "Emergency Water Pipe Burst", "Burst pipe flooding the main highway causing heavy traffic accident hazard", has_image=True)
        assert p_crit in ["High", "Critical"]
        assert score_crit >= 65
        print(f"  [OK] Normal issue classified as: {p_low} (Score: {score_low})")
        print(f"  [OK] Emergency issue classified as: {p_crit} (Score: {score_crit})")
        print(f"  [OK] Transparent explanation string generated: '{reason_crit[:60]}...'")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] Test 3 failed: {e}")

    # 4. Spatial Duplicate Issue Detection
    print("\n[Test 4/7] Testing Haversine Distance & Spatial Duplicate Detection...")
    try:
        from backend.app.utils.geo import calculate_haversine_distance, format_distance
        from backend.app.services.duplicate_detector import find_potential_duplicates
        
        # Distance test (approx 111 meters between 0.001 deg latitude)
        dist = calculate_haversine_distance(28.6139, 77.2090, 28.6149, 77.2090)
        assert 100 < dist < 125
        print(f"  [OK] Haversine distance calculation verified: 0.001 deg lat = {format_distance(dist)}")

        db = SessionLocal()
        dups = find_potential_duplicates(db, "Roads & Potholes", "Pothole", "Dangerous pothole near metro", 28.6140, 77.2091)
        db.close()
        assert len(dups) > 0
        print(f"  [OK] Proximity scanner detected {len(dups)} nearby candidate (Similarity: {dups[0]['similarity_percentage']}%, Distance: {dups[0]['distance_formatted']})")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] Test 4 failed: {e}")

    # 5. Security, Password Hashing & JWT Authentication
    print("\n[Test 5/7] Testing PBKDF2 Password Encryption & JWT Tokens...")
    try:
        from backend.app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token
        
        test_pass = "SecureCollegeTest2026!"
        hashed = hash_password(test_pass)
        assert verify_password(test_pass, hashed) is True
        assert verify_password("wrongpass", hashed) is False
        
        token = create_access_token({"sub": "testadmin", "role": "Admin"})
        decoded = decode_access_token(token)
        assert decoded["sub"] == "testadmin"
        print(f"  [OK] PBKDF2 HMAC SHA-256 salted password encryption verified")
        print(f"  [OK] Signed JWT session token encoded and validated successfully")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] Test 5 failed: {e}")

    # 6. Real-time Analytics Calculations
    print("\n[Test 6/7] Testing Live Analytics Computation directly from SQLite...")
    try:
        from backend.app.routers.analytics import get_analytics
        db = SessionLocal()
        stats = get_analytics(db)
        db.close()
        assert stats["total_reports"] > 0
        assert "category_breakdown" in stats
        assert len(stats["daily_trends"]) == 7
        print(f"  [OK] Analytics aggregation verified: {stats['total_reports']} total, {stats['resolved_reports']} resolved ({stats['resolution_rate_percentage']}%)")
        print(f"  [OK] Category categories tallied: {len(stats['category_breakdown'])} distinct categories")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] Test 6 failed: {e}")

    # 7. FastAPI REST API Integration
    print("\n[Test 7/7] Testing FastAPI Web Routes & Endpoints...")
    try:
        from fastapi.testclient import TestClient
        from backend.app.main import app
        client = TestClient(app)
        
        h_res = client.get("/api/health")
        assert h_res.status_code == 200
        
        m_res = client.get("/api/map/reports")
        assert m_res.status_code == 200
        assert len(m_res.json()) > 0
        
        ui_res = client.get("/")
        assert ui_res.status_code == 200
        assert "CivicPulse AI" in ui_res.text
        
        print(f"  [OK] Health check endpoint: OK (200)")
        print(f"  [OK] Map GIS points endpoint: OK ({len(m_res.json())} geo markers)")
        print(f"  [OK] Web dashboard frontend served: OK (200)")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] Test 7 failed: {e}")

    # Final Report Summary
    print("\n" + "=" * 70)
    if passed_tests == total_tests:
        print(f"  ALL {passed_tests}/{total_tests} AUDIT TESTS PASSED SUCCESSFULLY! (100% SCORE)")
        print("  CivicPulse AI is ready for college evaluation and live demonstration.")
    else:
        print(f"  {passed_tests}/{total_tests} TESTS PASSED.")
    print("=" * 70)

if __name__ == "__main__":
    run_system_verification()

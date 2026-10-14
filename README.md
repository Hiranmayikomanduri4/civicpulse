# CivicPulse AI — Smart Civic Issue Reporting & Resolution Platform
> **AI-Powered Urban Infrastructure Management, Intelligent Triage, & Citizen Resolution Platform**  
> *Developed for Academic Evaluation, College Project Review, & Viva Presentation*

---

## 📌 1. Project Overview & Objectives

**CivicPulse AI** is a full-stack, AI-enabled civic-tech web application that bridges the communication gap between citizens and municipal authorities. It empowers citizens to report public infrastructure failures—such as dangerous potholes, broken streetlights, water pipeline fractures, and overflowing waste bins—while giving municipal officers an intelligent, automated dashboard to triage, prioritize, and resolve community complaints.

### Key Objectives:
- **Transparent Citizen Participation:** Allow any citizen to register geotagged civic complaints with photo evidence without bureaucratic barriers.
- **AI-Assisted Vision Classification:** Automatically identify and recommend the appropriate municipal department using computer vision (Google Gemini 1.5 Flash Vision / Heuristic Fallback).
- **Explainable Smart Priority Scoring:** Automatically calculate hazard urgency (Low, Medium, High, Critical) using a transparent multi-factor scoring model to protect human life and urban safety.
- **Spatial Duplicate Detection:** Prevent municipal backlog by identifying nearby duplicate complaints using Haversine geodesic distance and text similarity.
- **Open Resolution Tracking:** Provide real-time public auditability through interactive status timelines (`Reported` ➔ `Acknowledged` ➔ `In Progress` ➔ `Resolved`).

---

## 🏙️ 2. Problem Statement & Proposed Solution

### The Real-World Challenge:
Modern municipal corporations struggle with fragmented, slow, and opaque issue reporting channels:
1. **Unstructured Data:** Citizens submit vague reports without exact coordinates or department classification.
2. **Duplication Fatigue:** Dozens of citizens report the same pothole, overwhelming municipal call centers.
3. **Delayed Triage:** Critical emergencies (e.g., exposed sparking power cables or burst water mains) get lost in queues behind minor aesthetic complaints.
4. **Lack of Transparency:** Citizens rarely know if their complaint was received, acknowledged, or resolved.

### The CivicPulse AI Solution:
```
[Citizen Uploads Photo] 
       │
       ▼
[AI Vision Categorization] ─── (Recommends Dept: Roads, Water, Electricity)
       │
       ▼
[Spatial Proximity Check] ──── (Detects nearby duplicates via Haversine distance)
       │
       ▼
[Explainable Priority Engine] ─ (Calculates Urgency 1-100 based on hazard keywords)
       │
       ▼
[Persistent SQLite Ledger] ─── (Real-time GIS Map + Municipal Admin Console)
```

---

## 🏛️ 3. Full-Stack System Architecture

CivicPulse AI is built with a decoupled 3-tier architecture ensuring zero vendor lock-in, zero hosting costs, and fast local execution:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION TIER (FRONTEND)                    │
│  - Responsive Vanilla JS SPA (No complex build step, runs anywhere)    │
│  - Leaflet.js + OpenStreetMap (Interactive GIS Map & Location Picker)  │
│  - Chart.js (Real-Time Category & 7-Day Resolution Velocity Charts)    │
│  - Modern Civic-Tech CSS (Glassmorphism, Dark Mode, Micro-animations)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST (JSON / Multipart Forms)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION TIER (FASTAPI)                      │
│  - Python 3.12 + FastAPI ASGI Framework                                │
│  - Pydantic v2 (Strict Schema Validation & Serialization)              │
│  - Security: JWT Bearer Tokens + Salted PBKDF2 Password Hashing        │
│  - AI Vision Service: Google Gemini 1.5 Flash API + Heuristic Fallback │
│  - Smart Priority Engine: Multi-factor Hazard Scoring Rule System      │
│  - Duplicate Detector: Haversine Distance + Token Jaccard Similarity   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SQLAlchemy 2.0 ORM
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         DATA TIER (PERSISTENCE)                        │
│  - SQLite Database (`civicpulse.db`) with Foreign Key Constraints      │
│  - Persistent Media Directory (`backend/uploads/`)                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 4. Technology Stack

| Layer | Technology | Justification & Role |
| :--- | :--- | :--- |
| **Backend Language** | **Python 3.12** | Industry-standard language for AI, data science, and web APIs. |
| **Web Framework** | **FastAPI** | High-performance asynchronous Python REST framework with auto-generated Swagger docs. |
| **ASGI Server** | **Uvicorn** | Fast, production-ready server running on `127.0.0.1:8000`. |
| **Database** | **SQLite + SQLAlchemy 2.0** | Zero-configuration relational database with full ACID compliance and persistence. |
| **Validation** | **Pydantic v2** | Strong data typing and validation for incoming complaint submissions. |
| **GIS / Mapping** | **Leaflet + OpenStreetMap** | Open-source interactive map without requiring paid Google Maps API keys. |
| **Data Visualization**| **Chart.js** | Dynamic client-side charts for municipal analytics. |
| **AI Vision Model** | **Google Gemini 1.5 Flash** | Multimodal vision model (with built-in explainable offline fallback). |
| **Security** | **PyJWT + PBKDF2-HMAC** | Cryptographic token sessions and salted password storage. |

---

## 📁 5. Complete Folder Structure

```
CivicPulse-AI-Full-Project/
│
├── .env.example              # Environment variables template
├── .env                      # Local environment configuration
├── .gitignore                # Git ignore rules for virtual environments & db
├── requirements.txt          # Python dependencies
├── start.bat                 # 1-Click Windows execution script
├── test_system.py            # Comprehensive 7-point academic system audit script
├── pytest.ini                # Pytest configuration
├── README.md                 # Complete documentation & viva review guide
│
├── backend/
│   ├── __init__.py
│   ├── requirements.txt      # Backend specific requirements
│   ├── uploads/              # Uploaded complaint photos & resolution proofs
│   │   ├── .gitkeep
│   │   └── sample_*.jpg      # Realistic initial demonstration photos
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI server initialization & static mount
│   │   ├── config.py         # Application settings & environment loader
│   │   ├── database.py       # SQLAlchemy session & SQLite connection engine
│   │   ├── models.py         # Relational database models (Report, Status, Admin)
│   │   ├── schemas.py        # Pydantic request/response schemas
│   │   ├── seed_data.py      # Seed realistic initial civic issues with demo flag
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── reports.py    # Complaint CRUD, upvotes, AI classification
│   │   │   ├── analytics.py  # Live municipal stats & 7-day velocity
│   │   │   ├── map.py        # Map geo-markers & reverse geocoding
│   │   │   └── admin.py      # Admin login, status updates, resolution proofs
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_classifier.py     # Gemini Vision + Heuristic Fallback
│   │   │   ├── priority_engine.py   # Multi-factor explainable priority scoring
│   │   │   ├── duplicate_detector.py# Haversine distance + Jaccard similarity
│   │   │   └── auth_service.py      # PBKDF2 hashing + JWT token manager
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── geo.py        # Haversine geographic formula
│   │       └── image_handler.py # Image validation, sizing & secure storage
│   │
│   └── tests/
│       ├── __init__.py
│       └── test_api.py       # Automated 11-point Pytest integration test suite
│
└── frontend/
    ├── index.html            # Single Page Application HTML5 Dashboard
    ├── css/
    │   └── styles.css        # Modern Civic-Tech CSS design system
    ├── js/
    │   ├── api.js            # API client wrapper with authentication
    │   ├── map.js            # Leaflet GIS map integration & custom markers
    │   ├── charts.js         # Chart.js visualizations
    │   └── app.js            # Main application controller & state manager
    └── assets/
        └── logo.svg          # Vector CivicPulse AI brand icon
```

---

## 🗄️ 6. Database Design & Relational Schema

Data is stored persistently in SQLite using SQLAlchemy ORM. The relational model enforces referential integrity:

### 1. `reports` Table (Primary Civic Ledger)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(30) | PRIMARY KEY, INDEX | Unique human-readable ticket ID (e.g., `CP-1001`). |
| `title` | VARCHAR(200) | NOT NULL, INDEX | Brief summary of the civic problem. |
| `description` | TEXT | NOT NULL | Complete citizen description. |
| `category` | VARCHAR(100) | NOT NULL, INDEX | Municipal category (Roads, Water, Lighting, etc.). |
| `priority` | VARCHAR(20) | NOT NULL, INDEX | `Low`, `Medium`, `High`, or `Critical`. |
| `priority_score` | INTEGER | DEFAULT 50 | Numerical hazard score (1 to 100). |
| `priority_reason`| TEXT | NULLABLE | Transparent written breakdown of score factors. |
| `status` | VARCHAR(50) | NOT NULL, INDEX | `Reported`, `Acknowledged`, `In Progress`, `Resolved`. |
| `latitude` | FLOAT | NOT NULL | GPS Latitude (-90 to +90). |
| `longitude` | FLOAT | NOT NULL | GPS Longitude (-180 to +180). |
| `address` | VARCHAR(300) | NOT NULL | Street landmark or reverse-geocoded address. |
| `image_url` | VARCHAR(300) | NULLABLE | Relative path to uploaded photographic evidence. |
| `ai_classified` | BOOLEAN | DEFAULT FALSE | Flag indicating if visual AI was invoked. |
| `ai_confidence` | FLOAT | NULLABLE | Model confidence score (0.0 to 1.0). |
| `ai_notes` | TEXT | NULLABLE | Explanation produced by AI model. |
| `reporter_name` | VARCHAR(100) | DEFAULT 'Anonymous' | Optional citizen name for privacy. |
| `reporter_contact`| VARCHAR(100)| NULLABLE | Optional citizen contact for resolution alerts. |
| `upvotes` | INTEGER | DEFAULT 0 | Community affirmation / severity endorsements. |
| `resolution_notes`| TEXT | NULLABLE | Official remarks recorded by municipal officer. |
| `resolution_image_url`| VARCHAR(300)| NULLABLE | Photo proof of resolution. |
| `is_demo` | BOOLEAN | DEFAULT FALSE | Transparent label for sample demo records. |
| `created_at` | DATETIME | DEFAULT UTC NOW | Complaint creation timestamp. |
| `updated_at` | DATETIME | ON UPDATE UTC NOW | Last modification timestamp. |

### 2. `status_updates` Table (Auditable Resolution Timeline)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique log ID. |
| `report_id` | VARCHAR(30) | FOREIGN KEY (`reports.id`) | Relational link to the complaint ticket. |
| `old_status` | VARCHAR(50) | NULLABLE | Previous status state. |
| `new_status` | VARCHAR(50) | NOT NULL | Transitioned status state. |
| `changed_by` | VARCHAR(100) | DEFAULT 'Admin' | Name/Role of official who authorized change. |
| `remarks` | TEXT | NULLABLE | Official operational remarks. |
| `created_at` | DATETIME | DEFAULT UTC NOW | Exact timestamp of status change. |

### 3. `admin_users` Table (Municipal Security)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY | User ID. |
| `username` | VARCHAR(50) | UNIQUE, INDEX | Administrator handle (default: `admin`). |
| `password_hash` | VARCHAR(255) | NOT NULL | Salted PBKDF2 HMAC SHA-256 hash. |
| `full_name` | VARCHAR(100) | NOT NULL | Official name of administrator. |
| `role` | VARCHAR(50) | DEFAULT 'Admin' | Authorization role. |

---

## 🧠 7. AI/ML Components & Explainable Algorithms

CivicPulse AI does not use fake labels or black-box buzzwords. It implements three distinct, real computational intelligence modules:

### A. Image-Based Issue Classification (`ai_classifier.py`)
1. **Google Gemini 1.5 Flash Integration:**
   - When `GEMINI_API_KEY` is configured in `.env`, the backend encodes the uploaded image into base64 and invokes the Gemini REST API.
   - It prompts the model to classify the image into one of the 9 strict municipal categories, returning a confidence percentage and a 1-sentence visual reasoning.
2. **Transparent Heuristic Fallback Engine:**
   - If no API key is provided, the platform **does not crash or show fake predictions**.
   - It analyzes image dimensions, color profiles (e.g. night illumination vs daylight asphalt), and contextual user input using Pillow (`PIL`).
   - It outputs the prediction with a clear disclosure:
     > *"Fallback Engine: GEMINI_API_KEY is not configured. This is an explainable heuristic, not a trained ML model. Please verify before submitting."*
   - Citizens can review and manually override the category before final submission.

### B. Smart Priority Hazard Detection Engine (`priority_engine.py`)
Rather than relying on an unexplainable deep network, this engine uses a transparent, municipal safety scoring formula (1 to 100 points):

$$\text{Total Score} = \text{Category Risk} + \text{Safety Keywords} + \text{Evidence Attached} + \text{Description Detail} + \text{Community Upvotes}$$

- **1. Inherent Category Risk (10–35 pts):**
  - Traffic & Signage: 35 pts (immediate vehicle collisions)
  - Roads & Potholes: 30 pts (two-wheeler skid danger)
  - Water & Drainage: 28 pts (pipeline bursting, street flooding)
  - Street Lighting: 24 pts (dark zones, pedestrian vulnerability)
  - Garbage / Dustbins: 16–18 pts (sanitation health)
- **2. Safety Keyword Triggers (0–35 pts):**
  - *Critical (+30 pts):* `emergency`, `accident`, `sparking`, `exposed wire`, `collapsed`, `sinkhole`, `flooding`.
  - *High (+20 pts):* `hospital`, `school`, `children`, `main road`, `heavy traffic`, `burst pipe`, `open manhole`.
- **3. Visual Photo Attached (+10 pts):** Verified evidence prioritizes inspection.
- **4. Community Affirmation (+2 pts per upvote, max 10 pts):** Direct citizen democracy.

**Priority Tiers:**
- `Score >= 75`: **Critical Priority** (Red)
- `Score 55 - 74`: **High Priority** (Orange)
- `Score 35 - 54`: **Medium Priority** (Amber)
- `Score < 35`: **Low Priority** (Green)

### C. Spatial & Textual Duplicate Detection (`duplicate_detector.py`)
To prevent duplicate reports from cluttering municipal workflows:
1. **Haversine Geodesic Distance:**
   Calculates the exact distance in meters between the new complaint's coordinates and all active complaints:
   $$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
2. **Token Jaccard Similarity:**
   Computes word-token overlap between complaint descriptions:
   $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
3. **Composite Proximity Match:**
   If another complaint exists within **300 meters** and has a similarity score $> 0.35$, the UI displays an alert banner showing the existing ticket ID, distance, and a one-click button to upvote instead of filing a duplicate!

---

## 🌐 8. REST API Endpoint Documentation

All endpoints return standard HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `422 Unprocessable Entity`).

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Public | Serves the single-page application dashboard. |
| `GET` | `/api/health` | Public | Returns database connection status and server health. |
| `POST`| `/api/reports` | Public | Submits a new complaint (multipart form with image upload). |
| `GET` | `/api/reports` | Public | Lists complaints with pagination, category/status/priority filters, and text search. |
| `GET` | `/api/reports/{id}` | Public | Fetches detailed ticket data including full status timeline history. |
| `POST`| `/api/reports/{id}/upvote` | Public | Increments community upvotes and updates priority urgency. |
| `POST`| `/api/reports/ai-classify` | Public | Evaluates an uploaded photo and suggests a category. |
| `POST`| `/api/reports/check-duplicate`| Public | Checks spatial & textual duplicate candidates near coordinates. |
| `GET` | `/api/map/reports` | Public | Returns lightweight geo-points with priority colors for Leaflet. |
| `GET` | `/api/map/reverse-geocode` | Public | Translates latitude/longitude to street landmark. |
| `GET` | `/api/analytics` | Public | Computes real-time KPIs, category counts, and 7-day velocity trends. |
| `POST`| `/api/admin/login` | Public | Authenticates admin credentials and returns JWT Bearer token. |
| `GET` | `/api/admin/me` | Admin | Validates JWT token and returns admin profile. |
| `PATCH`| `/api/admin/reports/{id}/status`| Admin | Official status change with mandatory transition remarks. |
| `POST`| `/api/admin/reports/{id}/resolve-with-proof`| Admin | Marks ticket Resolved with official resolution photo proof. |
| `DELETE`| `/api/admin/reports/{id}`| Admin | Deletes spam or invalid complaints. |

Interactive OpenAPI documentation is live at `http://127.0.0.1:8000/docs`.

---

## 🚀 9. Installation & Execution Guide

### Prerequisites:
- Windows 10/11
- Python 3.10, 3.11, or 3.12 installed and added to your system `PATH`.
- Modern web browser (Chrome, Edge, Firefox).

---

### Option A: 1-Click Launch (Recommended for Windows)
Simply double-click the **`start.bat`** file in the project folder.  
It will automatically:
1. Verify Python installation.
2. Create the `.venv` virtual environment if needed.
3. Install all required dependencies from `requirements.txt`.
4. Create the local `.env` configuration.
5. Initialize the SQLite database and seed initial demo complaints.
6. Launch Uvicorn at `http://127.0.0.1:8000` and automatically open your default browser!

---

### Option B: Manual Command-Line Launch
Open PowerShell or Command Prompt in the project folder:

```powershell
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
.\.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment configuration
copy .env.example .env

# 5. Launch the application server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
- **Application Dashboard:** `http://127.0.0.1:8000`
- **Swagger API Documentation:** `http://127.0.0.1:8000/docs`

---

## ⚙️ 10. Environment Variable Setup (`.env`)

The application works 100% out of the box with default offline settings. If you wish to enable live Google Gemini Vision AI, edit the `.env` file:

```env
# Server
HOST=127.0.0.1
PORT=8000
DEBUG=True

# SQLite Database
DATABASE_URL=sqlite:///./civicpulse.db

# Administrator Default Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
JWT_SECRET_KEY=civicpulse-ai-secure-secret-key-change-in-production-2026

# Optional: Add your Google Gemini API Key for online vision classification
# Get a free key at https://aistudio.google.com/
GEMINI_API_KEY=

# Seed initial realistic demo records on fresh database
SEED_DEMO_DATA=True
```

---

## 🧪 11. Automated Testing Instructions

CivicPulse AI includes two independent test suites to prove system correctness:

### 1. Pytest API Integration Suite (11 Tests)
Run the automated Pytest suite:
```powershell
.\.venv\Scripts\pytest -v backend/tests/test_api.py
```
**Tests Verified:**
- `test_health_check`: Server health and DB connectivity.
- `test_list_reports`: Pagination, sorting, and filtering.
- `test_get_single_report`: Single report retrieval with status history.
- `test_get_nonexistent_report`: 404 error handling.
- `test_create_report_validation`: Input validation and bad request rejections.
- `test_create_report_success`: Real complaint submission and priority calculation.
- `test_upvote_report`: Community upvoting.
- `test_duplicate_detection`: Spatial proximity duplicate checks.
- `test_analytics_calculation`: Real-time SQLite statistics aggregation.
- `test_map_reports`: Leaflet marker data formatting and color badges.
- `test_admin_authentication_and_status_update`: Token authentication & secured status updates.

### 2. Comprehensive System Audit Script
Run the student audit script:
```powershell
.\.venv\Scripts\python test_system.py
```
This runs a 7-point audit across environment, database persistence, priority scoring, Haversine formula, PBKDF2 encryption, analytics, and FastAPI routes, printing a 100% verification score.

---

## 📸 12. Screenshots Section (Adding Actual Screenshots)

To prepare this project for your college submission report, capture screenshots of the running application and place them in an `assets/screenshots/` folder:

1. **Dashboard View:** Showing KPI cards, velocity charts, and recent complaints feed.
2. **Report Issue Form:** Showing photo upload with AI scanner beam and Leaflet location picker.
3. **Duplicate Detection Alert:** Showing the warning banner when picking a location near an existing report.
4. **Interactive GIS Map:** Showing colored priority pins on OpenStreetMap.
5. **Analytics Charts:** Showing category breakdown and 7-day intake trends.
6. **Detail Modal & Timeline:** Showing the resolution audit trail.
7. **Admin Management Console:** Showing authorized status transition dropdowns.

---

## 🎓 13. College Project Review & Viva Presentation Guide

When presenting CivicPulse AI to external examiners and faculty professors, follow this structured presentation strategy:

### 1. The 60-Second Elevator Pitch
> *"CivicPulse AI is an intelligent civic-tech platform that solves municipal reporting bottlenecks. Rather than treating complaint submission as a passive form, our system uses computer vision to recommend responsible departments, applies an explainable hazard scoring engine to elevate life-threatening problems to Critical priority, and uses spatial Haversine mathematics to prevent duplicate complaint backlogs. All actions are tracked on an auditable resolution timeline."*

### 2. Key Technical Talking Points
- **Why FastAPI over Flask or Django?**  
  FastAPI provides asynchronous concurrency, automatic OpenAPI Swagger documentation, and native Pydantic v2 data validation, resulting in faster execution and less boilerplate code.
- **Why Rule-Based Priority Scoring instead of ML Classifier?**  
  In municipal emergency triage, accountability is paramount. A machine learning model is often a black-box that cannot explain *why* it assigned a score. Our engine provides explicit, legally defensible justifications (e.g., *"+30 points for hospital proximity, +30 points for live wire hazard"*).
- **Why Leaflet over Google Maps?**  
  Leaflet is lightweight, open-source, and integrates seamlessly with OpenStreetMap tiles without requiring paid API credentials or credit cards, making it ideal for academic evaluation and open-source civic technology.

### 3. Demonstration Flow during Viva
1. **Open Dashboard (`/`):** Point out the live KPI metrics and the 7-day velocity chart calculated from the SQLite database.
2. **Submit a Complaint (`/report`):** Upload an image, click **Analyze with AI Vision**, show the category prediction and confidence meter. Pick a location on the Leaflet map and demonstrate auto-geocoding.
3. **Show Duplicate Alert:** Move the pin near the Connaught Circus demo pothole (lat: `28.6139`, lon: `77.2090`) to show how the system detects the nearby ticket within 300m and offers an upvote button.
4. **Open Admin Portal (`/admin`):** Log in using `admin` / `admin123`. Transition the status of a ticket to `In Progress` or `Resolved` with official remarks.
5. **Open Detail Modal:** Show the examiner the **Resolution Status Timeline** proving that every state change is logged with who changed it and when.

---

## 🔮 14. Known Limitations & Future Enhancements

### Limitations:
- **Offline Reverse Geocoding:** Reverse geocoding uses OpenStreetMap Nominatim which requires internet connectivity; when offline, it falls back to raw coordinate labels.
- **Single Admin Role:** The platform currently features a single municipal administrator role rather than hierarchical multi-departmental sub-roles.

### Future Roadmap:
- **Citizen WhatsApp/SMS Bot:** Integration with Twilio for submitting issues via messaging apps.
- **Automated Work-Order Routing:** Assigning tickets directly to field contractors based on GPS zones.
- **Drone Survey Integration:** Bulk automated road surface defect scanning using aerial drone imagery.

---

## 📄 License & Attribution
Developed for academic evaluation. Built using open-source technologies (FastAPI, Leaflet, OpenStreetMap, Chart.js, and SQLite).

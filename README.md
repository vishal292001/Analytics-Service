# Translytics Supply Chain Analytics Service

A FastAPI-based service for uploading and analyzing supply chain demand forecasts.

## Features

- CSV upload with comprehensive validation
- PostgreSQL database storage with optimized indexing
- Business logic for transportation surcharges
- Aggregated summary APIs
- Advanced regional analytics
- Clean architecture with separation of concerns
- Comprehensive error handling
- Docker support

## Project Structure

```
app/
├── main.py                      # FastAPI application entry point
├── db.py                        # Database configuration and connection
├── models.py                    # SQLAlchemy ORM models
├── routers.py                   # API route handlers
└── services/                    # Business logic services
    ├── validation_service.py    # Data validation service
    ├── file_upload_service.py   # Upload processing service
    ├── summary_service.py       # Data aggregation service
    └── analytics_service.py     # Analytics service
requirements.txt                 # Python dependencies
Dockerfile                       # Container configuration
docker-compose.yml               # Local development setup
```

## ⚙️ Environment Configuration

Environment configuration is stored in the `.env` file:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/hr_db
```

## 💻 Manual Setup Running Locally (No Docker)

### For Mac/Linux
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

### For Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

### Database Setup
```sql
CREATE DATABASE Analytics_DB;
```

### Configure Environment
```bash
export DATABASE_URL="postgresql+psycopg2://postgres:1234@localhost:5432/Analytics_DB"
```

### Run the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🐳 Running with Docker

```bash
docker compose up --build
```

- Access API at: [http://localhost:8000](http://localhost:8000)

---

## API Endpoints

### Upload Forecast Data
```
POST /api/upload-forecast
Content-Type: multipart/form-data
```
Upload CSV with columns: `sku`, `date`, `forecast_qty`, `unit_price`, `region`

### Get Summary
```
GET /api/summary?start_date=2023-01-01&end_date=2023-12-31&sku=SKU001&region=North
```
Returns aggregated data by SKU and region with business logic applied.

### Get Analytics
```
GET /api/analytics?start_date=2023-01-01&end_date=2023-12-31
```
Returns regional analytics including top SKUs, averages, and counts.

## Business Logic

- Transportation surcharge: **10%** added to forecast value when `forecast_qty > 500`
- Regional validation: Only `North`, `South`, `East`, `West` regions allowed
- Data validation: Comprehensive validation for all fields

## Production Deployment

The application includes:
- Proper error handling and logging
- Database connection pooling
- Health check endpoints
- Docker containerization
- Clean architecture principles
- Type hints throughout


## 🧑‍💻 Author

**Vishal Nitavne**  
Backend Developer | FastAPI | PostgreSQL | Kafka

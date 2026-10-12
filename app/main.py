from typing import List, Optional
from fastapi import Depends, HTTPException, status, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field
import logging
from datetime import date
from uuid import uuid4

import uuid
import time

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Time Tracker API")

from app.database import get_db


# --- Pydantic Models ---

class ActivationRequest(BaseModel):
    token: str


class TimeEntryItem(BaseModel):
    id: str
    projectId: str = Field(..., alias="projectId")
    projectName: str = Field(..., alias="projectName")
    clientName: Optional[str] = Field(None, alias="clientName")
    startTime: int = Field(..., alias="startTime")
    endTime: Optional[int] = Field(None, alias="endTime")
    duration: Optional[int] = 0
    userId: Optional[str] = Field(None, alias="userId")

    class Config:
        populate_by_name = True


class SyncPayload(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    entries: List[TimeEntryItem]

    class Config:
        populate_by_name = True

# --- Pydantic Model برای مرخصی ---
class AbsenceRequest(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    userId: str = Field(..., alias="userId")
    absenceType: str = Field(..., alias="absenceType")  # 'urlaub' یا 'krankheit'
    startDate: str = Field(..., alias="startDate")      # YYYY-MM-DD
    endDate: str = Field(..., alias="endDate")          # YYYY-MM-DD
    note: Optional[str] = None

    class Config:
        populate_by_name = True

# مدل‌های ورودی (Pydantic Models)
class ClientCreate(BaseModel):
    tenantSchema: str
    clientName: str
    description:Optional[str] = None

class ProjectCreate(BaseModel):
    tenantSchema: str
    clientId: Optional[int] = None
    clientName: str
    projectName: str
    budgetHours: Optional[float] = None


class ClientCreate(BaseModel):
    tenantSchema: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    taxId: Optional[str] = None

class ProjectCreate(BaseModel):
    tenantSchema: str
    clientId: str
    name: str
    description: Optional[str] = None


# --- تابع ساخت هوشمند جداول ۵‌گانه در شیمای شرکت ---

def ensure_tenant_tables(schema: str, db: Session):
    init_sql = text(f"""
        -- ۱. جدول کاربران شرکت
        CREATE TABLE IF NOT EXISTS {schema}.users (
            id VARCHAR(50) PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            full_name VARCHAR(255),
            role VARCHAR(50) DEFAULT 'employee',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- ۲. جدول پروژه‌ها
        CREATE TABLE IF NOT EXISTS {schema}.projects (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            client_name VARCHAR(255),
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- ۳. جدول کارکرد زمانی
        CREATE TABLE IF NOT EXISTS {schema}.time_entries (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50),
            project_id VARCHAR(50) NOT NULL,
            project_name VARCHAR(255) NOT NULL,
            client_name VARCHAR(255),
            start_time BIGINT NOT NULL,
            end_time BIGINT,
            duration INT DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- اطمینان از وجود ستون user_id در صورتی که جدول از قبل بدون این ستون ساخته شده باشد
        ALTER TABLE {schema}.time_entries ADD COLUMN IF NOT EXISTS user_id VARCHAR(50);

        -- ۴. جدول استراحت‌ها (مطابق قانون ArbZG آلمان)
        CREATE TABLE IF NOT EXISTS {schema}.breaks (
            id VARCHAR(50) PRIMARY KEY,
            time_entry_id VARCHAR(50) REFERENCES {schema}.time_entries(id) ON DELETE CASCADE,
            start_time BIGINT NOT NULL,
            end_time BIGINT,
            duration INT DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- ۵. جدول خلاصه کارکرد روزانه
        CREATE TABLE IF NOT EXISTS {schema}.daily_summaries (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            work_date DATE NOT NULL,
            total_work_minutes INT DEFAULT 0,
            total_break_minutes INT DEFAULT 0,
            is_approved BOOLEAN DEFAULT false,
            approved_by VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT unique_user_date_{schema.replace('.', '_')} UNIQUE (user_id, work_date)
        );

        -- ۶. جدول مرخصی‌ها و استعلاجی (Urlaub & Krankheit)
        CREATE TABLE IF NOT EXISTS {schema}.absences (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            absence_type VARCHAR(20) NOT NULL, -- 'urlaub' or 'krankheit'
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            note TEXT,
            is_approved BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );        
    """)
    db.execute(init_sql)
    db.commit()

def calculate_arbzg_compliance(total_work_minutes: int, registered_break_minutes: int):
    """
        Calculation of break times under the German ArbZG (Working Hours Act):
        - Work between 360 and 540 minutes (6 to 9 hours): minimum 30-minute break
        - Work exceeding 540 minutes (9 hours): minimum 45-minute break    

    """
    required_break = 0
    if total_work_minutes > 540: 
        required_break = 45
    elif total_work_minutes > 360:
        required_break = 30

    break_deduction = max(0, required_break - registered_break_minutes)
    effective_work_minutes = max(0, total_work_minutes - break_deduction)

    exceeds_max_limit = effective_work_minutes > 600

    return {
        "required_break": required_break,
        "applied_break_deduction": break_deduction,
        "effective_work_minutes": effective_work_minutes,
        "is_violation": exceeds_max_limit
    }

# --- Endpoints ---

@app.post("/auth/activate")
def activate_device(payload: ActivationRequest, db: Session = Depends(get_db)):
    token_str = payload.token

    token_query = text("""
        SELECT company_user_id, used_at 
        FROM timetracker.activation_tokens 
        WHERE token = :token
    """)
    token_row = db.execute(token_query, {"token": token_str}).fetchone()

    if not token_row:
        raise HTTPException(status_code=400, detail="Invalid token")
    if token_row.used_at is not None:
        raise HTTPException(status_code=400, detail="Token already used")

    company_user_id = token_row.company_user_id

    company_query = text("""
        SELECT c.id, c.name, cu.role 
        FROM timetracker.companies c
        JOIN timetracker.company_users cu ON cu.company_id = c.id
        WHERE cu.id = :cu_id
    """)
    company_row = db.execute(company_query, {"cu_id": company_user_id}).fetchone()

    if not company_row:
        raise HTTPException(status_code=400, detail="Company user not found")

    company_id, company_name, user_role = company_row
    schema_name = f"tenant_{str(company_id).replace('-', '_')}"

    # اطمینان از وجود ۵ جدول پایه هنگام فعال‌سازی دستگاه
    ensure_tenant_tables(schema_name, db)

    projects_query = text(f"SELECT id, name FROM {schema_name}.projects WHERE is_active = true")
    projects_rows = db.execute(projects_query).fetchall()
    
    projects_list = [{"id": str(r.id), "name": r.name} for r in projects_rows]

    db.execute(
        text("UPDATE timetracker.activation_tokens SET used_at = NOW() WHERE token = :token"),
        {"token": token_str}
    )
    db.commit()

    fake_auth_token = f"Bearer_secret_token_for_{company_user_id}"

    return {
        "clientName": company_name,
        "tenantSchema": schema_name,
        "authToken": fake_auth_token,
        "role": user_role or "employee",
        "projects": projects_list
    }


@app.post("/time-entries/sync")
def sync_time_entries(payload: SyncPayload, db: Session = Depends(get_db)):
    schema = payload.tenantSchema

    try:
        # ۱. اطمینان از وجود جداول در دیتابیس
        ensure_tenant_tables(schema, db)

        # ۲. کوئری ذخیره با نگاشت صریح متغیرهای CamelCase به ستون‌های snake_case
        insert_sql = text(f"""
            INSERT INTO {schema}.time_entries 
            (id, user_id, project_id, project_name, client_name, start_time, end_time, duration)
            VALUES (:id, :user_id, :project_id, :project_name, :client_name, :start_time, :end_time, :duration)
            ON CONFLICT (id) DO UPDATE 
            SET end_time = EXCLUDED.end_time, 
                duration = EXCLUDED.duration,
                project_name = EXCLUDED.project_name;
        """)

        for entry in payload.entries:
            db.execute(insert_sql, {
                "id": entry.id,
                "user_id": entry.userId,
                "project_id": entry.projectId,
                "project_name": entry.projectName,
                "client_name": entry.clientName,
                "start_time": entry.startTime,
                "end_time": entry.endTime,
                "duration": entry.duration or 0
            })

        db.commit()
        return {"status": "success", "synced_count": len(payload.entries)}

    except Exception as e:
        db.rollback()
        logger.error(f"Sync failed for schema {schema}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync entries: {str(e)}"
        )


@app.get("/compliance/daily-summary")
def get_daily_compliance_summary(
    tenantSchema: str, 
    user_id: str, 
    target_date: str, 
    db: Session = Depends(get_db)
):
    """
    ارزیابی مجموع کارکرد روزانه کاربر مطابق با قانون ArbZG
    """
    try:
        query = text(f"""
            SELECT 
                COALESCE(SUM(duration), 0) as total_work,
                COALESCE(SUM(total_break_duration), 0) as total_break
            FROM {tenantSchema}.time_entries
            WHERE user_id = :user_id 
              AND DATE(TO_TIMESTAMP(start_time / 1000)) = :target_date
        """)
        
        row = db.execute(query, {"user_id": user_id, "target_date": target_date}).fetchone()
        
        total_work = row.total_work if row else 0
        total_break = row.total_break if row else 0

        compliance = calculate_arbzg_compliance(total_work, total_break)

        return {
            "date": target_date,
            "registered_work_minutes": total_work,
            "registered_break_minutes": total_break,
            "required_break_minutes": compliance["required_break"],
            "auto_deducted_break_minutes": compliance["applied_break_deduction"],
            "effective_work_minutes": compliance["effective_work_minutes"],
            "exceeds_10h_limit": compliance["is_violation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")    


# --- Endpoints مرخصی و بیماری ---

@app.post("/absences/request")
def request_absence(payload: AbsenceRequest, db: Session = Depends(get_db)):
    schema = payload.tenantSchema
    absence_id = f"abs_{uuid4().hex[:12]}"
    
    try:
        ensure_tenant_tables(schema, db)
        
        sql = text(f"""
            INSERT INTO {schema}.absences 
            (id, user_id, absence_type, start_date, end_date, note)
            VALUES (:id, :user_id, :type, :start_date, :end_date, :note)
        """)
        
        db.execute(sql, {
            "id": absence_id,
            "user_id": payload.userId,
            "type": payload.absenceType,
            "start_date": payload.startDate,
            "end_date": payload.endDate,
            "note": payload.note
        })
        db.commit()
        
        return {"status": "success", "absence_id": absence_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record absence: {str(e)}")


@app.get("/absences/list")
def get_user_absences(tenantSchema: str, user_id: str, db: Session = Depends(get_db)):
    try:
        sql = text(f"""
            SELECT id, absence_type, start_date, end_date, note, is_approved
            FROM {tenantSchema}.absences
            WHERE user_id = :user_id
            ORDER BY start_date DESC
        """)
        
        rows = db.execute(sql, {"user_id": user_id}).fetchall()
        
        result = []
        for r in rows:
            result.append({
                "id": r.id,
                "absenceType": r.absence_type,
                "startDate": str(r.start_date),
                "endDate": str(r.end_date),
                "note": r.note,
                "isApproved": r.is_approved
            })
            
        return {"absences": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch absences: {str(e)}")


@app.get("/admin/monthly-report")
def get_monthly_audit_report(
    tenantSchema: str, 
    year: int, 
    month: int, 
    db: Session = Depends(get_db)
):
    try:
        # استفاده از ستون‌های واقعی موجود در جدول شما (duration به جای total_break_duration)
        query_entries = text(f"""
            SELECT 
                user_id,
                client_name,
                project_name,
                duration,
                start_time
            FROM {tenantSchema}.time_entries
            WHERE EXTRACT(YEAR FROM TIMESTAMP 'epoch' + start_time * INTERVAL '1 millisecond') = :year
              AND EXTRACT(MONTH FROM TIMESTAMP 'epoch' + start_time * INTERVAL '1 millisecond') = :month
        """)
        
        entries = db.execute(query_entries, {"year": year, "month": month}).fetchall()
        
        query_absences = text(f"""
            SELECT 
                user_id,
                absence_type,
                start_date,
                end_date,
                is_approved
            FROM {tenantSchema}.absences
            WHERE (EXTRACT(YEAR FROM start_date) = :year AND EXTRACT(MONTH FROM start_date) = :month)
               OR (EXTRACT(YEAR FROM end_date) = :year AND EXTRACT(MONTH FROM end_date) = :month)
        """)
        
        absences = db.execute(query_absences, {"year": year, "month": month}).fetchall()
        
        return {
            "year": year,
            "month": month,
            "totalEntriesCount": len(entries),
            "absencesCount": len(absences),
            "entries": [
                {
                    "userId": e.user_id,
                    "clientName": e.client_name,
                    "projectName": e.project_name,
                    "durationMinutes": e.duration,
                    "breakMinutes": 0,
                    "startTime": str(e.start_time)
                } for e in entries
            ],
            "absences": [
                {
                    "userId": a.user_id if hasattr(a, 'user_id') else 'usr_default',
                    "absenceType": a.absence_type,
                    "startDate": str(a.start_date),
                    "endDate": str(a.end_date),
                    "isApproved": a.is_approved
                } for a in absences
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate monthly report: {str(e)}")


@app.get("/projects/list")
def get_clients_and_projects(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        # اطمینان از وجود جداول پایه
        db.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {tenantSchema}.clients (
                id UUID PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(50),
                address TEXT,
                tax_id VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS {tenantSchema}.projects (
                id UUID PRIMARY KEY,
                company_id UUID,
                client_id UUID REFERENCES {tenantSchema}.clients(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        db.commit()

        # خواندن مشتریان به همراه پروژه‌های مرتبط
        clients_query = text(f"SELECT id, name, email, phone, address, tax_id FROM {tenantSchema}.clients ORDER BY name")
        clients_result = db.execute(clients_query).fetchall()

        clients_data = []
        for c in clients_result:
            proj_query = text(f"SELECT id, name, description, is_active FROM {tenantSchema}.projects WHERE client_id = :client_id ORDER BY name")
            projects_result = db.execute(proj_query, {"client_id": c.id}).fetchall()
            
            projects_list = [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "isActive": p.isActive if hasattr(p, 'isActive') else p.is_active
                } for p in projects_result
            ]
            
            clients_data.append({
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "address": c.address,
                "taxId": c.tax_id,
                "projects": projects_list
            })

        return {"clients": clients_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")

@app.post("/clients/create")
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    try:
        client_id = str(uuid.uuid4())
        query = text(f"""
            INSERT INTO {data.tenantSchema}.clients (id, name, email, phone, address, tax_id)
            VALUES (:id, :name, :email, :phone, :address, :tax_id)
        """)
        db.execute(query, {
            "id": client_id,
            "name": data.name.strip(),
            "email": data.email,
            "phone": data.phone,
            "address": data.address,
            "tax_id": data.taxId
        })
        db.commit()
        return {"status": "success", "clientId": client_id, "message": "Client created successfully"}
    except Exception as e:
        db.rollback()
        print("DATABASE ERROR:", str(e))  # این خط را برای چاپ در ترمینال اضافه کنید
        raise HTTPException(status_code=500, detail=f"Failed to create client: {str(e)}")

@app.post("/projects/create")
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    try:
        project_id = str(uuid.uuid4())
        query = text(f"""
            INSERT INTO {data.tenantSchema}.projects (id, client_id, name, description)
            VALUES (:id, :client_id, :name, :description)
        """)
        db.execute(query, {
            "id": project_id,
            "client_id": data.clientId,
            "name": data.name.strip(),
            "description": data.description
        })
        db.commit()
        return {"status": "success", "projectId": project_id, "message": "Project created successfully"}
    except Exception as e:
        db.rollback()
        print("PROJECT DATABASE ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")
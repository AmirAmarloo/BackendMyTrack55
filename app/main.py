from typing import List, Optional
from fastapi import Depends, HTTPException, status, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import UUID, text
from pydantic import BaseModel, Field
import logging
from uuid import uuid4
import uuid
from fastapi import APIRouter, HTTPException, Query
import psycopg2
from uuid import UUID
from passlib.context import CryptContext
from pydantic import BaseModel
import bcrypt
from pydantic import BaseModel
from typing import List, Optional
import io
import csv
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   

router = APIRouter()

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Time Tracker API")

from app.database import get_db


# --- Pydantic Models ---

class ActivationRequest(BaseModel):
    token: str

class BreakItem(BaseModel):
    id: str
    startTime: int = Field(..., alias="startTime")
    endTime: Optional[int] = Field(None, alias="endTime")
    duration: Optional[int] = 0

    class Config:
        populate_by_name = True

class TimeEntryItem(BaseModel):
    id: str
    projectId: str = Field(..., alias="projectId")
    projectName: str = Field(..., alias="projectName")
    clientName: Optional[str] = Field(None, alias="clientName")
    startTime: int = Field(..., alias="startTime")
    endTime: Optional[int] = Field(None, alias="endTime")
    duration: Optional[int] = 0
    userId: Optional[str] = Field(None, alias="userId")
    breaks: Optional[List[BreakItem]] = []

    class Config:
        populate_by_name = True


class SyncPayload(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    entries: List[TimeEntryItem]

    class Config:
        populate_by_name = True


class AbsenceRequest(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    userId: str = Field(..., alias="userId")
    absenceType: str = Field(..., alias="absenceType")
    startDate: str = Field(..., alias="startDate")
    endDate: str = Field(..., alias="endDate")
    note: Optional[str] = None

    class Config:
        populate_by_name = True


class ClientCreate(BaseModel):
    tenantSchema: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    taxId: Optional[str] = None


class ProjectCreate(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    companyId: Optional[str] = Field(None, alias="companyId")
    clientId: str = Field(..., alias="clientId")
    name: str = Field(..., alias="name")
    description: Optional[str] = Field(None, alias="description")

    class Config:
        populate_by_name = True
        extra = "ignore"


class ManualEntryRequest(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    userId: str = Field(..., alias="userId")
    projectId: str = Field(..., alias="projectId")
    projectName: str = Field(..., alias="projectName")
    clientName: Optional[str] = Field(None, alias="clientName")
    startTime: int = Field(..., alias="startTime")
    endTime: int = Field(..., alias="endTime")
    duration: int = Field(..., alias="duration")
    note: str = Field(..., alias="note") # علت فراموشی یا ثبت دستی
    isAdminAction: Optional[bool] = Field(False, alias="isAdminAction")

    class Config:
        populate_by_name = True



class ManualEntryRequest(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    userId: str = Field(..., alias="userId")
    projectId: str = Field(..., alias="projectId")
    projectName: str = Field(..., alias="projectName")
    clientName: Optional[str] = Field(None, alias="clientName")
    startTime: int = Field(..., alias="startTime")
    endTime: int = Field(..., alias="endTime")
    duration: int = Field(..., alias="duration")
    note: str = Field(..., alias="note")
    isAdminAction: Optional[bool] = Field(False, alias="isAdminAction")
    totalBreakDuration: Optional[int] = 0 
    breaks: Optional[List[BreakItem]] = []

    class Config:
        populate_by_name = True        

class CreateUserRequest(BaseModel):
    tenantSchema: str
    fullName: str
    email: str
    role: str = "employee"  # 'admin' یا 'employee'
    includeInReports: bool = True

class AssignProjectRequest(BaseModel):
    tenantSchema: str
    userId: str
    projectId: str

class CompanyRegistrationRequest(BaseModel):
    companyName: str = Field(..., alias="companyName")
    adminName: str = Field(..., alias="adminName")
    adminEmail: str = Field(..., alias="adminEmail")

    class Config:
        populate_by_name = True

class LoginPayload(BaseModel):
    email: str
    password: str

class ActivationPayload(BaseModel):
    token: str
    email: str
    password: str

    class Config:
        populate_by_name = True    


class ReportStatusPayload(BaseModel):
    includeInReports: bool
    tenantSchema: str

class TimeEntrySyncItem(BaseModel):
    id: str
    projectId: str
    projectName: str
    clientName: Optional[str] = ""
    startTime: int
    endTime: Optional[int] = None
    duration: int
    note: Optional[str] = ""

class SyncPayload(BaseModel):
    tenantSchema: str
    userId: str
    entries: List[TimeEntrySyncItem]

class BreakItem(BaseModel):
    id: Optional[str] = None
    startTime: int
    endTime: Optional[int] = None
    duration: Optional[int] = 0

# به‌روزرسانی مدل ورودی برای ثبت دستی یا سنکرون
class TimeEntryPayloadItem(BaseModel):
    id: str
    projectId: str
    projectName: str
    clientName: Optional[str] = ""
    startTime: int
    endTime: Optional[int] = None
    duration: int
    note: Optional[str] = ""
    breaks: Optional[List[BreakItem]] = []
    totalBreakDuration: Optional[int] = 0

class ProjectUpdateRequest(BaseModel):
    tenantSchema: str
    projectId: str
    name: str
    description: Optional[str] = None
    isActive: bool

class AbsenceApprovalRequest(BaseModel):
    tenantSchema: str
    absenceId: str
    status: str  # 'approved' یا 'rejected'

# ---------------------------- Database Tables Setup -------------------------------

def ensure_tenant_tables(schema_name: str, db: Session):
    db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name};"))
    
    init_sql = text(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.users (
            id VARCHAR(50) PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            password_hash VARCHAR(255),
            full_name VARCHAR(255),
            role VARCHAR(50) DEFAULT 'employee',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            include_in_reports BOOLEAN DEFAULT TRUE
        );

        CREATE TABLE IF NOT EXISTS {schema_name}.clients (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            address TEXT,
            tax_id VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS {schema_name}.projects (
            id UUID PRIMARY KEY,
            company_id UUID NOT NULL,
            client_id UUID REFERENCES {schema_name}.clients(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS {schema_name}.time_entries (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50),
            project_id UUID NOT NULL,
            project_name VARCHAR(255) NOT NULL,
            note VARCHAR(255) NOT NULL,
            client_name VARCHAR(255),
            is_manual BOOLEAN DEFAULT false,
            start_time BIGINT NOT NULL,
            end_time BIGINT,
            approval_status VARCHAR(20) DEFAULT 'approved',
            duration INT DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS {schema_name}.breaks (
            id VARCHAR(50) PRIMARY KEY,
            time_entry_id VARCHAR(50) REFERENCES {schema_name}.time_entries(id) ON DELETE CASCADE,
            start_time BIGINT NOT NULL,
            end_time BIGINT,
            duration INT DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS {schema_name}.daily_summaries (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            work_date DATE NOT NULL,
            total_work_minutes INT DEFAULT 0,
            total_break_minutes INT DEFAULT 0,
            is_approved BOOLEAN DEFAULT false,
            approved_by VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT unique_user_date_{schema_name.replace('-', '_')} UNIQUE (user_id, work_date)
        );

        CREATE TABLE IF NOT EXISTS {schema_name}.absences (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            absence_type VARCHAR(20) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            note TEXT,
            is_approved BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS {schema_name}.user_projects (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            project_id VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, project_id)
        );        

        CREATE TABLE IF NOT EXISTS {schema_name}.audit_logs (
            id VARCHAR(36) PRIMARY KEY,
            admin_id VARCHAR(36),
            action_type VARCHAR(100) NOT NULL,
            target_type VARCHAR(100),
            target_id VARCHAR(36),
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        ALTER TABLE timetracker.users 
        ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,
        ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

        ALTER TABLE {schema_name}.users 
        ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,
        ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

    """)
    db.execute(init_sql)
    db.commit()

def calculate_arbzg_compliance(total_work_minutes: int, registered_break_minutes: int):
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


def log_audit_event(db: Session, schema: str, admin_id: str, action_type: str, target_type: str, target_id: str, details: str):
    try:
        log_id = str(uuid.uuid4())
        sql = text(f"""
            INSERT INTO {schema}.audit_logs (id, admin_id, action_type, target_type, target_id, details, created_at)
            VALUES (:id, :admin_id, :action_type, :target_type, :target_id, :details, NOW())
        """)
        db.execute(sql, {
            "id": log_id,
            "admin_id": admin_id or "system_admin",
            "action_type": action_type,
            "target_type": target_type,
            "target_id": target_id,
            "details": details
        })
        db.commit()
    except Exception as e:
        print("🔴 ERROR IN AUDIT LOG:", str(e))


def validate_arbzg_rules(duration_minutes: int, break_minutes: int = 0):
    """
    بررسی قوانین کار و استراحت آلمان (ArbZG)
    duration_minutes: زمان خالص کارکرد
    break_minutes: مجموع زمان استراحت ثبت شده
    """
    net_hours = duration_minutes / 60
    total_span_minutes = duration_minutes + break_minutes
    total_span_hours = total_span_minutes / 60

    # ۱. سقف ساعت کاری روزانه (حداکثر ۱۰ ساعت)
    if net_hours > 10:
        raise HTTPException(
            status_code=400,
            detail="ArbZG Violation: Daily net working hours cannot exceed 10 hours."
        )

    # ۲. قوانین استراحت اجباری بر اساس کل زمان حضور (Span)
    if total_span_hours > 6 and total_span_hours <= 9:
        if break_minutes < 30:
            raise HTTPException(
                status_code=400,
                detail="ArbZG Compliance Error: Working over 6 hours requires at least 30 minutes of break."
            )
    elif total_span_hours > 9:
        if break_minutes < 45:
            raise HTTPException(
                status_code=400,
                detail="ArbZG Compliance Error: Working over 9 hours requires at least 45 minutes of break."
            )

def calculate_break_minutes(breaks: List[BreakItem], total_break_duration: Optional[int] = 0) -> int:
    if total_break_duration and total_break_duration > 0:
        return total_break_duration
    
    if not breaks:
        return 0
        
    total_mins = 0
    for b in breaks:
        if b.duration and b.duration > 0:
            total_mins += b.duration
        elif b.endTime and b.startTime:
            # محاسبه تفاوت زمانی بر حسب دقیقه
            diff_mins = round((b.endTime - b.startTime) / (1000 * 60))
            total_mins += max(1, diff_mins)
            
    return total_mins

# -------- Endpoints ----------
#------------------------------

@app.post("/auth/activate", response_model=None)
def activate_token(payload: ActivationPayload, db: Session = Depends(get_db)):
    try:
        # ۱. اصلاح کوئری برای استخراج صحیحِ user_id اصلی (cu.user_id به جای t.company_user_id)
        token_row = db.execute(text("""
            SELECT cu.user_id, cu.company_id 
            FROM timetracker.activation_tokens t
            JOIN timetracker.company_users cu ON t.company_user_id = cu.id
            JOIN timetracker.companies c ON cu.company_id = c.id
            WHERE t.token = :token AND t.expires_at > NOW() AND t.used_at IS NULL
        """), {"token": payload.token}).fetchone()

        if not token_row:
            raise HTTPException(status_code=400, detail="Invalid or expired activation token.")

        user_id = token_row[0]  # این حالا دقیقاً شناسه‌ی واقعی کاربر در جدول users است
        comp_id = token_row[1]
        
        schema_name = f"tenant_{str(comp_id).replace('-', '_')}"

        # هش کردن پسورد با bcrypt
        password_hash = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # ۲. به‌روزرسانی جدول مرکزی users با شناسه صحیح
        db.execute(text("""
            UPDATE timetracker.users 
            SET email = :email, password_hash = :password_hash 
            WHERE id = :user_id
        """), {"email": payload.email, "password_hash": password_hash, "user_id": str(user_id)})

        # ۳. به‌روزرسانی جدول اسکیمای اختصاصی شرکت
        db.execute(text(f"""
            UPDATE {schema_name}.users 
            SET email = :email, password_hash = :password_hash 
            WHERE id = :user_id
        """), {"email": payload.email, "password_hash": password_hash, "user_id": str(user_id)})

        # ۴. علامت‌زدن توکن به عنوان استفاده‌شده
        db.execute(text("""
            UPDATE timetracker.activation_tokens 
            SET used_at = NOW() 
            WHERE token = :token
        """), {"token": payload.token})

        db.commit()
        return {"status": "success", "message": "Account activated successfully. You can now log in."}

    except Exception as e:
        db.rollback()
        print(f"ERROR IN activate_token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
            
@app.post("/time-entries/sync")
def sync_time_entries(payload: SyncPayload, db: Session = Depends(get_db)):
    schema = payload.tenantSchema

    try:
        ensure_tenant_tables(schema, db)

        insert_entry_sql = text(f"""
            INSERT INTO {schema}.time_entries 
            (id, user_id, project_id, project_name, client_name, start_time, end_time, duration, note, synced_at)
            VALUES (:id, :user_id, :project_id, :project_name, :client_name, :start_time, :end_time, :duration, :note, NOW())
            ON CONFLICT (id) DO UPDATE 
            SET end_time = EXCLUDED.end_time, 
                duration = EXCLUDED.duration,
                project_name = EXCLUDED.project_name,
                note = EXCLUDED.note,
                synced_at = NOW();
        """)

        insert_break_sql = text(f"""
            INSERT INTO {schema}.breaks 
            (id, time_entry_id, start_time, end_time, duration)
            VALUES (:id, :time_entry_id, :start_time, :end_time, :duration)
            ON CONFLICT (id) DO UPDATE 
            SET end_time = EXCLUDED.end_time, 
                duration = EXCLUDED.duration;
        """)

        for entry in payload.entries:
            # ۱. اعتبارسنجی UUID پروژه
            try:
                uuid_obj = uuid.UUID(entry.projectId)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid project ID format: '{entry.projectId}'. Project ID must be a valid UUID."
                )

            project_exists = db.execute(
                text(f"SELECT 1 FROM {schema}.projects WHERE id = :project_id"),
                {"project_id": str(uuid_obj)}
            ).fetchone()

            if not project_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Project with ID '{entry.projectId}' does not exist in tenant schema."
                )

            # ۲. محاسبه استراحت و اعتبارسنجی قوانین ArbZG برای هر رکورد
            break_mins = calculate_break_minutes(entry.breaks, entry.totalBreakDuration)
            validate_arbzg_rules(entry.duration, break_mins)

            # ۳. درج یا آپدیت تایم‌انری در دیتابیس
            db.execute(insert_entry_sql, {
                "id": entry.id,
                "user_id": payload.userId,
                "project_id": entry.projectId,
                "project_name": entry.projectName,
                "client_name": entry.clientName or "",
                "start_time": entry.startTime,
                "end_time": entry.endTime,
                "duration": entry.duration,
                "note": entry.note or ""
            })

            # ۴. درج یا آپدیت بازه‌های استراحت مربوط به این رکورد (در صورت وجود)
            if entry.breaks:
                for b in entry.breaks:
                    b_id = b.id or str(uuid.uuid4())
                    b_duration = b.duration or (round((b.endTime - b.startTime) / (1000 * 60)) if b.endTime else 0)
                    db.execute(insert_break_sql, {
                        "id": b_id,
                        "time_entry_id": entry.id,
                        "start_time": b.startTime,
                        "end_time": b.endTime,
                        "duration": b_duration
                    })

        db.commit()
        return {"status": "success", "message": "All entries synced successfully."}

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        print("ERROR IN SYNC:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/projects/list")
def get_clients_and_projects(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        ensure_tenant_tables(tenantSchema, db)

        clients_query = text(f"SELECT id, name, email, phone, address, tax_id FROM {tenantSchema}.clients ORDER BY name")
        clients_result = db.execute(clients_query).fetchall()

        clients_data = []
        for c in clients_result:
            proj_query = text(f"SELECT id, name, description, is_active FROM {tenantSchema}.projects WHERE client_id = :client_id ORDER BY name")
            projects_result = db.execute(proj_query, {"client_id": c.id}).fetchall()
            
            projects_list = []
            for p in projects_result:
                duration_query = text(f"""
                    SELECT COALESCE(SUM(duration), 0) as total 
                    FROM {tenantSchema}.time_entries 
                    WHERE project_id = :project_id
                """)
                duration_res = db.execute(duration_query, {"project_id": p.id}).fetchone()
                total_minutes = duration_res.total if duration_res else 0

                projects_list.append({
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "isActive": p.is_active,
                    "totalMinutes": total_minutes
                })
            
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
        raise HTTPException(status_code=500, detail=f"Failed to create client: {str(e)}")


@app.post("/projects/create")
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    try:
        project_id = str(uuid.uuid4())
        company_id = data.tenantSchema.replace("tenant_", "").replace("_", "-")
        query = text(f"""
            INSERT INTO {data.tenantSchema}.projects (id, company_id, client_id, name, description)
            VALUES (:id, :company_id, :client_id, :name, :description)
        """)
        db.execute(query, {
            "id": project_id,
            "company_id": company_id,
            "client_id": data.clientId,
            "name": data.name.strip(),
            "description": data.description
        })
        db.commit()
        return {"status": "success", "projectId": project_id, "message": "Project created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@app.get("/compliance/daily-summary")
def get_daily_compliance_summary(tenantSchema: str, user_id: str, target_date: str, db: Session = Depends(get_db)):
    try:
        query = text(f"""
            SELECT 
                COALESCE(SUM(duration), 0) as total_work,
                0 as total_break
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


@app.post("/absences/request")
def request_absence(payload: AbsenceRequest, db: Session = Depends(get_db)):
    schema = payload.tenantSchema
    absence_id = f"abs_{uuid4().hex[:12]}"
    try:
        ensure_tenant_tables(schema, db)
        sql = text(f"""
            INSERT INTO {schema}.absences (id, user_id, absence_type, start_date, end_date, note)
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
            FROM {tenantSchema}.absences WHERE user_id = :user_id ORDER BY start_date DESC
        """)
        rows = db.execute(sql, {"user_id": user_id}).fetchall()
        result = [{
            "id": r.id,
            "absenceType": r.absence_type,
            "startDate": str(r.start_date),
            "endDate": str(r.end_date),
            "note": r.note,
            "isApproved": r.is_approved
        } for r in rows]
        return {"absences": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch absences: {str(e)}")


@app.get("/admin/monthly-report")
def get_monthly_audit_report(tenantSchema: str, year: int, month: int, db: Session = Depends(get_db)):
    try:
        # دریافت تمام رکوردهای ماه همراه با وضعیت تایید
        query_entries = text(f"""
            SELECT e.user_id, e.client_name, e.project_name, e.duration, e.start_time, e.approval_status, COALESCE(u.include_in_reports, TRUE) as include_in_reports
            FROM {tenantSchema}.time_entries e
            LEFT JOIN {tenantSchema}.users u ON e.user_id::text = u.id::text
            WHERE EXTRACT(YEAR FROM TIMESTAMP 'epoch' + e.start_time * INTERVAL '1 millisecond') = :year
              AND EXTRACT(MONTH FROM TIMESTAMP 'epoch' + e.start_time * INTERVAL '1 millisecond') = :month
              --AND COALESCE(u.include_in_reports, TRUE) = TRUE
        """)        
        entries = db.execute(query_entries, {"year": year, "month": month}).fetchall()
        
        query_absences = text(f"""
            SELECT user_id, absence_type, start_date, end_date, is_approved
            FROM {tenantSchema}.absences
            WHERE (EXTRACT(YEAR FROM start_date) = :year AND EXTRACT(MONTH FROM start_date) = :month)
               OR (EXTRACT(YEAR FROM end_date) = :year AND EXTRACT(MONTH FROM end_date) = :month)
        """)
        absences = db.execute(query_absences, {"year": year, "month": month}).fetchall()
        
        formatted_entries = [{
            "userId": e.user_id,
            "clientName": e.client_name,
            "projectName": e.project_name,
            "durationMinutes": e.duration,
            "breakMinutes": 0,
            "startTime": str(e.start_time),
            "approvalStatus": e.approval_status or "pending",
            "includeInReports": bool(e.include_in_reports)
        } for e in entries]

        return {
            "year": year,
            "month": month,
            "totalEntriesCount": len(entries),
            "absencesCount": len(absences),
            "entries": formatted_entries,
            "absences": [{
                "userId": a.user_id if hasattr(a, 'user_id') else 'usr_default',
                "absenceType": a.absence_type,
                "startDate": str(a.start_date),
                "endDate": str(a.end_date),
                "isApproved": a.is_approved
            } for a in absences]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate monthly report: {str(e)}")



@app.post("/time-entries/manual")
def create_manual_entry(payload: ManualEntryRequest, db: Session = Depends(get_db)):
    schema = payload.tenantSchema


    
    # استفاده از uuid4 واقعی به جای رشته متنی
    entry_id = str(uuid.uuid4())
    
    approval_status = 'approved' if payload.isAdminAction else 'pending'

    
    try:
        ensure_tenant_tables(schema, db)
        
        # ۱. ابتدا محاسبه استراحت و اعتبارسنجی قوانین ArbZG
        break_mins = calculate_break_minutes(payload.breaks, payload.totalBreakDuration)
        validate_arbzg_rules(payload.duration, break_mins)
        print(f"🔹 Inserting manual entry: {entry_id} for user {payload.userId} in schema {schema}")
        print(f"🔹 Start Time: {payload.startTime}, End Time: {payload.endTime}, Duration: {payload.duration}, Break Minutes: {break_mins}")
        print(f"🔹 Approval Status: {approval_status}, Project: {payload.projectName}, Client: {payload.clientName}")

        # ۲. درج تایم انری در دیتابیس
        sql = text(f"""
            INSERT INTO {schema}.time_entries 
            (id, user_id, project_id, project_name, client_name, start_time, end_time, duration, is_manual, approval_status, synced_at)
            VALUES (:id, :user_id, :project_id, :project_name, :client_name, :start_time, :end_time, :duration, TRUE, :approval_status, NOW())
        """)
        print(f"DEBUG ---> SQL Query: {sql}")
        
        db.execute(sql, {
            "id": entry_id,
            "user_id": payload.userId,
            "project_id": payload.projectId,
            "project_name": payload.projectName,
            "client_name": payload.clientName,
            "start_time": payload.startTime,
            "end_time": payload.endTime,
            "duration": payload.duration,
            "approval_status": approval_status
        })

        # ۳. درج بازه‌های استراحت (در صورت وجود) در جدول breaks
        if payload.breaks:
            insert_break_sql = text(f"""
                INSERT INTO {schema}.breaks 
                (id, time_entry_id, start_time, end_time, duration)
                VALUES (:id, :time_entry_id, :start_time, :end_time, :duration)
                ON CONFLICT (id) DO NOTHING
            """)
            for b in payload.breaks:
                b_id = b.id or str(uuid.uuid4())
                b_duration = b.duration or (round((b.endTime - b.startTime) / (1000 * 60)) if b.endTime else 0)
                db.execute(insert_break_sql, {
                    "id": b_id,
                    "time_entry_id": entry_id,
                    "start_time": b.startTime,
                    "end_time": b.endTime,
                    "duration": b_duration
                })

        db.commit()
        return {"status": "success", "entryId": entry_id, "message": "Manual entry processed successfully."}
        
    except HTTPException as he:
        # 👈 مهم: خطای 400 مربوط به قوانین ArbZG بدون دستکاری به فرانت‌اند می‌رسد
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        print("🔴 ERROR IN MANUAL ENTRY:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
# 2. لیست کاربران شرکت (برای اینکه ادمین بدد برای چه کسی دارد ساعت ثبت می‌کند)
@app.get("/admin/users-list")
def get_tenant_users(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        query = text(f"""
            SELECT id, display_name, email, role, COALESCE(include_in_reports, TRUE) as include_in_reports 
            FROM {tenantSchema}.users
        """)
        users = db.execute(query).fetchall()
        return [
            {
                "id": u.id,
                "displayName": u.display_name,
                "email": u.email,
                "role": u.role,
                "includeInReports": bool(u.include_in_reports)
            } for u in users
        ]
    except Exception as e:
        print("ERROR IN users-list:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/time-entries/pending")
def get_pending_entries(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        sql = text(f"""
            SELECT 
                ti.id, 
                user_id, 
                project_id, 
                project_name, 
                client_name, 
                start_time, 
                end_time, 
                duration, 
                ti.created_at, 
                is_manual, 
                approval_status,
                u.full_name AS user_name
            FROM {tenantSchema}.time_entries ti
            JOIN {tenantSchema}.users u ON ti.user_id = u.id
            WHERE approval_status = 'pending'
            ORDER BY created_at DESC
        """)
        result = db.execute(sql).fetchall()
        
        entries = []
        for row in result:
            entries.append({
                "id": row.id,
                "userId": row.user_id,
                "projectId": row.project_id,
                "projectName": row.project_name,
                "clientName": row.client_name,
                "startTime": row.start_time,
                "endTime": row.end_time,
                "duration": row.duration,
                "createdAt": str(row.created_at) if row.created_at else None,
                "isManual": row.is_manual,
                "approvalStatus": row.approval_status,
                "userName": row.user_name  # نام یا شناسه کاربر برای ادمین
            })
            
        return {"entries": entries}
    except Exception as e:
        print("--- PENDING ERROR ---:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending entries: {str(e)}")


# 4. تایید یا رد کردن درخواست توسط ادمین
class ApprovalActionRequest(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    entryId: str = Field(..., alias="entryId")
    status: str = Field(..., alias="status") # 'approved' یا 'rejected'

    class Config:
        populate_by_name = True

@app.post("/time-entries/approve")
def approve_time_entry(payload: ApprovalActionRequest, db: Session = Depends(get_db)):
    schema = payload.tenantSchema
    try:
        sql = text(f"""
            UPDATE {schema}.time_entries 
            SET approval_status = :status
            WHERE id = :entry_id
        """)
        db.execute(sql, {"status": payload.status, "entry_id": payload.entryId})
        
        db.commit()
        return {"status": "success", "message": f"Entry status updated to {payload.status}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update entry status: {str(e)}")

@app.get("/users/list")
def get_users_list(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        query = text(f"""
            SELECT id, full_name, email, role, COALESCE(include_in_reports, TRUE) as include_in_reports 
            FROM {tenantSchema}.users
        """)
        users = db.execute(query).fetchall()
        
        return {
            "users": [
                {
                    "id": str(u.id),
                    "fullName": u.full_name,
                    "email": u.email,
                    "role": u.role,
                    "includeInReports": bool(u.include_in_reports)
                } for u in users
            ]
        }
    except Exception as e:
        print("ERROR IN /users/list:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

    
@app.post("/users/create")
def create_user(payload: CreateUserRequest, db: Session = Depends(get_db)):
    schema = payload.tenantSchema
    user_id = f"usr_{uuid4().hex[:12]}"
    
    try:
        ensure_tenant_tables(schema, db)
        
        sql = text(f"""
            INSERT INTO {schema}.users (id, full_name, email, role, include_in_reports)
            VALUES (:id, :full_name, :email, :role, :include_in_reports)
        """)
        
        db.execute(sql, {
            "id": user_id,
            "full_name": payload.fullName,
            "email": payload.email,
            "role": payload.role,
            "include_in_reports": payload.includeInReports
        })
        db.commit()
        
        return {"status": "success", "userId": user_id, "message": "User created successfully."}
    except Exception as e:
        db.rollback()
        print("🔴 ERROR IN CREATE USER:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/assign")
def assign_project(data: AssignProjectRequest, db: Session = Depends(get_db)):
    try:
        ensure_tenant_tables(data.tenantSchema, db)
        
        insert_query = text(f"""
            INSERT INTO {data.tenantSchema}.user_projects (user_id, project_id)
            VALUES (:user_id, :project_id);
        """)
        db.execute(insert_query, {"user_id": data.userId, "project_id": data.projectId})
        db.commit()
        
        return {"status": "success", "message": "Project successfully assigned to user."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/assigned-list")
def get_assigned_projects(
    tenantSchema: str = Query(...), 
    userId: str = Query(...), 
    isAdmin: bool = Query(False),
    db: Session = Depends(get_db)
):
    try:
        ensure_tenant_tables(tenantSchema, db)
        
        if isAdmin:
            query = text(f"SELECT id, name, description, is_active FROM {tenantSchema}.projects;")
            result = db.execute(query).fetchall()
        else:
            query = text(f"""
                SELECT p.id, p.name, p.description, p.is_active FROM {tenantSchema}.projects p
                JOIN {tenantSchema}.user_projects up ON p.id::text = up.project_id
                WHERE up.user_id = :user_id;
            """)
            print(f"DEBUG ---> SQL Query: {query}")
            params = {"user_id": userId}
            print(f"DEBUG ---> SQL Params: {params}")
            result = db.execute(query, params).fetchall()
            
        projects_list = [{
            "id": str(row.id),
            "name": row.name,
            "description": row.description,
            "isActive": row.is_active
        } for row in result]
        
        return {"status": "success", "projects": projects_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/create-employee-token", response_model=None)
def create_employee_token(company_id: str, employee_name: str, role: str = "employee", db: Session = Depends(get_db)):
    import uuid
    try:
        comp_uuid = UUID(company_id)
        new_user_id = uuid.uuid4()
        new_token = f"EMP_TOKEN_{uuid.uuid4().hex[:8]}"
        
        # ۱. بررسی وجود شرکت در جدول مرکزی
        comp_check = db.execute(text("SELECT id FROM timetracker.companies WHERE id = :comp_id"), {"comp_id": comp_uuid}).fetchone()
        if not comp_check:
            raise HTTPException(status_code=400, detail="Company ID does not exist in database!")
        
        # ۲. ساخت نام اسکیما به روش استاندارد
        schema_name = f"tenant_{str(comp_uuid).replace('-', '_')}"

        # ۳. درج در جدول مرکزی users
        db.execute(text("""
            INSERT INTO timetracker.users (id, display_name, role) 
            VALUES (:user_id, :display_name, :role)
            ON CONFLICT (id) DO NOTHING
        """), {"user_id": new_user_id, "display_name": employee_name, "role": role})

        # ۴. درج در جدول مرکزی company_users (برای رفع خطای کلید خارجی جدول توکن‌ها)
        db.execute(text("""
            INSERT INTO timetracker.company_users (id, company_id, user_id, status, role) 
            VALUES (:id, :comp_id, :user_id, 'active', :role)
            ON CONFLICT (id) DO NOTHING
        """), {
            "id": new_user_id, 
            "comp_id": comp_uuid, 
            "user_id": new_user_id,
            "role": role
        })

        # ۵. درج کاربر در جدولِ اسکیمای اختصاصی شرکت (برای هماهنگی با لیست کاربران)
        db.execute(text(f"""
            INSERT INTO {schema_name}.users (id, full_name, role, is_active) 
            VALUES (:user_id, :full_name, :role, true)
            ON CONFLICT (id) DO NOTHING
        """), {
            "user_id": new_user_id, 
            "full_name": employee_name, 
            "role": role
        })

        # ۶. درج توکن فعال‌سازی در جدول مرکزی توکن‌ها
        db.execute(text("""
            INSERT INTO timetracker.activation_tokens (company_user_id, token, expires_at) 
            VALUES (:user_id, :token, NOW() + INTERVAL '7 days')
        """), {
            "user_id": new_user_id, 
            "token": new_token
        })
        
        db.commit()
        return {"token": new_token, "userId": str(new_user_id), "role": role}
        
    except Exception as e:
        db.rollback()
        print(f"ERROR IN create_employee_token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
            
@app.post("/auth/register-company")
def register_company(payload: CompanyRegistrationRequest, db: Session = Depends(get_db)):
    try:
        company_id = uuid.uuid4()
        admin_user_id = uuid.uuid4()
        schema_name = f"tenant_{str(company_id).replace('-', '_')}"

        # ۱. درج شرکت در جدول مرکزی companies
        db.execute(text("""
            INSERT INTO timetracker.companies (id, name)
            VALUES (:id, :name)
        """), {"id": company_id, "name": payload.companyName})

        # ۲. درج ادمین در جدول مرکزی users
        db.execute(text("""
            INSERT INTO timetracker.users (id, display_name, role)
            VALUES (:id, :display_name, 'admin')
        """), {"id": admin_user_id, "display_name": payload.adminName})

        # ۳. اتصال ادمین به شرکت در جدول company_users
        db.execute(text("""
            INSERT INTO timetracker.company_users (id, company_id, user_id, status, role)
            VALUES (:id, :comp_id, :user_id, 'active', 'admin')
        """), {
            "id": admin_user_id,
            "comp_id": company_id,
            "user_id": admin_user_id
        })

        # ۴. ایجاد اسکیمای اختصاصی تننت و جدول‌های آن
        ensure_tenant_tables(schema_name, db)

        # ۵. درج ادمین در جدول usersِ اسکیمای تننت
        db.execute(text(f"""
            INSERT INTO {schema_name}.users (id, full_name, email, role)
            VALUES (:id, :full_name, :email, 'admin')
            ON CONFLICT (email) DO NOTHING
        """), {
            "id": str(admin_user_id),
            "full_name": payload.adminName,
            "email": payload.adminEmail
        })

        db.commit()

        return {
            "status": "success",
            "companyId": str(company_id),
            "adminId": str(admin_user_id),
            "tenantSchema": schema_name,
            "role": "admin",
            "message": "Company and Admin registered successfully."
        }

    except Exception as e:
        db.rollback()
        print(f"ERROR IN register_company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))    


import bcrypt 

@app.post("/auth/login", response_model=None)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    try:
        # ۱. پیدا کردن کاربر از روی ایمیل در جدول مرکزی
        user_row = db.execute(text("""
            SELECT id, display_name, role, password_hash 
            FROM timetracker.users 
            WHERE email = :email
        """), {"email": payload.email}).fetchone()

        if not user_row or not user_row[3]:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        user_id = user_row[0]
        stored_password_hash = user_row[3]
        role = user_row[2]

        # ۲. اعتبارسنجی رمز عبور با bcrypt.checkpw (به جای pwd_context.verify)
        is_valid = bcrypt.checkpw(
            payload.password.encode('utf-8'), 
            stored_password_hash.encode('utf-8')
        )

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        # ۳. پیدا کردن شرکت و نام اسکیما مرتبط با این کاربر (تبدیل user_id به رشته برای جلوگیری از خطای UUID)
        comp_row = db.execute(text("""
            SELECT c.id FROM timetracker.company_users cu
            JOIN timetracker.companies c ON cu.company_id = c.id
            WHERE cu.user_id = :user_id
        """), {"user_id": str(user_id)}).fetchone()

        if not comp_row:
            raise HTTPException(status_code=403, detail="User is not assigned to any company.")

        comp_id = comp_row[0]
        schema_name = f"tenant_{str(comp_id).replace('-', '_')}"

        # ۴. بازگرداندن اطلاعات مورد نیاز برای فرانت‌اند
        return {
            "status": "success",
            "userId": str(user_id),
            "role": role,
            "tenantSchema": schema_name,
            "companyId": str(comp_id)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"ERROR IN login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/admin/users/{user_id}/report-status")
def update_user_report_status(user_id: str, payload: ReportStatusPayload, db: Session = Depends(get_db)):
    try:
        sql = text(f"""
            UPDATE {payload.tenantSchema}.users 
            SET include_in_reports = :include_in_reports 
            WHERE id = :user_id
        """)
        db.execute(sql, {"include_in_reports": payload.includeInReports, "user_id": user_id})
        log_audit_event(
            db=db,
            schema=payload.tenantSchema,
            admin_id="admin_user", 
            action_type="UPDATE_USER_REPORT_STATUS",
            target_type="USER",
            target_id=user_id,
            details=f"Changed include_in_reports to {payload.includeInReports}"
        )
        db.commit()
        
        return {"status": "success", "message": "User report status updated successfully."}
    except Exception as e:
        db.rollback()
        print("ERROR IN update_user_report_status:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/user-projects/{user_id}")
def get_user_assigned_projects(tenantSchema: str, user_id: str, db: Session = Depends(get_db)):
    try:
        query = text(f"""
            SELECT p.id, p.project_name, p.client_name
            FROM {tenantSchema}.user_projects up
            JOIN {tenantSchema}.projects p ON up.project_id = p.id
            WHERE up.user_id = :user_id
        """)
        projects = db.execute(query, {"user_id": user_id}).fetchall()
        
        return [
            {
                "id": str(p.id),
                "projectName": p.project_name,
                "clientName": p.client_name
            } for p in projects
        ]
    except Exception as e:
        print("ERROR IN user-projects:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/time-entries/sync-batch")
def sync_time_entries_batch(payload: SyncPayload, db: Session = Depends(get_db)):
    try:
        synced_count = 0
        conflicts = []

        for entry in payload.entries:
            # بررسی اینکه آیا این رکورد قبلاً با این id در سرور ثبت شده است یا خیر
            check_sql = text(f"SELECT id, approval_status FROM {payload.tenantSchema}.time_entries WHERE id = :id")
            existing = db.execute(check_sql, {"id": entry.id}).fetchone()

            if existing:
                # اگر رکورد قبلاً توسط ادمین تایید شده باشد و کاربر لوکال تغییرش داده باشد (تضاد)
                if existing.approval_status == 'approved':
                    conflicts.append({"id": entry.id, "reason": "Already approved by admin, local changes ignored."})
                    continue
                else:
                    # آپدیت رکورد موجود اگر هنوز در حالت pending است
                    update_sql = text(f"""
                        UPDATE {payload.tenantSchema}.time_entries 
                        SET start_time = :start_time, end_time = :end_time, duration = :duration, note = :note
                        WHERE id = :id
                    """)
                    db.execute(update_sql, {
                        "id": entry.id,
                        "start_time": entry.startTime,
                        "end_time": entry.endTime,
                        "duration": entry.duration,
                        "note": entry.note
                    })
            else:
                # درج رکورد جدید (Upsert / Insert)
                insert_sql = text(f"""
                    INSERT INTO {payload.tenantSchema}.time_entries 
                    (id, user_id, project_id, project_name, client_name, start_time, end_time, duration, note, approval_status, synced_at)
                    VALUES (:id, :user_id, :project_id, :project_name, :client_name, :start_time, :end_time, :duration, :note, 'pending', NOW())
                """)
                db.execute(insert_sql, {
                    "id": entry.id,
                    "user_id": payload.userId,
                    "project_id": entry.projectId,
                    "project_name": entry.projectName,
                    "client_name": entry.clientName,
                    "start_time": entry.startTime,
                    "end_time": entry.endTime,
                    "duration": entry.duration,
                    "note": entry.note
                })
            synced_count += 1

        db.commit()
        return {"status": "success", "syncedCount": synced_count, "conflicts": conflicts}
    except Exception as e:
        db.rollback()
        print("ERROR IN SYNC BATCH:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/export-datev")
def export_datev_report(tenantSchema: str, year: int, month: int, db: Session = Depends(get_db)):
    try:
        # استخراج رکوردهای تاییدشده‌ی ماه مورد نظر
        sql = text(f"""
            SELECT te.user_id, te.project_name, te.duration, te.start_time, te.note, te.approval_status
            FROM {tenantSchema}.time_entries te
            WHERE EXTRACT(YEAR FROM TO_TIMESTAMP(te.start_time / 1000.0)) = :year
              AND EXTRACT(MONTH FROM TO_TIMESTAMP(te.start_time / 1000.0)) = :month
              AND te.approval_status = 'approved'
        """)
        entries = db.execute(sql, {"year": year, "month": month}).fetchall()

        # ساخت فایل CSV در حافظه (In-Memory Buffer)
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';') # استاندارد آلمان معمولاً با کاما (;) کار می‌کند
        
        # هدرهای استاندارد برای گزارش ساعت کارکرد
        writer.writerow(["UserID", "Project", "Date", "Hours", "Note", "Status"])

        for row in entries:
            date_str = datetime.fromtimestamp(row.start_time / 1000.0).strftime('%d.%m.%Y')
            hours_val = round(row.duration / 60, 2) # تبدیل دقیقه به ساعت اعشاری
            writer.writerow([
                row.user_id,
                row.project_name,
                date_str,
                str(hours_val).replace('.', ','), # استاندارد عدد اعشاری در آلمان با کاما است
                row.note or "",
                row.approval_status
            ])

        output.seek(0)
        
        # بازگرداندن فایل به صورت استریم برای دانلود
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=DATEV_Report_{year}_{month:02d}.csv"
        return response

    except Exception as e:
        print("ERROR IN DATEV EXPORT:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/compliance-reminders")
def check_admin_reminders(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        current_day = datetime.now().day
        
        # اگر در ۵ روز پایانی ماه باشیم، رکوردهای پندینگ را چک می‌کنیم
        if current_day >= 25:
            sql = text(f"""
                SELECT COUNT(*) as pending_count 
                FROM {tenantSchema}.time_entries 
                WHERE approval_status = 'pending'
            """)
            result = db.execute(sql).fetchone()
            pending_count = result.pending_count if result else 0
            
            if pending_count > 0:
                return {
                    "hasReminder": True,
                    "message": f"Reminder: You have {pending_count} unapproved time entries waiting before month-end payroll processing."
                }
                
        return {"hasReminder": False}
    except Exception as e:
        return {"hasReminder": False, "error": str(e)}

@app.put("/projects/update")
def update_project(payload: ProjectUpdateRequest, db: Session = Depends(get_db)):
    try:
        query = text(f"""
            UPDATE {payload.tenantSchema}.projects
            SET name = :name, 
                description = :description, 
                is_active = :is_active
            WHERE id = :project_id
        """)
        
        db.execute(
            query, 
            {
                "name": payload.name, 
                "description": payload.description, 
                "is_active": payload.isActive, 
                "project_id": payload.projectId
            }
        )

#        query_entries = text(f"""
#                    UPDATE {payload.tenantSchema}.time_entries
#                    SET project_name = :name
#                    WHERE project_id = :project_id
#                """)
#        db.execute(query_entries, {
#                    "name": payload.name, 
#                    "project_id": payload.projectId
#                })

        db.commit()
        
        return {"status": "success", "message": "Project updated successfully"}
    except Exception as e:
        db.rollback()
        print("ERROR IN update-project:", str(e))
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/reports/by-project")
def get_report_by_project(tenantSchema: str, year: int, month: int, db: Session = Depends(get_db)):
    try:
        import calendar
        from datetime import datetime
        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59)
        
        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000)

        query = text(f"""
            SELECT 
                        p.id AS project_id,
                        p.name,
                        p.is_active,
                        t.client_name,
                        COALESCE(SUM(t.duration), 0) AS total_minutes,
                        COUNT(t.id) AS total_entries,
                        MAX(t.client_name) AS client_name
                    FROM {tenantSchema}.projects p
                    LEFT JOIN {tenantSchema}.time_entries t ON p.id = t.project_id 
                        AND t.start_time >= :start_ts AND t.start_time <= :end_ts
                    GROUP BY p.id, p.name, p.is_active, t.client_name
                    ORDER BY t.client_name, total_minutes DESC
            """)
        results = db.execute(query, {"start_ts": start_ts, "end_ts": end_ts}).fetchall()
        
        report_data = [
            {
                "projectId": str(row.project_id),
                "projectName": row.name,
                "isActive": row.is_active,
                "clientName": row.client_name,
                "totalMinutes": row.total_minutes,
                "totalEntries": row.total_entries
            } for row in results
        ]
        
        return {"status": "success", "report": report_data}
    except Exception as e:
        print("ERROR IN project report:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/admin/absences/approval")
def update_absence_approval(payload: AbsenceApprovalRequest, db: Session = Depends(get_db)):
    try:
        query = text(f"""
            UPDATE {payload.tenantSchema}.absences
            SET approval_status = :status
            WHERE id = :absence_id
        """)
        db.execute(query, {"status": payload.status, "absence_id": payload.absenceId})
        db.commit()
        return {"status": "success", "message": f"Absence status updated to {payload.status}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
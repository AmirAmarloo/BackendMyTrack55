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

    class Config:
        populate_by_name = True


class ManualEntryRequest(BaseModel):
    tenantSchema: str = Field(..., alias="tenantSchema")
    userId: str = Field(..., alias="userId")  # شناسه کارمندی که ساعت برای او ثبت می‌شود
    projectId: str = Field(..., alias="projectId")
    projectName: str = Field(..., alias="projectName")
    clientName: Optional[str] = Field(None, alias="clientName")
    startTime: int = Field(..., alias="startTime")
    endTime: int = Field(..., alias="endTime")
    duration: int = Field(..., alias="duration")
    note: str = Field(..., alias="note") # دلیل ثبت دستی توسط ادمین یا کاربر

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

    class Config:
        populate_by_name = True        

class CreateUserRequest(BaseModel):
    tenantSchema: str
    fullName: str
    email: str
    role: str = "employee"  # 'admin' یا 'employee'

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

# ---------------------------- Database Tables Setup -------------------------------

def ensure_tenant_tables(schema_name: str, db: Session):
    db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name};"))
    
    init_sql = text(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.users (
            id VARCHAR(50) PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            full_name VARCHAR(255),
            role VARCHAR(50) DEFAULT 'employee',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
            client_name VARCHAR(255),
            start_time BIGINT NOT NULL,
            end_time BIGINT,
            duration INT DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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

        ALTER TABLE timetracker.users 
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


# --- Endpoints ---

@app.post("/auth/activate")
def activate_device(payload: ActivationRequest, db: Session = Depends(get_db)):
    try:
        # ۱. پیدا کردن توکن و اطلاعات کاربر و شرکت از اسکیمای timetracker
        token_row = db.execute(text("""
            SELECT t.company_user_id, cu.company_id, c.id AS comp_id
            FROM timetracker.activation_tokens t
            JOIN timetracker.company_users cu ON t.company_user_id = cu.id
            JOIN timetracker.companies c ON cu.company_id = c.id
            WHERE t.token = :token AND t.expires_at > NOW() AND t.used_at IS NULL
        """), {"token": payload.token}).fetchone()

        if not token_row:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user_uuid = token_row.company_user_id
        company_uuid = token_row.company_id
        
        # ساخت نام اسکیما از روی UUID شرکت
        schema_name = f"tenant_{str(company_uuid).replace('-', '_')}"

        # ۲. خواندن پروژه‌ها با استفاده از Savepoint (برای جلوگیری از ابورت شدن تراکنش اصلی)
        projects_list = []
        try:
            with db.begin_nested(): # ایجاد یک نقطه ذخیره موقت (Savepoint)
                projects_query = text(f"""
                    SELECT p.id, p.name
                    FROM {schema_name}.projects p
                    JOIN {schema_name}.user_projects up ON up.project_id = p.id
                    WHERE up.user_id = :u_id::uuid AND p.is_active = true
                """)
                projects_rows = db.execute(projects_query, {"u_id": str(user_uuid)}).fetchall()
                projects_list = [{"id": str(r.id), "name": r.name} for r in projects_rows]
        except Exception as ex:
            print(f"Notice: Could not fetch projects from tenant schema yet: {ex}")
            projects_list = [] # اگر جدول‌ها هنوز ساخته نشده‌اند، لیست خالی برمی‌گرداند تا درخواست متوقف نشود

        # ۳. به روزرسانی توکن به عنوان استفاده شده
        db.execute(text("""
            UPDATE timetracker.activation_tokens 
            SET used_at = NOW() 
            WHERE token = :token
        """), {"token": payload.token})

        db.commit()
        
        return {
            "status": "activated",
            "userId": str(user_uuid),
            "companyId": str(company_uuid),
            "schemaName": schema_name,
            "projects": projects_list
        }

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        print(f"ERROR IN activate_device: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
            
@app.post("/time-entries/sync")
def sync_time_entries(payload: SyncPayload, db: Session = Depends(get_db)):
    schema = payload.tenantSchema

    try:
        ensure_tenant_tables(schema, db)

        insert_entry_sql = text(f"""
            INSERT INTO {schema}.time_entries 
            (id, user_id, project_id, project_name, client_name, start_time, end_time, duration)
            VALUES (:id, :user_id, :project_id, :project_name, :client_name, :start_time, :end_time, :duration)
            ON CONFLICT (id) DO UPDATE 
            SET end_time = EXCLUDED.end_time, 
                duration = EXCLUDED.duration,
                project_name = EXCLUDED.project_name;
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
                    detail=f"Project with ID '{entry.projectId}' does not exist in tenant schema. Please create a project first."
                )
    
            # ۲. درج تایم‌انِتری در صورت معتبر بودن پروژه
            db.execute(insert_entry_sql, {
                "id": entry.id,
                "user_id": entry.userId,
                "project_id": entry.projectId,
                "project_name": entry.projectName,
                "client_name": entry.client_name if hasattr(entry, 'client_name') else entry.clientName,
                "start_time": entry.startTime,
                "end_time": entry.endTime,
                "duration": entry.duration or 0
            })

            if entry.breaks:
                for brk in entry.breaks:
                    db.execute(insert_break_sql, {
                        "id": brk.id,
                        "time_entry_id": entry.id,
                        "start_time": brk.startTime,
                        "end_time": brk.endTime,
                        "duration": brk.duration or 0
                    })

        db.commit()
        return {"status": "success", "synced_count": len(payload.entries)}

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Sync failed for schema {schema}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to sync entries: {str(e)}")

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
        """).bindparams(schema=tenantSchema)
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
        query_entries = text(f"""
            SELECT user_id, client_name, project_name, duration, start_time
            FROM {tenantSchema}.time_entries
            WHERE EXTRACT(YEAR FROM TIMESTAMP 'epoch' + start_time * INTERVAL '1 millisecond') = :year
              AND EXTRACT(MONTH FROM TIMESTAMP 'epoch' + start_time * INTERVAL '1 millisecond') = :month
        """)
        entries = db.execute(query_entries, {"year": year, "month": month}).fetchall()
        
        query_absences = text(f"""
            SELECT user_id, absence_type, start_date, end_date, is_approved
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
            "entries": [{
                "userId": e.user_id,
                "clientName": e.client_name,
                "projectName": e.project_name,
                "durationMinutes": e.duration,
                "breakMinutes": 0,
                "startTime": str(e.start_time)
            } for e in entries],
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
        
        sql = text(f"""
            INSERT INTO {schema}.time_entries 
            (id, user_id, project_id, project_name, client_name, start_time, end_time, duration, is_manual, approval_status)
            VALUES (:id, :user_id, :project_id, :project_name, :client_name, :start_time, :end_time, :duration, TRUE, :approval_status)
        """)
        
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
        db.commit()
        
        return {"status": "success", "entryId": entry_id, "message": "Manual entry processed successfully."}
    except Exception as e:
        db.rollback()
        print("🔴 ERROR IN MANUAL ENTRY:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# 2. لیست کاربران شرکت (برای اینکه ادمین بدد برای چه کسی دارد ساعت ثبت می‌کند)
@app.get("/users/list")
def list_tenant_users(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        sql = text(f"""
            SELECT id, full_name, email, role, is_active 
            FROM {tenantSchema}.users 
            ORDER BY full_name ASC
        """)
        result = db.execute(sql).fetchall()
        
        users = []
        for row in result:
            users.append({
                "id": row[0],
                "fullName": row[1],
                "email": row[2],
                "role": row[3],
                "isActive": row[4]
            })
        return {"status": "success", "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


@app.get("/time-entries/pending")
def get_pending_entries(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        sql = text(f"""
            SELECT 
                id, 
                user_id, 
                project_id, 
                project_name, 
                client_name, 
                start_time, 
                end_time, 
                duration, 
                created_at, 
                is_manual, 
                approval_status
            FROM {tenantSchema}.time_entries 
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
                "userName": row.user_id  # نام یا شناسه کاربر برای ادمین
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
def list_users(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        # اطمینان از وجود جدول کاربران در اسکیما تننت
        ensure_tenant_tables(tenantSchema, db)
        
        sql = text(f"SELECT id, full_name, email, role, created_at FROM {tenantSchema}.users ORDER BY created_at DESC")
        result = db.execute(sql).fetchall()
        
        users = []
        for row in result:
            users.append({
                "id": row.id,
                "fullName": row.full_name,
                "email": row.email,
                "role": row.role,
                "createdAt": str(row.created_at) if row.created_at else None
            })
            
        return {"status": "success", "users": users}
    except Exception as e:
        print("🔴 ERROR IN LIST USERS:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/create")
def create_user(payload: CreateUserRequest, db: Session = Depends(get_db)):
    schema = payload.tenantSchema
    user_id = f"usr_{uuid4().hex[:12]}"
    
    try:
        ensure_tenant_tables(schema, db)
        
        sql = text(f"""
            INSERT INTO {schema}.users (id, full_name, email, role)
            VALUES (:id, :full_name, :email, :role)
        """)
        
        db.execute(sql, {
            "id": user_id,
            "full_name": payload.fullName,
            "email": payload.email,
            "role": payload.role
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
            result = db.execute(query, {"user_id": userId}).fetchall()
            
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
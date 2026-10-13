from typing import List, Optional
from fastapi import Depends, HTTPException, status, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field
import logging
from uuid import uuid4

import uuid

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


# ---------------------------- Database Tables Setup -------------------------------

def ensure_tenant_tables(schema: str, db: Session):
    init_sql = text(f"""
        CREATE TABLE IF NOT EXISTS {schema}.users (
            id VARCHAR(50) PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            full_name VARCHAR(255),
            role VARCHAR(50) DEFAULT 'employee',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS {schema}.clients (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            address TEXT,
            tax_id VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS {schema}.projects (
            id UUID PRIMARY KEY,
            company_id UUID NOT NULL,
            client_id UUID REFERENCES {schema}.clients(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS {schema}.time_entries (
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

        CREATE TABLE IF NOT EXISTS {schema}.breaks (
            id VARCHAR(50) PRIMARY KEY,
            time_entry_id UUID REFERENCES {schema}.time_entries(id) ON DELETE CASCADE,
            start_time BIGINT NOT NULL,
            end_time BIGINT,
            duration INT DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

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

        CREATE TABLE IF NOT EXISTS {schema}.absences (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            absence_type VARCHAR(20) NOT NULL,
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
    token_query = text("SELECT company_user_id, used_at FROM timetracker.activation_tokens WHERE token = :token")
    token_row = db.execute(token_query, {"token": token_str}).fetchone()

    if not token_row:
        raise HTTPException(status_code=400, detail="Invalid token")
    if token_row.used_at is not None:
        raise HTTPException(status_code=400, detail="Token already used")

    company_user_id = token_row.company_user_id
    company_query = text("SELECT c.id, c.name, cu.role FROM timetracker.companies c JOIN timetracker.company_users cu ON cu.company_id = c.id WHERE cu.id = :cu_id")
    company_row = db.execute(company_query, {"cu_id": company_user_id}).fetchone()

    if not company_row:
        raise HTTPException(status_code=400, detail="Company user not found")

    company_id, company_name, user_role = company_row
    schema_name = f"tenant_{str(company_id).replace('-', '_')}"

    ensure_tenant_tables(schema_name, db)

    projects_query = text(f"SELECT id, name FROM {schema_name}.projects WHERE is_active = true")
    projects_rows = db.execute(projects_query).fetchall()
    projects_list = [{"id": str(r.id), "name": r.name} for r in projects_rows]

    db.execute(text("UPDATE timetracker.activation_tokens SET used_at = NOW() WHERE token = :token"), {"token": token_str})
    db.commit()

    return {
        "clientName": company_name,
        "tenantSchema": schema_name,
        "authToken": f"Bearer_secret_token_for_{company_user_id}",
        "role": user_role or "employee",
        "projects": projects_list
    }


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
            db.execute(insert_entry_sql, {
                "id": entry.id,
                "user_id": entry.userId,
                "project_id": entry.projectId,
                "project_name": entry.projectName,
                "client_name": entry.clientName,
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
            FROM {schema}.absences WHERE user_id = :user_id ORDER BY start_date DESC
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
    entry_id = f"man_{uuid4().hex[:12]}"
    
    try:
        ensure_tenant_tables(schema, db)
        
        sql = text(f"""
            INSERT INTO {schema}.time_entries 
            (id, user_id, project_id, project_name, client_name, start_time, end_time, duration, is_manual, approval_status)
            VALUES (:id, :user_id, :project_id, :project_name, :client_name, :start_time, :end_time, :duration, TRUE, 'pending')
        """)
        
        db.execute(sql, {
            "id": entry_id,
            "user_id": payload.userId,
            "project_id": payload.projectId,
            "project_name": payload.projectName,
            "client_name": payload.clientName,
            "start_time": payload.startTime,
            "end_time": payload.endTime,
            "duration": payload.duration
        })
        db.commit()
        
        return {"status": "success", "entryId": entry_id, "message": "Manual entry submitted for approval."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit manual entry: {str(e)}")


@app.post("/time-entries/manual")
def create_manual_entry(payload: ManualEntryRequest, db: Session = Depends(get_db)):
    schema = payload.tenantSchema
    entry_id = f"man_{uuid4().hex[:12]}"
    
    # اگر ادمین ثبت کند، مستقیم تایید می‌شود (approved)، وگرنه در انتظار تایید می‌ماند (pending)
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
        raise HTTPException(status_code=500, detail=f"Failed to submit manual entry: {str(e)}")


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


# 3. گرفتن لیست ساعت‌های در انتظار تایید (برای ادمین)
@app.get("/time-entries/pending")
def get_pending_entries(tenantSchema: str, db: Session = Depends(get_db)):
    try:
        sql = text(f"""
            SELECT te.id, te.user_id, u.full_name, te.project_id, te.project_name, 
                   te.start_time, te.end_time, te.duration, te.is_manual, te.approval_status
            FROM {tenantSchema}.time_entries te
            LEFT JOIN {tenantSchema}.users u ON te.user_id = u.id
            WHERE te.approval_status = 'pending'
            ORDER BY te.start_time DESC
        """)
        result = db.execute(sql).fetchall()
        
        entries = []
        for row in result:
            entries.append({
                "id": row[0],
                "userId": row[1],
                "userName": row[2] or "Unknown",
                "projectId": row[3],
                "projectName": row[4],
                "startTime": row[5],
                "endTime": row[6],
                "duration": row[7],
                "isManual": row[8],
                "approvalStatus": row[9]
            })
        return {"status": "success", "entries": entries}
    except Exception as e:
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
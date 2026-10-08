from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

class ActivationRequest(BaseModel):
    token: str

class TimeEntryItem(BaseModel):
    id: str
    projectId: str
    projectName: str
    clientName: Optional[str] = None
    startTime: int
    endTime: Optional[int] = None
    duration: Optional[int] = 0

class SyncPayload(BaseModel):
    tenantSchema: str
    entries: List[TimeEntryItem]

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
    
    insert_sql = text(f"""
        INSERT INTO {schema}.time_entries 
        (id, project_id, project_name, client_name, start_time, end_time, duration)
        VALUES (:id, :projectId, :projectName, :clientName, :startTime, :endTime, :duration)
        ON CONFLICT (id) DO UPDATE 
        SET end_time = EXCLUDED.end_time, 
            duration = EXCLUDED.duration
    """)

    for entry in payload.entries:
        db.execute(insert_sql, entry.model_dump())

    db.commit()

    return {"status": "success", "synced_count": len(payload.entries)}
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from app.database import get_db
from app.schemas.auth import ActivationRequest, ActivationResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/activate", response_model=ActivationResponse)
def activate_device(payload: ActivationRequest, db: Session = Depends(get_db)):
    try:
        raw_token = payload.activationToken.strip()
        print(f"\n---> [DEBUG] Received token from mobile: '{raw_token}'")

        # 0. ابتدا بررسی کنیم اصلاً توکنی با این نام در دیتابیس هست یا نه
        check_exist = db.execute(
            text("SELECT id, used_at, expires_at FROM timetracker.activation_tokens WHERE token = :token"),
            {"token": raw_token}
        ).fetchone()

        if not check_exist:
            print(f"---> [REASON FAILED]: Token '{raw_token}' NOT FOUND in database!")
        else:
            print(f"---> [DEBUG] Token details in DB -> used_at: {check_exist[1]}, expires_at: {check_exist[2]}")

        # 1. Check activation token using PostgreSQL native NOW()
        token_query = text("""
            SELECT id, company_user_id 
            FROM timetracker.activation_tokens 
            WHERE token = :token 
              AND used_at IS NULL 
              AND expires_at > NOW()
        """)
        token_row = db.execute(token_query, {"token": raw_token}).fetchone()

        if not token_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid, used, or expired activation token."
            )

        token_id, company_user_id = token_row

        # 2. Get company details via company_users
        company_query = text("""
            SELECT c.id, c.name 
            FROM timetracker.companies c
            JOIN timetracker.company_users cu ON cu.company_id = c.id
            WHERE cu.id = :cu_id
        """)
        company_row = db.execute(company_query, {"cu_id": company_user_id}).fetchone()

        if not company_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company or company user not found."
            )

        company_id, company_name = company_row
        schema_name = f"tenant_{str(company_id).replace('-', '_')}"

        # 3. Fetch active projects from tenant schema
        projects_query = text(f"""
            SELECT id, name, description, is_active 
            FROM {schema_name}.projects 
            WHERE is_active = true
        """)
        projects_rows = db.execute(projects_query).fetchall()

        projects_list = [
            {
                "id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "is_active": row[3]
            }
            for row in projects_rows
        ]

        # 4. Mark token as used using PostgreSQL native NOW()
        update_token_query = text("""
            UPDATE timetracker.activation_tokens 
            SET used_at = NOW(), 
                updated_at = NOW()
            WHERE id = :token_id
        """)
        db.execute(update_token_query, {"token_id": token_id})
        db.commit()
        
        auth_jwt = f"mock_jwt_token_for_{schema_name}"

        print(f"---> [SUCCESS] Device successfully activated for: {company_name}\n")

        return {
            "clientName": company_name,
            "tenantSchema": schema_name,
            "authToken": auth_jwt,
            "projects": projects_list
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"---> [SERVER ERROR]: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
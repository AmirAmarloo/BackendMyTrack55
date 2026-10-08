from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class ActivationRequest(BaseModel):
    activationToken: str

class ProjectSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class ActivationResponse(BaseModel):
    clientName: str
    tenantSchema: str
    authToken: str
    projects: List[ProjectSchema]
import asyncpg
from fastapi import APIRouter, Depends
from uuid import UUID
from src.api.schemas.organizer_schema import (
    OrganizerCreateRequest, OrganizerCreateResponse, OrganizerListResponse,
    OrganizerResponse, OrganizerUpdateRequest, OrganizerStatusRequest
)
from src.shared.core.services.organizer_service import OrganizerService
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_admin
from src.api.models.models import User

router = APIRouter(prefix="/api/v1/organizers", tags=["organizers"])

@router.post("", response_model=OrganizerCreateResponse)
async def create_organizer(
    data: OrganizerCreateRequest,
    admin: User = Depends(get_current_admin),
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = OrganizerService(db)
    return await service.create_organizer(data, admin.id)

@router.get("", response_model=OrganizerListResponse)
async def list_organizers(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_current_admin),
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = OrganizerService(db)
    return await service.get_all_organizers(skip, limit)

@router.get("/{organizer_id}", response_model=OrganizerResponse)
async def get_organizer(
    organizer_id: UUID,
    admin: User = Depends(get_current_admin),
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = OrganizerService(db)
    return await service.get_organizer(organizer_id)

@router.put("/{organizer_id}", response_model=OrganizerResponse)
async def update_organizer(
    organizer_id: UUID,
    data: OrganizerUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = OrganizerService(db)
    return await service.update_organizer(organizer_id, data, admin.id)

@router.patch("/{organizer_id}/status")
async def update_organizer_status(
    organizer_id: UUID,
    data: OrganizerStatusRequest,
    admin: User = Depends(get_current_admin),
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = OrganizerService(db)
    return await service.update_status(organizer_id, data, admin.id)

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.routers.deps import auth_required, get_org_service
from src.exceptions.db_exceptions import NotFoundError
from src.schemas.org_schema import OrgCreate, OrgPublic, OrgUpdate
from src.services.org_service import OrgService

org_router = APIRouter(
    prefix="/org", tags=["orgs"], dependencies=[Depends(auth_required)]
)

logger = logging.getLogger(__name__)


@org_router.post("", status_code=status.HTTP_201_CREATED)
async def create_org(
    org_data: OrgCreate,
    service: OrgService = Depends(get_org_service),
) -> OrgPublic:
    try:
        return await service.create_org(org_data)
    except Exception as e:
        logger.exception("error while creating org")
        raise HTTPException(status_code=500, detail=str(e)) from e


@org_router.get("")
async def list_orgs(
    limit: Annotated[int, Query(le=100)] = 100,
    offset: int = 0,
    service: OrgService = Depends(get_org_service),
) -> list[OrgPublic]:
    try:
        return list(await service.list_orgs(limit=limit, offset=offset))
    except Exception as e:
        logger.exception("error while listing orgs")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@org_router.get("/{org_id}")
async def get_org(
    org_id: int,
    service: OrgService = Depends(get_org_service),
) -> OrgPublic:
    try:
        org = await service.get_org(org_id)
        if not org:
            raise NotFoundError
        return org
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="Org not found") from e
    except Exception as e:
        logger.exception("error while fetching org")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@org_router.patch("/{org_id}")
async def update_org(
    org_id: int,
    org_data: OrgUpdate,
    service: OrgService = Depends(get_org_service),
) -> OrgPublic:
    try:
        return await service.update_org(org_id, org_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="Org not found") from e
    except Exception as e:
        logger.exception("error while updating org")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@org_router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org(
    org_id: int,
    service: OrgService = Depends(get_org_service),
) -> None:
    try:
        deleted = await service.remove_org(org_id)
        if not deleted:
            raise NotFoundError
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="Org not found") from e
    except Exception as e:
        logger.exception("error while deleting org")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

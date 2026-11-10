from fastapi import APIRouter, Depends

from app.application.use_cases.admin import ReferenceData
from app.presentation.dependencies.security import provide
from app.presentation.schemas.admin import CategoryOut, CityOut, RegionOut

router = APIRouter(prefix="/reference", tags=["Référentiels"])


@router.get("/regions", response_model=list[RegionOut])
def regions(uc: ReferenceData = Depends(provide(ReferenceData))):
    return uc.list_regions()


@router.get("/cities", response_model=list[CityOut])
def cities(region_id: int | None = None, uc: ReferenceData = Depends(provide(ReferenceData))):
    return uc.list_cities(region_id)


@router.get("/categories", response_model=list[CategoryOut])
def categories(uc: ReferenceData = Depends(provide(ReferenceData))):
    return uc.list_categories()

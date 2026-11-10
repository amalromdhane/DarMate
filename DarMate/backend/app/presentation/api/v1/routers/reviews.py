from fastapi import APIRouter, Depends

from app.application.dto.dto import Actor
from app.application.use_cases.reviews import CreateReview
from app.presentation.dependencies.security import get_current_actor, provide
from app.presentation.schemas import social as s

router = APIRouter(prefix="/reviews", tags=["Évaluations"])


@router.post("", response_model=s.ReviewOut, status_code=201)
def create(body: s.ReviewIn, actor: Actor = Depends(get_current_actor), usecase: CreateReview = Depends(provide(CreateReview))):
    return usecase.execute(actor, body.rental_request_id, body.target_type, body.rating, body.comment, body.reviewee_id)

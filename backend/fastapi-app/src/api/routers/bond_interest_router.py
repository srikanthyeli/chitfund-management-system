from fastapi import APIRouter
from src.api.controllers.bond_interest_controller import BondInterestController
from src.api.schemas.bond_interest_schema import BondInterestRequest, BondInterestResponse

router = APIRouter(prefix="/api/v1/financial-utilities/bond-interest", tags=["Bond Interest"])


@router.post("/calculate", response_model=BondInterestResponse)
def calculate_bond_interest(payload: BondInterestRequest) -> BondInterestResponse:
    return BondInterestController.calculate(payload)

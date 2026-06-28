from src.api.schemas.bond_interest_schema import BondInterestRequest, BondInterestResponse
from src.shared.core.services.bond_interest_service import BondInterestService


class BondInterestController:
    @staticmethod
    def calculate(payload: BondInterestRequest) -> BondInterestResponse:
        result = BondInterestService.calculate(
            principal=payload.principal,
            interest_rate=payload.interest_rate,
            bond_start_date=payload.bond_start_date,
            calculation_date=payload.calculation_date,
        )
        return BondInterestResponse(**result)

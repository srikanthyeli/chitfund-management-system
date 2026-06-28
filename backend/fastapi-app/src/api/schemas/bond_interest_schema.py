from pydantic import BaseModel, field_validator
from datetime import date


class BondInterestRequest(BaseModel):
    principal: float
    interest_rate: float  # ₹X per ₹100 per month → X%
    bond_start_date: date
    calculation_date: date

    @field_validator("calculation_date")
    @classmethod
    def calc_date_not_before_start(cls, v, info):
        if "bond_start_date" in info.data and v < info.data["bond_start_date"]:
            raise ValueError("Calculation Date cannot be earlier than Bond Start Date.")
        return v


class BondInterestResponse(BaseModel):
    principal: float
    interest_rate: float
    bond_start_date: date
    calculation_date: date
    expiry_date: date
    duration_years: int
    duration_months: int
    duration_days: int
    monthly_interest: float
    daily_interest: float
    complete_months: int
    remaining_days: int
    interest: float
    total_amount: float
    bond_status: str          # ACTIVE | EXPIRED
    suggested_new_principal: float | None

from datetime import date
from dateutil.relativedelta import relativedelta

BOND_VALIDITY_YEARS = 3


class BondInterestService:
    @staticmethod
    def calculate(
        principal: float,
        interest_rate: float,
        bond_start_date: date,
        calculation_date: date,
    ) -> dict:
        expiry_date = bond_start_date + relativedelta(years=BOND_VALIDITY_YEARS)
        bond_status = "ACTIVE" if calculation_date <= expiry_date else "EXPIRED"

        # Duration between bond_start_date and calculation_date
        delta = relativedelta(calculation_date, bond_start_date)
        duration_years = delta.years
        duration_months = delta.months
        duration_days = delta.days

        # Flat complete months & remaining days
        complete_months_total = duration_years * 12 + duration_months
        remaining_days = duration_days

        monthly_interest = round(principal * (interest_rate / 100), 2)
        daily_interest = round(monthly_interest / 30, 2)

        interest = round(
            complete_months_total * monthly_interest + remaining_days * daily_interest, 2
        )
        total_amount = round(principal + interest, 2)

        suggested_new_principal = None
        if bond_status == "EXPIRED":
            # Interest up to expiry date only
            expiry_delta = relativedelta(expiry_date, bond_start_date)
            exp_months = expiry_delta.years * 12 + expiry_delta.months
            exp_days = expiry_delta.days
            interest_till_expiry = round(
                exp_months * monthly_interest + exp_days * daily_interest, 2
            )
            suggested_new_principal = round(principal + interest_till_expiry, 2)

        return {
            "principal": principal,
            "interest_rate": interest_rate,
            "bond_start_date": bond_start_date,
            "calculation_date": calculation_date,
            "expiry_date": expiry_date,
            "duration_years": duration_years,
            "duration_months": duration_months,
            "duration_days": duration_days,
            "monthly_interest": monthly_interest,
            "daily_interest": daily_interest,
            "complete_months": complete_months_total,
            "remaining_days": remaining_days,
            "interest": interest,
            "total_amount": total_amount,
            "bond_status": bond_status,
            "suggested_new_principal": suggested_new_principal,
        }

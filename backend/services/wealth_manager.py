from typing import Dict, List, Any

class WealthManagerService:
    def __init__(self):
        pass

    def calculate_sip_returns(self, monthly_investment: float, years: int, expected_return_rate: float = 12.0) -> Dict[str, Any]:
        """
        Calculates Future Value of SIP.
        Formula: FV = P * [ (1+i)^n - 1 ] * (1+i) / i
        """
        i = (expected_return_rate / 100) / 12
        n = years * 12
        
        fv = monthly_investment * ((((1 + i) ** n) - 1) * (1 + i)) / i
        total_invested = monthly_investment * n
        wealth_gained = fv - total_invested

        return {
            "monthly_investment": monthly_investment,
            "years": years,
            "rate": expected_return_rate,
            "total_invested": round(total_invested, 2),
            "wealth_gained": round(wealth_gained, 2),
            "maturity_value": round(fv, 2)
        }

    def analyze_debt_impact(self, principal: float, interest_rate: float, tenure_months: int) -> Dict[str, Any]:
        """
        Simple Loan Analysis (EMI).
        """
        # EMI = [P x R x (1+R)^N]/[(1+R)^N-1]
        r = interest_rate / (12 * 100)
        n = tenure_months
        
        if r == 0:
            emi = principal / n
        else:
            emi = (principal * r * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
            
        total_payment = emi * n
        total_interest = total_payment - principal

        return {
            "principal": principal,
            "interest_rate": interest_rate,
            "tenure_months": tenure_months,
            "emi": round(emi, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2)
        }

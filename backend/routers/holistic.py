from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.services.business_finance import BusinessFinanceService
from backend.services.wealth_manager import WealthManagerService

router = APIRouter(prefix="/api/holistic", tags=["Holistic Finance"])

business_service = BusinessFinanceService()
wealth_service = WealthManagerService()

# --- Models ---
class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float

class InvoiceRequest(BaseModel):
    client_name: str
    items: List[InvoiceItem]
    gst_rate: float = 18.0

class SIPRequest(BaseModel):
    monthly_investment: float
    years: int
    rate: float = 12.0

class DebtRequest(BaseModel):
    principal: float
    interest_rate: float
    tenure_months: int

# --- Endpoints ---

@router.post("/invoice/generate")
async def generate_invoice(request: InvoiceRequest):
    try:
        # Convert Pydantic models to dicts
        items_dict = [item.dict() for item in request.items]
        result = business_service.generate_invoice(request.client_name, items_dict, request.gst_rate)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gst/estimate")
async def estimate_gst(income: float, rate: float = 18.0):
    return business_service.estimate_gst_liability(income, rate)

@router.post("/wealth/sip")
async def calculate_sip(request: SIPRequest):
    return wealth_service.calculate_sip_returns(request.monthly_investment, request.years, request.rate)

@router.post("/wealth/debt")
async def analyze_debt(request: DebtRequest):
    return wealth_service.analyze_debt_impact(request.principal, request.interest_rate, request.tenure_months)

# backend/routers/invoices.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path
import uuid

from backend.services.invoice_service import InvoiceService

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

INVOICE_DIR = Path("invoices")
INVOICE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Helper: avoid global shared service
# ---------------------------------------------------------
def get_invoice_service():
    return InvoiceService()


# ---------------------------------------------------------
# Request Model
# ---------------------------------------------------------
class InvoiceData(BaseModel):
    txn_type: str = Field(..., description="Credited / Debited")
    amount: float = Field(..., description="Transaction amount")
    counterparty: str = Field(..., description="Merchant or source")
    date: str = Field(..., description="ISO date string")
    message: str = Field(..., description="Description or narration")
    category: str = Field(..., description="Expense category")


# ---------------------------------------------------------
# 1️⃣ Generate Invoice PDF
# ---------------------------------------------------------
@router.post("/generate")
async def generate_invoice_endpoint(data: InvoiceData):
    try:
        filename = f"invoice_{uuid.uuid4().hex[:10]}.pdf"
        filepath = INVOICE_DIR / filename

        invoice_service = get_invoice_service()

        invoice_service.generate_invoice_pdf(data.model_dump(), str(filepath))

        return {
            "success": True,
            "filename": filename,
            "download_url": f"/api/invoices/download/{filename}",
            "message": "Invoice generated successfully."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invoice generation failed: {str(e)}")


# ---------------------------------------------------------
# 2️⃣ Download Invoice
# ---------------------------------------------------------
@router.get("/download/{filename}")
async def download_invoice(filename: str):

    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    filepath = INVOICE_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Invoice not found")

    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=filename
    )

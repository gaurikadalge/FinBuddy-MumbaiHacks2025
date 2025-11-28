from datetime import datetime
from typing import Dict, List, Any

class BusinessFinanceService:
    def __init__(self):
        pass

    def generate_invoice(self, client_name: str, items: List[Dict[str, Any]], gst_rate: float = 18.0) -> Dict[str, Any]:
        """
        Generates invoice data structure.
        items: List of dicts with 'description', 'quantity', 'unit_price'
        """
        subtotal = 0
        invoice_items = []

        for item in items:
            total = item['quantity'] * item['unit_price']
            subtotal += total
            invoice_items.append({
                **item,
                'total': total
            })

        gst_amount = (subtotal * gst_rate) / 100
        grand_total = subtotal + gst_amount

        return {
            "invoice_number": f"INV-{int(datetime.now().timestamp())}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "client_name": client_name,
            "items": invoice_items,
            "subtotal": subtotal,
            "gst_rate": gst_rate,
            "gst_amount": gst_amount,
            "grand_total": grand_total
        }

    def estimate_gst_liability(self, total_income: float, gst_rate: float = 18.0) -> Dict[str, Any]:
        """
        Estimates GST liability based on total income.
        """
        # Assuming total_income includes GST
        # taxable_value = total_income / (1 + gst_rate/100)
        # gst_liability = total_income - taxable_value
        
        # If total_income is taxable value (exclusive of GST)
        gst_liability = (total_income * gst_rate) / 100
        
        return {
            "total_income": total_income,
            "gst_rate": gst_rate,
            "estimated_liability": gst_liability,
            "threshold_status": "Safe" if total_income < 2000000 else "Registration Required"
        }

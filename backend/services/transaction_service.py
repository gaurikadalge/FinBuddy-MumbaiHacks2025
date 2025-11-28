# backend/services/transaction_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from backend.core.database import get_transactions_collection
from backend.models.transaction import (
    Transaction,
    TransactionType
)
from backend.services.compliance_service import ComplianceService
from backend.utils.logger import logger

# IST timezone (UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def mongo_to_transaction(doc: Dict[str, Any]) -> Transaction:
    """
    Convert MongoDB document → Transaction Pydantic model.
    Handles missing fields, None values, and incorrect types (like lists).
    """
    doc = doc.copy()

    # Convert ObjectId to string
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]

    # Convert string dates to IST
    if isinstance(doc.get("date"), str):
        try:
            doc["date"] = datetime.fromisoformat(doc["date"].replace("Z", "+00:00"))
            # Convert to IST if timezone-aware
            if doc["date"].tzinfo:
                doc["date"] = doc["date"].astimezone(IST)
        except:
            doc["date"] = datetime.now(IST)
    
    # Helper function to ensure string (handles lists, None, etc.)
    def ensure_string(value, default=""):
        if value is None or value == "":
            return default
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            # If it's a list, take the first element if available
            return str(value[0]) if len(value) > 0 else default
        return str(value)
    
    # Fix all string fields
    doc["counterparty"] = ensure_string(doc.get("counterparty"), "Unknown")
    doc["message"] = ensure_string(doc.get("message"), "No description")
    doc["category"] = ensure_string(doc.get("category"), "general")
    doc["txn_type"] = ensure_string(doc.get("txn_type"), "Unknown")
    doc["ai_insight"] = ensure_string(doc.get("ai_insight"), "")
    doc["compliance_alert"] = ensure_string(doc.get("compliance_alert"), "")

    return Transaction(**doc)


class TransactionService:
    def __init__(self):
        self._collection = None
        self.compliance_service = ComplianceService()

    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_transactions_collection()
        return self._collection

    # ---------------------------------------------------------
    # CREATE TRANSACTION
    # ---------------------------------------------------------
    async def create_transaction(self, data: Dict[str, Any]) -> Transaction:
        """
        Data is a dictionary created by routers.
        """
        tx = data.copy()

        # Ensure date exists with IST timezone
        tx.setdefault("date", datetime.now(IST))

        # Compliance + AI insights
        ai_result = await self.compliance_service.analyze_transaction(tx)
        tx["ai_insight"] = ai_result.get("insight", "")
        tx["compliance_alert"] = ai_result.get("compliance_alert", "")

        # Insert into Mongo
        result = await self.collection.insert_one(tx)

        # Add DB _id → id
        tx["id"] = str(result.inserted_id)

        logger.info(f"Created transaction {tx['id']}")
        return Transaction.from_mongo(tx)

    # ---------------------------------------------------------
    # GET ALL TRANSACTIONS
    # ---------------------------------------------------------
    async def get_all_transactions(self) -> List[Transaction]:
        docs = await self.collection.find({}).sort("date", -1).to_list(None)
        return [mongo_to_transaction(doc) for doc in docs]

    # ---------------------------------------------------------
    # GET BY ID
    # ---------------------------------------------------------
    async def get_transaction_by_id(self, tx_id: str) -> Optional[Transaction]:
        try:
            obj_id = ObjectId(tx_id)
        except:
            return None

        doc = await self.collection.find_one({"_id": obj_id})
        return mongo_to_transaction(doc) if doc else None

    # ---------------------------------------------------------
    # UPDATE TRANSACTION
    # ---------------------------------------------------------
    async def update_transaction(self, tx_id: str, update_data: Dict[str, Any]) -> Optional[Transaction]:
        try:
            obj_id = ObjectId(tx_id)
        except:
            return None

        old_doc = await self.collection.find_one({"_id": obj_id})
        if not old_doc:
            return None

        # Normalize txn_type
        if "txn_type" in update_data:
            try:
                update_data["txn_type"] = TransactionType(update_data["txn_type"]).value
            except:
                update_data["txn_type"] = TransactionType.UNKNOWN.value

        # Merge old + new before compliance check
        merged = old_doc | update_data
        ai_update = await self.compliance_service.analyze_transaction(merged)

        update_data["ai_insight"] = ai_update.get("insight", "")
        update_data["compliance_alert"] = ai_update.get("compliance_alert", "")

        await self.collection.update_one({"_id": obj_id}, {"$set": update_data})

        new_doc = await self.collection.find_one({"_id": obj_id})
        return mongo_to_transaction(new_doc) if new_doc else None

    # ---------------------------------------------------------
    # DELETE TRANSACTION
    # ---------------------------------------------------------
    async def delete_transaction(self, tx_id: str) -> bool:
        try:
            obj_id = ObjectId(tx_id)
        except:
            return False

        result = await self.collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    async def get_transactions_summary(self) -> Dict[str, Any]:
        txs = await self.get_all_transactions()

        total_credit = sum(t.amount for t in txs if t.txn_type == TransactionType.CREDITED.value)
        total_debit = sum(t.amount for t in txs if t.txn_type == TransactionType.DEBITED.value)
        net_balance = total_credit - total_debit

        year = datetime.now(IST).year
        ytd_credit = sum(
            t.amount for t in txs
            if t.txn_type == TransactionType.CREDITED.value and t.date.year == year
        )

        latest_alert = next((t.compliance_alert for t in txs if t.compliance_alert), None)

        return {
            "total_transactions": len(txs),
            "total_credit": total_credit,
            "total_debit": total_debit,
            "net_balance": net_balance,
            "ytd_credit": ytd_credit,
            "latest_alert": latest_alert
        }

    # ---------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------------------------------------------------
    async def get_transactions_by_date_range(self, start: datetime, end: datetime) -> List[Transaction]:
        docs = await self.collection.find({
            "date": {"$gte": start, "$lte": end}
        }).to_list(None)

        return [mongo_to_transaction(doc) for doc in docs]

    async def get_transactions_by_category(self, category: str) -> List[Transaction]:
        docs = await self.collection.find({
            "category": {"$regex": f"^{category}$", "$options": "i"}
        }).to_list(None)

        return [mongo_to_transaction(doc) for doc in docs]

    async def search_transactions(self, query: str) -> List[Transaction]:
        docs = await self.collection.find({
            "$or": [
                {"counterparty": {"$regex": query, "$options": "i"}},
                {"message": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
            ]
        }).to_list(None)

        return [mongo_to_transaction(doc) for doc in docs]

    async def get_categories(self) -> List[str]:
        categories = await self.collection.distinct("category")
        return sorted([c for c in categories if isinstance(c, str)])
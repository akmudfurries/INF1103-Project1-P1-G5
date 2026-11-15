# Shared domain models for the AI Inventory & Procurement Advisor.

# These models keep application data independent of the CLI, business rules,
# AI provider, and persistence implementation.

from dataclasses import asdict, dataclass
from typing import Any
@dataclass
class InventoryRecord:
    # Represents one inventory item

    item_id: str
    item_name: str
    current_stock: int
    weekly_usage: float
    lead_time_weeks: int
    operational_notes: str
    category: str | None = None
    moq: int | None = None
    unit_cost: float | None = None
    budget: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the inventory record as a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InventoryRecord":
        """Create an inventory record from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("InventoryRecord.from_dict expects a dictionary.")

        allowed_fields = cls.__dataclass_fields__
        values = {
            field: value
            for field, value in data.items()
            if field in allowed_fields
        }
        return cls(**values)


@dataclass
class AIAssessment:
    # Stores the qualitative assessment returned by the AI component.

    demand_level: str
    demand_trend: str
    supply_risk: str
    operational_importance: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Return the AI assessment as a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AIAssessment":
        """Create an AI assessment from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("AIAssessment.from_dict expects a dictionary.")

        allowed_fields = cls.__dataclass_fields__
        values = {
            field: value
            for field, value in data.items()
            if field in allowed_fields
        }
        return cls(**values)


@dataclass
class ProcurementDecision:
    # Stores a procurement recommendation and its approval information.
    # The application controller can create a decision with procurement_id and
    # timestamp unset. DataManager/repository assigns those values when saving.

    item_id: str
    recommended_quantity: int
    priority: str
    action: str
    procurement_id: str | None = None
    approval_status: str = "PENDING"
    rejection_reason: str | None = None
    timestamp: str | None = None
    status_updated: str | None = None
    inventory_snapshot: dict[str, Any] | None = None
    ai_assessment: dict[str, Any] | None = None
    analysis_result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the procurement decision as a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProcurementDecision":
        """Create a procurement decision from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("ProcurementDecision.from_dict expects a dictionary.")

        allowed_fields = cls.__dataclass_fields__
        values = {
            field: value
            for field, value in data.items()
            if field in allowed_fields
        }
        return cls(**values)

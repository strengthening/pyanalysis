from typing import Optional, Dict, List, TypedDict

from pyanalysis.mail_templates.base import BaseTemplate

__all__ = ["StatusTemplate", "Step"]


class Step(TypedDict, total=False):
    """Step definition for StatusTemplate.

    Attributes:
        name: Step name/description.
        status: Step status ("pending", "in_progress", "completed").
    """
    name: str
    status: str  # "pending", "in_progress", "completed"


class StatusTemplate(BaseTemplate):
    """Status email template for progress updates.

    Suitable for: progress updates, status changes,
    approval workflows, etc.

    Args:
        title: Email title/heading.
        current_status: Current status text.
        previous_status: Optional previous status (shows status change).
        progress: Optional progress percentage (0-100).
        steps: Optional list of steps with status.
        eta: Optional estimated completion time.
        metadata: Optional dictionary of additional metadata.
        footer_text: Optional footer text.
        custom_styles: Optional additional inline CSS.
        locale: Language locale (default: "zh-CN").

    Example:
        template = StatusTemplate(
            title="Order Status Update",
            current_status="Shipped",
            previous_status="Processing",
            progress=75,
            steps=[
                {"name": "Order Placed", "status": "completed"},
                {"name": "Payment Confirmed", "status": "completed"},
                {"name": "Shipped", "status": "in_progress"},
                {"name": "Delivered", "status": "pending"},
            ],
            eta="2026-01-28",
            metadata={
                "Order ID": "ORD-12345",
                "Carrier": "Express Delivery",
            },
        )
        html = template.render()
    """

    _template_name = "status.html"

    def __init__(
        self,
        title: str,
        current_status: str,
        previous_status: Optional[str] = None,
        progress: Optional[int] = None,
        steps: Optional[List[Step]] = None,
        eta: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        footer_text: Optional[str] = None,
        custom_styles: Optional[str] = None,
        locale: str = "zh-CN",
    ):
        super().__init__(footer_text, custom_styles, locale)
        self._title = title
        self._current_status = current_status
        self._previous_status = previous_status
        self._progress = progress
        self._steps = steps
        self._eta = eta
        self._metadata = metadata

    def _get_template_context(self) -> dict:
        return {
            "title": self._title,
            "current_status": self._current_status,
            "previous_status": self._previous_status,
            "progress": self._progress,
            "steps": self._steps,
            "eta": self._eta,
            "metadata": self._metadata,
        }

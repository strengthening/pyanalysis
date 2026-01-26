from typing import Optional, Dict, List

from pyanalysis.templates.base import BaseTemplate

__all__ = ["AlertTemplate"]


class AlertTemplate(BaseTemplate):
    """Alert email template for exceptions and monitoring.

    Suitable for: exception alerts, monitoring notifications,
    service outages, etc.

    Args:
        title: Alert title/heading.
        message: Alert message describing the issue.
        severity: Alert severity level ("critical", "warning", "info").
        source: Optional source/origin of the alert.
        timestamp: Optional timestamp string.
        details: Optional dictionary of additional details.
        action_items: Optional list of recommended actions.
        footer_text: Optional footer text.
        custom_styles: Optional additional inline CSS.
        locale: Language locale (default: "zh-CN").

    Example:
        template = AlertTemplate(
            title="Service Exception Alert",
            message="Database connection timeout",
            severity="critical",
            source="order-service",
            timestamp="2026-01-26 10:30:00",
            details={
                "Server": "db-master-01",
                "Error Code": "ETIMEDOUT",
            },
            action_items=[
                "Check database server status",
                "Verify network connectivity",
            ],
        )
        html = template.render()
    """

    _template_name = "alert.html"

    SEVERITY_CRITICAL = "critical"
    SEVERITY_WARNING = "warning"
    SEVERITY_INFO = "info"

    def __init__(
        self,
        title: str,
        message: str,
        severity: str = "info",
        source: Optional[str] = None,
        timestamp: Optional[str] = None,
        details: Optional[Dict[str, str]] = None,
        action_items: Optional[List[str]] = None,
        footer_text: Optional[str] = None,
        custom_styles: Optional[str] = None,
        locale: str = "zh-CN",
    ):
        super().__init__(footer_text, custom_styles, locale)
        self._title = title
        self._message = message
        self._severity = severity
        self._source = source
        self._timestamp = timestamp
        self._details = details
        self._action_items = action_items

    def _get_template_context(self) -> dict:
        return {
            "title": self._title,
            "message": self._message,
            "severity": self._severity,
            "source": self._source,
            "timestamp": self._timestamp,
            "details": self._details,
            "action_items": self._action_items,
        }

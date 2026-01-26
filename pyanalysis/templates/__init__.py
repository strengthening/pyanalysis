"""Email template system for pyanalysis.mail.

This module provides Jinja2-based HTML email templates that are
compatible with all major email clients including Outlook.

Available Templates:
    - NotificationTemplate: System notifications, reminders, password resets
    - TableTemplate: Data reports, list displays, daily reports
    - AlertTemplate: Exception alerts, monitoring notifications
    - StatusTemplate: Progress updates, status changes, approval workflows

Example:
    from pyanalysis.mail import Mail
    from pyanalysis.templates import NotificationTemplate

    template = NotificationTemplate(
        title="Order Shipped",
        content="Your order has been shipped.",
        action_url="https://example.com/track",
        action_text="Track Order",
    )

    mail = Mail(username, password)
    mail.attach(template.to_html())
    mail.send("Order Update", ["customer@example.com"])
"""

from pyanalysis.templates.base import BaseTemplate
from pyanalysis.templates.notification import NotificationTemplate
from pyanalysis.templates.table import TableTemplate
from pyanalysis.templates.alert import AlertTemplate
from pyanalysis.templates.status import StatusTemplate, Step

__all__ = [
    "BaseTemplate",
    "NotificationTemplate",
    "TableTemplate",
    "AlertTemplate",
    "StatusTemplate",
    "Step",
]

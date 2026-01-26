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
    from pyanalysis.mail_templates import NotificationTemplate

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

from pyanalysis.mail_templates.base import BaseTemplate
from pyanalysis.mail_templates.notification import NotificationTemplate
from pyanalysis.mail_templates.table import TableTemplate
from pyanalysis.mail_templates.alert import AlertTemplate
from pyanalysis.mail_templates.status import StatusTemplate, Step

__all__ = [
    "BaseTemplate",
    "NotificationTemplate",
    "TableTemplate",
    "AlertTemplate",
    "StatusTemplate",
    "Step",
]

from typing import Optional

from pyanalysis.mail_templates.base import BaseTemplate

__all__ = ["NotificationTemplate"]


class NotificationTemplate(BaseTemplate):
    """Notification email template.

    Suitable for: system notifications, operation reminders,
    account activation, password reset, etc.

    Args:
        title: Email title/heading.
        content: Main content text.
        action_url: Optional URL for the action button.
        action_text: Optional text for the action button.
        subtitle: Optional subtitle text.
        icon: Optional icon type ("info", "success", "warning", "bell").
        footer_text: Optional footer text.
        custom_styles: Optional additional inline CSS.
        locale: Language locale (default: "zh-CN").

    Example:
        template = NotificationTemplate(
            title="Order Shipped",
            content="Your order has been shipped.",
            action_url="https://example.com/track",
            action_text="Track Order",
            icon="success"
        )
        html = template.render()
    """

    _template_name = "notification.html"

    def __init__(
        self,
        title: str,
        content: str,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        subtitle: Optional[str] = None,
        icon: Optional[str] = None,
        footer_text: Optional[str] = None,
        custom_styles: Optional[str] = None,
        locale: str = "zh-CN",
    ):
        super().__init__(footer_text, custom_styles, locale)
        self._title = title
        self._content = content
        self._action_url = action_url
        self._action_text = action_text
        self._subtitle = subtitle
        self._icon = icon

    def _get_template_context(self) -> dict:
        return {
            "title": self._title,
            "content": self._content,
            "action_url": self._action_url,
            "action_text": self._action_text,
            "subtitle": self._subtitle,
            "icon": self._icon,
        }

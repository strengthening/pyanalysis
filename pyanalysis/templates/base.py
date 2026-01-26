from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from pyanalysis.mail import HtmlContent
from pyanalysis.templates._styles import COLORS, STYLES, ICONS, FONT_FAMILY

__all__ = ["BaseTemplate"]

# Singleton Jinja2 environment (lazy loaded)
_jinja_env: Optional[Environment] = None


def _get_jinja_env() -> Environment:
    """Get or create the singleton Jinja2 environment."""
    global _jinja_env
    if _jinja_env is None:
        template_dir = Path(__file__).parent / "_html"
        _jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
    return _jinja_env


class BaseTemplate(ABC):
    """Abstract base class for email templates.

    Provides common functionality for rendering Jinja2 templates
    with shared styles and configuration.

    Args:
        footer_text: Optional footer text to display at bottom of email.
        custom_styles: Optional additional inline CSS styles.
        locale: Language locale code (default: "zh-CN").
    """

    # Subclasses must set this to their template filename
    _template_name: str = ""

    def __init__(
        self,
        footer_text: Optional[str] = None,
        custom_styles: Optional[str] = None,
        locale: str = "zh-CN",
    ):
        self._footer_text = footer_text
        self._custom_styles = custom_styles or ""
        self._locale = locale

    def _get_base_context(self) -> dict:
        """Get the base context shared by all templates."""
        return {
            "colors": COLORS,
            "styles": STYLES,
            "icons": ICONS,
            "font_family": FONT_FAMILY,
            "footer_text": self._footer_text,
            "custom_styles": self._custom_styles,
            "locale": self._locale,
        }

    @abstractmethod
    def _get_template_context(self) -> dict:
        """Get template-specific context variables.

        Subclasses must implement this to provide their own context.
        """
        pass

    def render(self) -> str:
        """Render the template to an HTML string.

        Returns:
            The rendered HTML string.
        """
        env = _get_jinja_env()
        template = env.get_template(self._template_name)

        context = self._get_base_context()
        context.update(self._get_template_context())

        return template.render(**context)

    def to_html(self) -> HtmlContent:
        """Render the template and wrap in HtmlContent.

        Returns:
            HtmlContent object that can be directly attached to Mail.

        Example:
            mail = Mail(username, password)
            mail.attach(template.to_html())
            mail.send("Subject", ["receiver@example.com"])
        """
        return HtmlContent(self.render())

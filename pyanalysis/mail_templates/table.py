from typing import Optional, List, Set, Dict, Any

from pyanalysis.mail_templates.base import BaseTemplate

__all__ = ["TableTemplate"]


class TableTemplate(BaseTemplate):
    """Table email template for data reports and lists.

    Suitable for: data reports, list displays, daily reports, etc.

    Args:
        title: Email title/heading.
        headers: List of column header names.
        rows: List of row data (each row is a list of cell values).
        summary: Optional summary text shown below the title.
        highlight_rows: Optional set of row indices to highlight (0-indexed).
        show_row_numbers: Whether to show row numbers (default: False).
        footer_text: Optional footer text.
        custom_styles: Optional additional inline CSS.
        locale: Language locale (default: "zh-CN").

    Example:
        template = TableTemplate(
            title="Daily Sales Report",
            headers=["Product", "Quantity", "Amount"],
            rows=[
                ["Product A", "10", "$1000"],
                ["Product B", "5", "$500"],
            ],
            summary="Total: $1500",
            highlight_rows={1},
        )
        html = template.render()
    """

    _template_name = "table.html"

    def __init__(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
        summary: Optional[str] = None,
        highlight_rows: Optional[Set[int]] = None,
        show_row_numbers: bool = False,
        footer_text: Optional[str] = None,
        custom_styles: Optional[str] = None,
        locale: str = "zh-CN",
    ):
        super().__init__(footer_text, custom_styles, locale)
        self._title = title
        self._headers = headers
        self._rows = rows
        self._summary = summary
        self._highlight_rows = highlight_rows or set()
        self._show_row_numbers = show_row_numbers

    def _get_template_context(self) -> dict:
        return {
            "title": self._title,
            "headers": self._headers,
            "rows": self._rows,
            "summary": self._summary,
            "highlight_rows": self._highlight_rows,
            "show_row_numbers": self._show_row_numbers,
        }

    @classmethod
    def from_dicts(
        cls,
        title: str,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None,
        summary: Optional[str] = None,
        highlight_rows: Optional[Set[int]] = None,
        show_row_numbers: bool = False,
        footer_text: Optional[str] = None,
        custom_styles: Optional[str] = None,
        locale: str = "zh-CN",
    ) -> "TableTemplate":
        """Create a TableTemplate from a list of dictionaries.

        Args:
            title: Email title/heading.
            data: List of dictionaries containing row data.
            columns: Optional list of column keys to include (in order).
                     If not specified, uses keys from the first dict.
            summary: Optional summary text.
            highlight_rows: Optional set of row indices to highlight.
            show_row_numbers: Whether to show row numbers.
            footer_text: Optional footer text.
            custom_styles: Optional additional inline CSS.
            locale: Language locale.

        Returns:
            A configured TableTemplate instance.

        Example:
            template = TableTemplate.from_dicts(
                title="User List",
                data=[
                    {"name": "Alice", "age": 25, "city": "NYC"},
                    {"name": "Bob", "age": 30, "city": "LA"},
                ],
                columns=["name", "city"],  # Only show these columns
            )
        """
        if not data:
            return cls(
                title=title,
                headers=[],
                rows=[],
                summary=summary,
                highlight_rows=highlight_rows,
                show_row_numbers=show_row_numbers,
                footer_text=footer_text,
                custom_styles=custom_styles,
                locale=locale,
            )

        if columns is None:
            columns = list(data[0].keys())

        headers = columns
        rows = [[str(row.get(col, "")) for col in columns] for row in data]

        return cls(
            title=title,
            headers=headers,
            rows=rows,
            summary=summary,
            highlight_rows=highlight_rows,
            show_row_numbers=show_row_numbers,
            footer_text=footer_text,
            custom_styles=custom_styles,
            locale=locale,
        )

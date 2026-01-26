import unittest

from pyanalysis.mail import HtmlContent
from pyanalysis.mail_templates import (
    BaseTemplate,
    NotificationTemplate,
    TableTemplate,
    AlertTemplate,
    StatusTemplate,
)


class TestNotificationTemplate(unittest.TestCase):
    """Test cases for NotificationTemplate."""

    def test_basic_render(self):
        """Test basic notification rendering."""
        template = NotificationTemplate(
            title="Test Title",
            content="Test content message.",
        )
        html = template.render()

        self.assertIn("Test Title", html)
        self.assertIn("Test content message.", html)
        self.assertIn("<!DOCTYPE html>", html)

    def test_with_action_button(self):
        """Test notification with action button."""
        template = NotificationTemplate(
            title="Action Required",
            content="Please click the button.",
            action_url="https://example.com/action",
            action_text="Click Here",
        )
        html = template.render()

        self.assertIn("https://example.com/action", html)
        self.assertIn("Click Here", html)

    def test_with_icon(self):
        """Test notification with different icons."""
        for icon in ["info", "success", "warning", "bell"]:
            template = NotificationTemplate(
                title="Icon Test",
                content="Testing icon.",
                icon=icon,
            )
            html = template.render()
            self.assertIn("<svg", html)

    def test_with_subtitle(self):
        """Test notification with subtitle."""
        template = NotificationTemplate(
            title="Main Title",
            content="Content here.",
            subtitle="Subtitle text",
        )
        html = template.render()

        self.assertIn("Subtitle text", html)

    def test_to_html_returns_html_content(self):
        """Test that to_html returns HtmlContent instance."""
        template = NotificationTemplate(
            title="Test",
            content="Test content.",
        )
        result = template.to_html()

        self.assertIsInstance(result, HtmlContent)

    def test_with_footer(self):
        """Test notification with footer text."""
        template = NotificationTemplate(
            title="Test",
            content="Content",
            footer_text="Footer message here",
        )
        html = template.render()

        self.assertIn("Footer message here", html)

    def test_locale_setting(self):
        """Test locale is set in HTML."""
        template = NotificationTemplate(
            title="Test",
            content="Content",
            locale="en-US",
        )
        html = template.render()

        self.assertIn('lang="en-US"', html)


class TestTableTemplate(unittest.TestCase):
    """Test cases for TableTemplate."""

    def test_basic_render(self):
        """Test basic table rendering."""
        template = TableTemplate(
            title="Sales Report",
            headers=["Product", "Quantity", "Amount"],
            rows=[
                ["Product A", "10", "$100"],
                ["Product B", "5", "$50"],
            ],
        )
        html = template.render()

        self.assertIn("Sales Report", html)
        self.assertIn("Product", html)
        self.assertIn("Quantity", html)
        self.assertIn("Amount", html)
        self.assertIn("Product A", html)
        self.assertIn("$100", html)

    def test_with_summary(self):
        """Test table with summary text."""
        template = TableTemplate(
            title="Report",
            headers=["Col1", "Col2"],
            rows=[["a", "b"]],
            summary="Total: $150",
        )
        html = template.render()

        self.assertIn("Total: $150", html)

    def test_with_row_numbers(self):
        """Test table with row numbers enabled."""
        template = TableTemplate(
            title="Report",
            headers=["Name"],
            rows=[["Alice"], ["Bob"]],
            show_row_numbers=True,
        )
        html = template.render()

        self.assertIn("#", html)

    def test_from_dicts(self):
        """Test creating table from list of dictionaries."""
        data = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        template = TableTemplate.from_dicts(
            title="User List",
            data=data,
        )
        html = template.render()

        self.assertIn("User List", html)
        self.assertIn("name", html)
        self.assertIn("Alice", html)
        self.assertIn("Bob", html)

    def test_from_dicts_with_columns(self):
        """Test from_dicts with specific columns."""
        data = [
            {"name": "Alice", "age": "25", "city": "NYC"},
            {"name": "Bob", "age": "30", "city": "LA"},
        ]
        template = TableTemplate.from_dicts(
            title="Filtered",
            data=data,
            columns=["name", "city"],
        )
        html = template.render()

        self.assertIn("name", html)
        self.assertIn("city", html)
        # age should not be rendered as header
        self.assertNotIn(">age<", html)

    def test_from_dicts_empty_data(self):
        """Test from_dicts with empty data list."""
        template = TableTemplate.from_dicts(
            title="Empty",
            data=[],
        )
        html = template.render()

        self.assertIn("Empty", html)

    def test_highlight_rows(self):
        """Test row highlighting."""
        template = TableTemplate(
            title="Report",
            headers=["Name"],
            rows=[["Alice"], ["Bob"], ["Charlie"]],
            highlight_rows={1},
        )
        html = template.render()
        # Highlight color should be present
        self.assertIn("#fffbe6", html)


class TestAlertTemplate(unittest.TestCase):
    """Test cases for AlertTemplate."""

    def test_basic_render(self):
        """Test basic alert rendering."""
        template = AlertTemplate(
            title="Alert Title",
            message="Something went wrong.",
        )
        html = template.render()

        self.assertIn("Alert Title", html)
        self.assertIn("Something went wrong.", html)

    def test_severity_levels(self):
        """Test different severity levels."""
        for severity in ["critical", "warning", "info"]:
            template = AlertTemplate(
                title="Test Alert",
                message="Test message",
                severity=severity,
            )
            html = template.render()
            self.assertIn("<svg", html)

    def test_with_source_and_timestamp(self):
        """Test alert with source and timestamp."""
        template = AlertTemplate(
            title="Error",
            message="Connection failed",
            source="api-server",
            timestamp="2026-01-26 10:30:00",
        )
        html = template.render()

        self.assertIn("api-server", html)
        self.assertIn("2026-01-26 10:30:00", html)

    def test_with_details(self):
        """Test alert with details dictionary."""
        template = AlertTemplate(
            title="Error",
            message="Database error",
            details={
                "Server": "db-master",
                "Error Code": "ETIMEDOUT",
            },
        )
        html = template.render()

        self.assertIn("Server", html)
        self.assertIn("db-master", html)
        self.assertIn("Error Code", html)
        self.assertIn("ETIMEDOUT", html)

    def test_with_action_items(self):
        """Test alert with action items."""
        template = AlertTemplate(
            title="Alert",
            message="Issue detected",
            action_items=[
                "Check server status",
                "Review logs",
                "Contact support",
            ],
        )
        html = template.render()

        self.assertIn("Check server status", html)
        self.assertIn("Review logs", html)
        self.assertIn("Contact support", html)

    def test_critical_severity_colors(self):
        """Test critical severity uses correct colors."""
        template = AlertTemplate(
            title="Critical",
            message="System down",
            severity="critical",
        )
        html = template.render()

        # Critical background color
        self.assertIn("#fff2f0", html)


class TestStatusTemplate(unittest.TestCase):
    """Test cases for StatusTemplate."""

    def test_basic_render(self):
        """Test basic status rendering."""
        template = StatusTemplate(
            title="Status Update",
            current_status="Active",
        )
        html = template.render()

        self.assertIn("Status Update", html)
        self.assertIn("Active", html)

    def test_with_status_change(self):
        """Test status with previous status."""
        template = StatusTemplate(
            title="Status Change",
            current_status="Approved",
            previous_status="Pending",
        )
        html = template.render()

        self.assertIn("Approved", html)
        self.assertIn("Pending", html)
        self.assertIn("→", html)

    def test_with_progress(self):
        """Test status with progress bar."""
        template = StatusTemplate(
            title="Progress",
            current_status="In Progress",
            progress=75,
        )
        html = template.render()

        self.assertIn("75%", html)

    def test_with_steps(self):
        """Test status with steps."""
        template = StatusTemplate(
            title="Workflow",
            current_status="Step 2",
            steps=[
                {"name": "Step 1", "status": "completed"},
                {"name": "Step 2", "status": "in_progress"},
                {"name": "Step 3", "status": "pending"},
            ],
        )
        html = template.render()

        self.assertIn("Step 1", html)
        self.assertIn("Step 2", html)
        self.assertIn("Step 3", html)

    def test_with_eta(self):
        """Test status with ETA."""
        template = StatusTemplate(
            title="Task",
            current_status="Running",
            eta="2026-01-30 15:00",
        )
        html = template.render()

        self.assertIn("2026-01-30 15:00", html)

    def test_with_metadata(self):
        """Test status with metadata."""
        template = StatusTemplate(
            title="Order Status",
            current_status="Shipped",
            metadata={
                "Order ID": "ORD-12345",
                "Carrier": "Express",
            },
        )
        html = template.render()

        self.assertIn("Order ID", html)
        self.assertIn("ORD-12345", html)
        self.assertIn("Carrier", html)
        self.assertIn("Express", html)

    def test_zero_progress(self):
        """Test progress bar with 0%."""
        template = StatusTemplate(
            title="Starting",
            current_status="Initializing",
            progress=0,
        )
        html = template.render()

        self.assertIn("0%", html)


class TestBaseTemplate(unittest.TestCase):
    """Test cases for BaseTemplate abstract class."""

    def test_cannot_instantiate_directly(self):
        """Test that BaseTemplate cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseTemplate()

    def test_custom_styles(self):
        """Test custom styles are applied."""
        template = NotificationTemplate(
            title="Test",
            content="Content",
            custom_styles=" color: red;",
        )
        html = template.render()

        self.assertIn("color: red;", html)


if __name__ == "__main__":
    unittest.main()

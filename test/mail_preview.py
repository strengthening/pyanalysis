#!/usr/bin/env python3
"""Generate HTML preview files for email templates.

Usage:
    python test/mail_preview.py

Output files will be saved to test/mail_preview/
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyanalysis.mail_templates import (
    NotificationTemplate,
    TableTemplate,
    AlertTemplate,
    StatusTemplate,
)


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "mail_preview")
    os.makedirs(output_dir, exist_ok=True)

    # 1. 通知模板
    notification = NotificationTemplate(
        title="订单发货通知",
        content="您的订单已发货，预计3天内送达。感谢您的购买！",
        action_url="https://example.com/track",
        action_text="查看物流",
        subtitle="订单号: ORD-2026012700001",
        icon="success",
        footer_text="如有疑问，请联系客服 400-123-4567",
    )
    with open(os.path.join(output_dir, "notification.html"), "w") as f:
        f.write(notification.render())

    # 2. 表格模板
    table = TableTemplate(
        title="今日销售报表",
        headers=["商品名称", "销售数量", "单价", "金额"],
        rows=[
            ["iPhone 15 Pro", "10", "¥8,999", "¥89,990"],
            ["MacBook Air", "5", "¥9,499", "¥47,495"],
            ["AirPods Pro", "20", "¥1,899", "¥37,980"],
            ["Apple Watch", "8", "¥3,299", "¥26,392"],
        ],
        summary="合计销售额: ¥201,857",
        highlight_rows={0},
        show_row_numbers=True,
        footer_text="数据统计时间: 2026-01-27 18:00",
    )
    with open(os.path.join(output_dir, "table.html"), "w") as f:
        f.write(table.render())

    # 3. 告警模板
    alert = AlertTemplate(
        title="数据库连接异常告警",
        message="检测到数据库连接池耗尽，部分请求无法处理。",
        severity="critical",
        source="order-service-prod-01",
        timestamp="2026-01-27 14:32:15",
        details={
            "服务器": "db-master-01.prod",
            "错误码": "ETIMEDOUT",
            "连接池大小": "100",
            "当前连接数": "100",
            "等待队列": "256",
        },
        action_items=[
            "检查数据库服务器负载状态",
            "确认是否有慢查询占用连接",
            "考虑临时扩大连接池大小",
            "联系 DBA 进行进一步排查",
        ],
        footer_text="此告警由监控系统自动发送",
    )
    with open(os.path.join(output_dir, "alert.html"), "w") as f:
        f.write(alert.render())

    # 4. 状态模板
    status = StatusTemplate(
        title="订单状态更新",
        current_status="配送中",
        previous_status="已发货",
        progress=75,
        steps=[
            {"name": "订单已提交", "status": "completed"},
            {"name": "支付成功", "status": "completed"},
            {"name": "商家发货", "status": "completed"},
            {"name": "配送中", "status": "in_progress"},
            {"name": "已签收", "status": "pending"},
        ],
        eta="2026-01-29 18:00",
        metadata={
            "订单号": "ORD-2026012700001",
            "快递公司": "顺丰速运",
            "快递单号": "SF1234567890",
            "收货地址": "北京市朝阳区xxx街道xxx号",
        },
        footer_text="如有疑问，请联系客服",
    )
    with open(os.path.join(output_dir, "status.html"), "w") as f:
        f.write(status.render())

    print(f"已生成 4 个预览文件到: {output_dir}")
    for filename in ["notification.html", "table.html", "alert.html", "status.html"]:
        print(f"  - {filename}")


if __name__ == "__main__":
    main()

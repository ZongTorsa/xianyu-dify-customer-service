"""闲鱼未读消息监听与自动回复流程。"""

from __future__ import annotations

import re

from playwright.sync_api import Playwright, sync_playwright

from .dify import get_dify_reply
from .settings import PROFILE_DIR


XIANYU_URL = "https://www.goofish.com/"
MESSAGE_LINK_NAME = "消息"
CHAT_BOX_NAME = "请输入消息，按Enter键发送或点击发送按钮发送"
SEND_BUTTON_NAME = "发 送"


def extract_message_text(row_text: str) -> str:
    """去掉消息行的第一行发送者名称，只保留消息正文。"""
    lines = [line.strip() for line in row_text.splitlines() if line.strip()]
    return "\n".join(lines[1:]) if len(lines) > 1 else ""


def read_latest_messages(page, unread_count: int) -> list[str]:
    """读取当前聊天窗口最后 unread_count 条文字消息。"""
    message_list = page.get_by_role("list").last
    message_list.wait_for(state="visible", timeout=10_000)
    message_rows = message_list.locator(":scope > *")
    row_count = message_rows.count()
    rows_to_read = min(unread_count, row_count)

    messages: list[str] = []
    for index in range(row_count - rows_to_read, row_count):
        message = extract_message_text(message_rows.nth(index).inner_text())
        if message:
            messages.append(message)
    return messages


def run(playwright: Playwright) -> None:
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR), channel="chrome", headless=False
    )
    try:
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(XIANYU_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3_000)

        with page.expect_popup() as message_page_info:
            page.get_by_role("link", name=MESSAGE_LINK_NAME).click()

        message_page = message_page_info.value
        message_page.wait_for_load_state("domcontentloaded")
        message_page.wait_for_timeout(2_000)
        number_title = re.compile(r"^\d+$")

        while True:
            titles = message_page.get_by_title(number_title)
            if titles.count() <= 1:
                print("\n暂无用户未读消息，10 秒后重新检查...")
                message_page.wait_for_timeout(10_000)
                message_page.reload(wait_until="domcontentloaded")
                message_page.wait_for_timeout(1_500)
                continue

            first_unread_user = titles.nth(1)
            unread_text = first_unread_user.get_attribute("title")
            if not unread_text or not unread_text.isdigit():
                print("\n无法读取当前用户的未读数量，停止处理。")
                break

            unread_count = int(unread_text)
            print(f"\n当前用户未读消息数量：{unread_count}")
            first_unread_user.click()
            message_page.wait_for_timeout(1_500)

            messages = read_latest_messages(message_page, unread_count)
            print(f"读取到 {len(messages)} 条消息：")
            for index, message in enumerate(messages, start=1):
                print(f"\n--- 第 {index} 条 ---\n{message}")

            reply = get_dify_reply(messages)
            if reply is None:
                print("本轮未获得 Dify 回复，跳过回复处理。")
            else:
                print(f"\n===== Dify 回复 =====\n{reply}")
                chat_box = message_page.get_by_role("textbox", name=CHAT_BOX_NAME)
                chat_box.fill(reply)
                message_page.get_by_role("button", name=SEND_BUTTON_NAME).click()
                print("Dify 回复已发送给客户。")
                message_page.wait_for_timeout(1_000)

            message_page.reload(wait_until="domcontentloaded")
            message_page.wait_for_timeout(1_500)
    finally:
        context.close()


def main() -> None:
    with sync_playwright() as playwright:
        run(playwright)

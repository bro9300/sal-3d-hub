#!/usr/bin/env python3
"""
Модуль обробки та перевірки платежів Monobank для 3D-магазину Степанського ліцею
Розроблено для автоматичного контролю надходження коштів у Банку Monobank
та сповіщення адміністраторів через Telegram-бота.

Можливості:
1. Генерація прямих платіжних посилань на Банку з параметрами суми (a=) та коментаря (text=).
2. Перевірка виписки Monobank API (/personal/statement) на наявність зарахування із номером замовлення.
3. Автоматична відправка сповіщення «ОПЛАТУ ОТРИМАНО» у Telegram-чат ліцею.
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

MONOBANK_API_URL = "https://api.monobank.ua"

class MonobankPaymentHandler:
    def __init__(self, jar_link=None, token=None, tg_bot_token=None, tg_chat_id=None):
        self.jar_link = jar_link or "https://send.monobank.ua/jar/89mXHukogN"
        self.token = token or os.environ.get("MONOBANK_TOKEN", "")
        self.tg_bot_token = tg_bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.tg_chat_id = tg_chat_id or os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "")

    def generate_jar_payment_url(self, order_number, amount_uah, customer_name=""):
        """
        Генерує персональне посилання на банку Monobank
        """
        clean_base = self.jar_link.split("?")[0]
        comment = f"{order_number} {customer_name}".strip()
        params = {
            "a": int(amount_uah),
            "text": comment
        }
        query_string = urllib.parse.urlencode(params)
        return f"{clean_base}?{query_string}"

    def check_statement(self, account_id="0", hours=2):
        """
        Перевірка виписки рахунку/банки через Monobank Open API за останні години
        (Потрібен токен із api.monobank.ua)
        """
        if not self.token:
            print("[!] Monobank Token не вказано. Працює у режимі прямої оплати на Банку.")
            return []

        time_from = int((datetime.now() - timedelta(hours=hours)).timestamp())
        url = f"{MONOBANK_API_URL}/personal/statement/{account_id}/{time_from}"
        headers = {"X-Token": self.token}

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except Exception as e:
            print(f"[!] Помилка запиту до Monobank API: {e}")
            return []

    def verify_order_payment(self, order_number, expected_amount_uah, account_id="0"):
        """
        Шукає платіж у виписці за номером замовлення та сумою
        """
        statements = self.check_statement(account_id=account_id)
        expected_cents = int(expected_amount_uah * 100)

        for tx in statements:
            comment = tx.get("comment", "") or tx.get("description", "")
            amount = tx.get("amount", 0)  # у копійках, позитивне для поповнення

            if order_number in comment and amount >= expected_cents:
                return {
                    "paid": True,
                    "tx_id": tx.get("id"),
                    "amount_uah": amount / 100,
                    "time": datetime.fromtimestamp(tx.get("time", 0)).strftime("%d.%m.%Y %H:%M"),
                    "description": comment
                }

        return {"paid": False}

    def notify_payment_received(self, order_number, amount_uah, customer_name=""):
        """
        Надсилає повідомлення про підтвердження оплати у Telegram-чат
        """
        if not self.tg_bot_token or not self.tg_chat_id:
            return False

        text = (
            f"✅ <b>ОПЛАТУ НА БАНКУ MONOBANK ОТРИМАНО!</b>\\n"
            f"━━━━━━━━━━━━━━━━━━━━\\n"
            f"📦 <b>Замовлення:</b> {order_number}\\n"
            f"👤 <b>Клієнт:</b> {customer_name}\\n"
            f"💰 <b>Сума:</b> {amount_uah} ₴\\n"
            f"🕒 <b>Час зарахування:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}\\n"
            f"━━━━━━━━━━━━━━━━━━━━\\n"
            f"<i>Замовлення готове до друку в STEM-майстерні!</i>"
        )

        url = f"https://api.telegram.org/bot{self.tg_bot_token}/sendMessage"
        payload = json.dumps({
            "chat_id": self.tg_chat_id,
            "text": text,
            "parse_mode": "HTML"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("ok", False)
        except Exception as e:
            print(f"[!] Помилка відправлення в Telegram: {e}")
            return False

def main():
    print("=== Monobank Payment Handler для STEM-хабу САЛ ===")
    handler = MonobankPaymentHandler()
    test_url = handler.generate_jar_payment_url("#STL-3021", 215, "Олена Мельник")
    print(f"[+] Згенероване тестове посилання на Банку: {test_url}")

if __name__ == "__main__":
    main()

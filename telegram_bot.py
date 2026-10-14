#!/usr/bin/env python3
"""
Telegram-бот для 3D-магазину Степанського академічного ліцею
Розроблено для прийому замовлень на 3D-друк та підтримки ЗСУ 🇺🇦

Працює на стандартній бібліотеці Python 3 (urllib) — жодних сторонніх pip-пакетів не потрібно!
Запуск:
    python3 telegram_bot.py --token "ВАШ_ТОКЕН" --chat "ВАШ_CHAT_ID"
або вкажіть змінні середовища:
    export TELEGRAM_BOT_TOKEN="ВАШ_ТОКЕН"
    export TELEGRAM_ADMIN_CHAT_ID="ВАШ_CHAT_ID"
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import argparse
from datetime import datetime

DEFAULT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DEFAULT_ADMIN_CHAT = os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "")
ORDERS_FILE = "orders_db.json"

CATALOG_SUMMARY = """
🏰 <b>КАТАЛОГ 3D-ВИРОБІВ СТЕПАНСЬКОГО ЛІЦЕЮ:</b>

🔑 <b>Брелоки та аксесуари:</b>
• Фірмовий брелок «Степанський ліцей» — 60 ₴
• Іменний брелок «Your Text» (автор: Д. Кривульський) — 70 ₴
• Чохол-кліпса для учнівського квитка САЛ — 50 ₴

📱 <b>Органайзери та підставки:</b>
• Підставка для ручок «Молот Тора» — 190 ₴
• Підвіс для навушників зі струбциною (автор: Б. Чунківський) — 160 ₴
• Телескопічна регульована підставка (автор: Б. Чунківський) — 180 ₴
• Гребінчаста підставка під смартфон (автор: Б. Чунківський) — 130 ₴
• Компактна підставка для телефона (автор: Д. Кривульський) — 90 ₴
• Органайзер канцелярії «Степанська Вежа» — 190 ₴
• Підставка «Степань STEM» — 140 ₴

🚁 <b>Деталі FPV та дронів (Допомога ЗСУ):</b>
• Захист стеку FPV з Гербом України (автор: Б. Чунківський) — 95 ₴
• Кріплення GoPro для FPV дронів (автор: Б. Чунківський) — 110 ₴
• Захист кінців променів рами Geprc Mark4 (4 шт.) — 85 ₴
• Хвостовик-тримач антени 45° — 75 ₴
• Хвостовик FPV з підтримкою GPS — 95 ₴

🏰 <b>Сувеніри та мініатюри:</b>
• Фігурка кухаря Ремі («Рататуй») — 140 ₴
• Фігурка панди з бамбуком — 150 ₴
• Декоративна пташка з візерунком — 120 ₴
• Космічний корабель «Star Wars» з підставкою — 240 ₴
• Військовий літак-штурмовик (автор: Д. Кривульський) — 210 ₴
• Лицарський меч «Степанська доблесть» — 230 ₴
• Макет «Степанський замок Острозьких XVI ст.» — 260 ₴
• Сувенірний Тризуб України 3D — 120 ₴

🏺 <b>Декор та побут:</b>
• Спіральна дизайнерська ваза «Wave Decor» — 220 ₴
• Органайзер зубних щіток та пасти — 120 ₴
• Миска для домашніх тварин (автор: Д. Кривульський) — 110 ₴
• Золота каблучка «Спіраль» (Silk Gold) — 75 ₴

🧩 <b>Антистрес:</b>
• Гнучкий антистрес «Горинь-Dragon Flexi» — 180 ₴
• Кубик-трансформер Infinity — 150 ₴
"""

class TelegramBot:
    def __init__(self, token, admin_chat_id=None):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}/"
        self.admin_chat_id = admin_chat_id
        self.offset = 0
        self.load_orders()

    def load_orders(self):
        if os.path.exists(ORDERS_FILE):
            try:
                with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                    self.orders = json.load(f)
            except Exception:
                self.orders = []
        else:
            self.orders = []

    def save_order(self, order_data):
        self.orders.append(order_data)
        try:
            with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.orders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Помилка запису в {ORDERS_FILE}: {e}")

    def call_api(self, method, data=None):
        url = self.base_url + method
        headers = {"Content-Type": "application/json"}
        req_data = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            print(f"HTTPError [{e.code}]: {err_body}")
            return {"ok": False, "error": err_body}
        except Exception as e:
            print(f"API Request Exception: {e}")
            return {"ok": False, "error": str(e)}

    def send_message(self, chat_id, text, reply_markup=None, parse_mode="HTML"):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.call_api("sendMessage", payload)

    def notify_admin(self, order_text):
        if self.admin_chat_id:
            return self.send_message(self.admin_chat_id, order_text)
        return False

    def handle_update(self, update):
        if "message" in update:
            msg = update["message"]
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "").strip()
            user = msg.get("from", {})
            user_name = user.get("first_name", "Друже")

            if text.startswith("/start"):
                self.cmd_start(chat_id, user_name)
            elif text.startswith("/catalog") or "каталог" in text.lower():
                self.cmd_catalog(chat_id)
            elif text.startswith("/fpv") or "дрон" in text.lower():
                self.cmd_fpv(chat_id)
            elif text.startswith("/order") or "замов" in text.lower():
                self.cmd_order_help(chat_id)
            elif text.startswith("/help") or "допомога" in text.lower():
                self.cmd_help(chat_id)
            elif text.startswith("/orders_list") and str(chat_id) == str(self.admin_chat_id):
                self.cmd_admin_orders(chat_id)
            else:
                reply = (
                    f"Дякуємо за повідомлення, {user_name}!\n\n"
                    "Для перегляду асортименту надішліть /catalog або скористайтесь меню нижче."
                )
                self.send_message(chat_id, reply, reply_markup=self.get_main_keyboard())

        elif "callback_query" in update:
            cb = update["callback_query"]
            data = cb.get("data")
            chat_id = cb.get("message", {}).get("chat", {}).get("id")
            cb_id = cb.get("id")
            self.call_api("answerCallbackQuery", {"callback_query_id": cb_id})

            if data == "cb_catalog":
                self.cmd_catalog(chat_id)
            elif data == "cb_fpv":
                self.cmd_fpv(chat_id)
            elif data == "cb_order":
                self.cmd_order_help(chat_id)
            elif data == "cb_about":
                self.cmd_about(chat_id)

    def get_main_keyboard(self):
        return {
            "inline_keyboard": [
                [
                    {"text": "🛍 Каталог 3D-виробів", "callback_data": "cb_catalog"},
                    {"text": "🚁 Дрони FPV для ЗСУ", "callback_data": "cb_fpv"}
                ],
                [
                    {"text": "📦 Як зробити замовлення", "callback_data": "cb_order"},
                    {"text": "🏫 Про STEM-хаб", "callback_data": "cb_about"}
                ]
            ]
        }

    def cmd_start(self, chat_id, user_name):
        text = (
            f"👋 <b>Вітаємо у 3D Shop Степанського академічного ліцею, {user_name}!</b>\n\n"
            "Тут ви можете замовити фірмовий мерч, корисні органайзери, сувеніри "
            "та комплектуючі для FPV-дронів, спроєктовані та надруковані ліцеїстами.\n\n"
            "🇺🇦 <b>Кошти йдуть на закупівлю пластику та допомогу ЗСУ!</b>\n\n"
            "Оберіть пункт меню нижче:"
        )
        self.send_message(chat_id, text, reply_markup=self.get_main_keyboard())

    def cmd_catalog(self, chat_id):
        self.send_message(chat_id, CATALOG_SUMMARY, reply_markup=self.get_main_keyboard())

    def cmd_fpv(self, chat_id):
        text = (
            "🚁 <b>ДЕТАЛІ ДЛЯ FPV ДРОНІВ ТА ПІДТРИМКА ЗСУ:</b>\n\n"
            "Учні нашого ліцею (зокрема Богдан Чунківський) розробляють та виготовляють "
            "критично важливі вузли для волонтерських та військових дронів:\n"
            "• <b>Захист стеку польотного контролера з Гербом України</b> (95 ₴)\n"
            "• <b>Кріплення екшн-камер GoPro</b> під рами 5″ та 7″ (110 ₴)\n"
            "• <b>Захист променів рами Geprc Mark4</b> (комплект 4 шт. — 85 ₴)\n"
            "• <b>Хвостовики антен Soft-Mount 45°</b> (75 ₴)\n"
            "• <b>Подовжені тримачі GPS-модулів BN-180/BN-220</b> (95 ₴)\n\n"
            "Всі вироби друкуються з ударостійкого термостійкого філаменту та протестовані на надійність."
        )
        self.send_message(chat_id, text, reply_markup=self.get_main_keyboard())

    def cmd_order_help(self, chat_id):
        text = (
            "📦 <b>ЯК ЗРОБИТИ ЗАМОВЛЕННЯ:</b>\n\n"
            "1. Відкрийте наш веб-сайт магазину, оберіть потрібні моделі та кольори пластику.\n"
            "2. Перейдіть до кошика та заповніть форму оформлення.\n"
            "3. Сайт автоматично надішле ваше замовлення у наш Telegram-бот!\n\n"
            "Також ви можете надіслати замовлення прямо сюди в чат у форматі:\n"
            "<code>ПІБ: Олена Мельник\n"
            "Клас/статус: 9-А\n"
            "Телефон: +380970000000\n"
            "Товари: 1 шт. Брелок ліцею (синій), 1 шт. Підставка «Тора»</code>"
        )
        self.send_message(chat_id, text, reply_markup=self.get_main_keyboard())

    def cmd_about(self, chat_id):
        text = (
            "🏫 <b>ПРО МЕЙКЕРСЬКИЙ STEM-ХАБ:</b>\n\n"
            "📍 Степанський академічний ліцей, смт Степань, Рівненська область.\n\n"
            "Наші ліцеїсти на уроках інформатики та робототехніки самостійно моделюють "
            "вироби у Tinkercad, Blender та FreeCAD, готують слайси та друкують на 3D-принтерах.\n"
            "Використовуємо екологічний та безпечний PLA-пластик з кукурудзяного крохмалю.

💻 <b>Fullstack розробка та UI:</b> Роман Берник (@bro9301)."
        )
        self.send_message(chat_id, text, reply_markup=self.get_main_keyboard())

    def cmd_help(self, chat_id):
        text = (
            "📋 <b>ДОСТУПНІ КОМАНДИ:</b>\n"
            "/start — Головне меню\n"
            "/catalog — Переглянути каталог із цінами\n"
            "/fpv — Розділ виробів для FPV-дронів та ЗСУ\n"
            "/order — Інструкція із замовлення\n"
            "/help — Довідка"
        )
        self.send_message(chat_id, text, reply_markup=self.get_main_keyboard())

    def cmd_admin_orders(self, chat_id):
        if not self.orders:
            self.send_message(chat_id, "База замовлень наразі порожня.")
            return
        last_orders = self.orders[-5:]
        res = "📋 <b>ОСТАННІ ЗАМОВЛЕННЯ:</b>\n\n"
        for o in reversed(last_orders):
            res += f"• <b>{o.get('number', 'N/A')}</b> від {o.get('date', 'N/A')}\n"
            res += f"  Клієнт: {o.get('fullname', 'N/A')} ({o.get('phone', 'N/A')})\n"
            res += f"  Сума: {o.get('total', 'N/A')}\n\n"
        self.send_message(chat_id, res)

    def run_polling(self):
        print(f"[*] Telegram-бот запущено! Очікування повідомлень...")
        print(f"[*] Токен: {self.token[:8]}...{self.token[-4:] if len(self.token) > 12 else ''}")
        if self.admin_chat_id:
            print(f"[*] Admin Chat ID: {self.admin_chat_id}")
            self.send_message(self.admin_chat_id, "🤖 Telegram-бот 3D-магазину ліцею успішно запущено онлайн!")

        while True:
            try:
                updates = self.call_api("getUpdates", {"offset": self.offset, "timeout": 20})
                if updates.get("ok"):
                    for u in updates.get("result", []):
                        self.offset = u["update_id"] + 1
                        self.handle_update(u)
                else:
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\n[!] Бот зупинений користувачем.")
                break
            except Exception as e:
                print(f"[!] Помилка polling: {e}")
                time.sleep(3)

def main():
    parser = argparse.ArgumentParser(description="Telegram Bot для 3D Shop Степанського ліцею")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Telegram Bot Token від @BotFather")
    parser.add_argument("--chat", default=DEFAULT_ADMIN_CHAT, help="ID чату або групи для замовлень")
    args = parser.parse_args()

    token = args.token.strip()
    if not token:
        print("[!] УВАГА: Токен бота не вказано.")
        print("Вкажіть токен через аргумент --token або змінну оточення TELEGRAM_BOT_TOKEN.")
        print("Приклад: python3 telegram_bot.py --token '123456789:ABC...' --chat '-100123456789'")
        token = input("Введіть токен бота (або Enter для виходу): ").strip()
        if not token:
            sys.exit(1)

    bot = TelegramBot(token, args.chat.strip() if args.chat else None)
    bot.run_polling()

if __name__ == "__main__":
    main()

import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = '7725259678:AAHhV82j6RJgWkI6I6C0F4JeI9RzSbMozDQ'

KRW_TO_USD = 0.00074
USD_TO_RUB = 94
LOGISTICS_USD = 1200
BROKER_FEE = 40000

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Вставь ссылку на Encar, и я посчитаю стоимость авто под ключ в РФ.")

def extract_price_from_encar(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    price_tag = soup.find('span', class_='price')
    if not price_tag:
        return None

    price_str = price_tag.text.replace(",", "").replace("₩", "").strip()
    try:
        return int(price_str)
    except:
        return None

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "encar.com" not in url:
        await update.message.reply_text("⛔ Я пока понимаю только ссылки с Encar.com")
        return

    price_krw = extract_price_from_encar(url)

    if not price_krw:
        await update.message.reply_text("❗ Не смог найти цену. Убедись, что ссылка ведёт на карточку автомобиля.")
        return

    price_usd = price_krw * KRW_TO_USD
    price_rub = price_usd * USD_TO_RUB
    logistics = LOGISTICS_USD * USD_TO_RUB
    customs = price_rub * 0.15
    total = price_rub + logistics + customs + BROKER_FEE

    result = (
        f"🚗 Цена на Encar: ₩{price_krw:,}\n"
        f"💵 В долларах: ${price_usd:,.0f}\n"
        f"🇷🇺 Стоимость в РФ под ключ: {int(total):,} ₽\n\n"
        f"📦 Включено:\n"
        f"— Логистика: {int(logistics):,} ₽\n"
        f"— Таможня: {int(customs):,} ₽\n"
        f"— Услуги: {BROKER_FEE:,} ₽"
    )

    await update.message.reply_text(result)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()

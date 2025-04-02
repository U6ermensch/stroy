from dotenv import load_dotenv
import os

load_dotenv()

# Bot settings
BOT_TOKEN = "7886244752:AAF3eqk7I3sB1QpMWsXAf8xt-Bs_R3HsWMQ"

# Store information
STORE_NAME = "Строительный магазин"
WORKING_HOURS = "Пн-Вс: 10:00 - 19:00\n"
ADDRESS = "Г.Иркутск Ул Розы Люксембург д. 293А"
CONTACT_PHONE = "89641245566"

# Admin user IDs (add your Telegram user ID here)
ADMIN_IDS = [420492655]  # Замените на ваш Telegram ID

# Database settings
DATABASE_URL = "sqlite+aiosqlite:///store.db" 
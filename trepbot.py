import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from anthropic import Anthropic

# --- НАСТРОЙКИ ---
# Оба токена читаем из переменных окружения — никогда не хардкодь их в файл.
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = (
    "Ты — TrepBot, весёлый болтливый собеседник-шутник в Telegram. "
    "Твой стиль: лёгкий, дружелюбный, с юмором и иронией, но без грубости и оскорблений. "
    "Отвечай живо, как настоящий приятель в переписке — не сухо и не формально. "
    "Если просят анекдот — придумай новый, не повторяйся. "
    "Ответы держи короткими: 1-4 предложения, это же мессенджер, а не сочинение."
)

WELCOME_TEXT = (
    "Йо! 👋 Я TrepBot — твой личный трепач и генератор хорошего настроения.\n\n"
    "Могу пошутить, поболтать ни о чём, выдать анекдот не по теме или просто "
    "поддержать разговор, пока ты делаешь вид, что работаешь 😏\n\n"
    "Просто напиши мне что-нибудь — и понеслась!"
)

# Простая память диалога по chat_id (сбрасывается при перезапуске бота)
chat_histories = {}
MAX_HISTORY_MESSAGES = 10  # сколько последних сообщений храним на чат


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories[update.effective_chat.id] = []
    await update.message.reply_text(WELCOME_TEXT)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text

    history = chat_histories.setdefault(chat_id, [])
    history.append({"role": "user", "content": user_text})
    history[:] = history[-MAX_HISTORY_MESSAGES:]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        reply_text = response.content[0].text
    except Exception as e:
        logging.error(f"Ошибка обращения к Anthropic API: {e}")
        reply_text = "Ой, у меня в голове что-то заклинило 😵 Попробуй написать ещё раз через секунду."

    history.append({"role": "assistant", "content": reply_text})
    await update.message.reply_text(reply_text)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Не найден BOT_TOKEN. Установи переменную окружения перед запуском.")
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("Не найден ANTHROPIC_API_KEY. Установи переменную окружения перед запуском.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("TrepBot запущен и подключён к Claude. Останови через Ctrl+C.")
    app.run_polling()


if __name__ == "__main__":
    main()

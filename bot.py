import logging
import os

from telebot import TeleBot, types
from handlers import (
    register_add_note,
    register_show_notes,
    register_toggle_status,
    register_delete_note,
    register_edit_note, register_delete_all_notes,
)

from config import TOKEN

# Ensure the logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(log_dir, "bot.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Log the startup message
logging.info("Bot is starting...")

# Initialize bot
bot = TeleBot(TOKEN)


# Main menu handler
@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"User {message.chat.id} started the bot.")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Add Note", "📋 Show Notes", "✅ Toggle Status", "✏️ Edit Note")
    markup.add("❌ Delete Note", "🗑️ Delete All Notes")
    bot.send_message(
        message.chat.id,
        "*Welcome to your Note Bot!*\n\nChoose an option below:",
        parse_mode="Markdown",
        reply_markup=markup,
    )


# Register handlers
register_add_note(bot)
register_show_notes(bot)
register_toggle_status(bot)
register_delete_note(bot)
register_edit_note(bot)
register_delete_all_notes(bot)

# Run the bot
if __name__ == "__main__":
    logging.info("Bot is starting...")
    bot.polling(non_stop=True)

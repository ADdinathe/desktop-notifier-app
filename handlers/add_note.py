import logging

from handlers.database import db

def register_handlers(bot):
    @bot.message_handler(func=lambda msg: msg.text == "📝 Add Note")
    def add_note_prompt(message):
        msg = bot.send_message(message.chat.id, "📝 *Please enter your note:*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, save_note)

    def save_note(message):
        try:
            note = message.text.strip()
            if note:
                db.add_note(message.chat.id, note)
                bot.send_message(message.chat.id, "✅ *Note added successfully!*", parse_mode="Markdown")
                logging.info(f"User {message.chat.id} added a note: {note}")
            else:
                bot.send_message(message.chat.id, "⚠️ *You didn't provide a note.*", parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error saving note for user {message.chat.id}: {e}")
            bot.send_message(message.chat.id, "❌ *An error occurred while saving your note.*", parse_mode="Markdown")

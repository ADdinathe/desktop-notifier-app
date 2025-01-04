import logging
from telebot import types
import traceback
from handlers.database import db

def register_handlers(bot):
    @bot.message_handler(func=lambda msg: msg.text == "❌ Delete Note")
    def delete_note_prompt(message):
        try:
            notes = db.get_notes(message.chat.id)
            print(notes)
            if notes:
                markup = types.InlineKeyboardMarkup()
                for note_id, note, _ in notes:
                    markup.add(
                        types.InlineKeyboardButton(
                            f"{note_id}. {note[:20]}...",
                            callback_data=f"delete_{note_id}"
                        )
                    )
                bot.send_message(message.chat.id, "🗑️ *Select a note to delete:*", parse_mode="Markdown",
                                 reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "📭 *No notes found to delete.*", parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error displaying delete options for user {message.chat.id}: {e}")
            bot.send_message(message.chat.id, "❌ *An error occurred while retrieving your notes.*",
                             parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
    def delete_note_callback(call):
        note_id = int(call.data.split("_")[1])
        print('note_id', note_id)
        try:
            logging.info(f"Attempting to delete note with ID {note_id} for user {call.message.chat.id}")
            db.delete_note(note_id, call.message.chat.id)
            bot.edit_message_text("🗑️ *Note deleted successfully!*", call.message.chat.id, call.message.message_id,
                                  parse_mode="Markdown")
            logging.info(f"User {call.message.chat.id} deleted note {note_id}.")
        except Exception as e:
            logging.error(f"Error deleting note {note_id} (user {call.message.chat.id}): {e}")
            logging.error(f"Stacktrace: {traceback.format_exc()}")
            bot.send_message(call.message.chat.id, "❌ *An error occurred while deleting the note.*",
                             parse_mode="Markdown")

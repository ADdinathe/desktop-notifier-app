import logging
from telebot import types
from handlers.database import db
def register_handlers(bot):
    @bot.message_handler(func=lambda msg: msg.text == "✏️ Edit Note")
    def edit_note_prompt(message):
        try:
            notes = db.get_notes(message.chat.id)
            if notes:
                markup = types.InlineKeyboardMarkup()
                for note_id, note, _ in notes:
                    markup.add(
                        types.InlineKeyboardButton(
                            f"{note_id}. {note[:20]}...",
                            callback_data=f"edit_{note_id}"
                        )
                    )
                bot.send_message(message.chat.id, "✏️ *Select a note to edit:*", parse_mode="Markdown", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "📭 *No notes found to edit.*", parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error displaying edit options for user {message.chat.id}: {e}")
            bot.send_message(message.chat.id, "❌ *An error occurred while retrieving your notes.*", parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
    def edit_note_callback(call):
        note_id = int(call.data.split("_")[1])
        msg = bot.send_message(call.message.chat.id, "✏️ *Enter the new content for the note:*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, lambda m: update_note_content(m, note_id))

    def update_note_content(message, note_id):
        try:
            new_content = message.text.strip()
            db.update_note_content(note_id, new_content, message.chat.id)
            bot.send_message(message.chat.id, "✅ *Note updated successfully!*", parse_mode="Markdown")
            logging.info(f"User {message.chat.id} updated note {note_id}.")
        except Exception as e:
            logging.error(f"Error updating note {note_id} (user {message.chat.id}): {e}")
            bot.send_message(message.chat.id, "❌ *An error occurred while updating the note.*", parse_mode="Markdown")

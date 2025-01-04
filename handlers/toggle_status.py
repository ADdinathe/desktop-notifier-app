import logging
from telebot import types
from handlers.database import db


def register_handlers(bot):
    @bot.message_handler(func=lambda msg: msg.text == "✅ Toggle Status")
    def toggle_status_prompt(message):
        try:
            notes = db.get_notes(message.chat.id)
            if notes:
                markup = types.InlineKeyboardMarkup()
                for note_id, note, status in notes:
                    markup.add(
                        types.InlineKeyboardButton(
                            f"{note_id}. [{status}] {note[:20]}...",
                            callback_data=f"toggle_{note_id}"
                        )
                    )
                bot.send_message(message.chat.id, "🛠️ *Select a note to toggle its status:*", parse_mode="Markdown",
                                 reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "📭 *No notes found to toggle.*", parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error displaying toggle options for user {message.chat.id}: {e}")
            bot.send_message(message.chat.id, "❌ *An error occurred while retrieving your notes.*",
                             parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_"))
    def toggle_status_callback(call):
        note_id = int(call.data.split("_")[1])
        try:
            current_status = db.get_note_status(note_id, call.message.chat.id)
            if current_status:
                new_status = "Checked" if current_status == "Unchecked" else "Unchecked"
                db.update_status(note_id, new_status, call.message.chat.id)
                bot.edit_message_text(
                    f"✅ *Note {note_id} status updated to {new_status}.*",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="Markdown"
                )
                logging.info(f"User {call.message.chat.id} toggled note {note_id} status to {new_status}.")
            else:
                bot.edit_message_text("❌ *Note not found.*", call.message.chat.id, call.message.message_id)
        except Exception as e:
            logging.error(f"Error toggling status for note {note_id} (user {call.message.chat.id}): {e}")
            bot.send_message(call.message.chat.id, "❌ *An error occurred while updating the note status.*",
                             parse_mode="Markdown")

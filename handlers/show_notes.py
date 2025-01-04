import logging
from telebot import types
from handlers.database import db


def register_handlers(bot):
    @bot.message_handler(func=lambda msg: msg.text == "📋 Show Notes")
    def show_notes(message, page=1, per_page=5):
        try:
            notes = db.get_notes(message.chat.id)
            total_notes = len(notes)
            total_pages = (total_notes + per_page - 1) // per_page

            if total_notes == 0:
                bot.send_message(message.chat.id, "📭 *No notes found.*", parse_mode="Markdown")
                return

            start_index = (page - 1) * per_page
            end_index = min(start_index + per_page, total_notes)
            current_notes = notes[start_index:end_index]

            response = f"📋 *Your Notes (Page {page}/{total_pages}):*\n\n"
            for note_id, note, status in current_notes:
                response += f"{note_id}. [{status}] {note}\n"

            markup = types.InlineKeyboardMarkup()
            if page > 1:
                markup.add(types.InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page - 1}"))
            if page < total_pages:
                markup.add(types.InlineKeyboardButton("➡️ Next", callback_data=f"page_{page + 1}"))

            bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=markup)
        except Exception as e:
            logging.error(f"Error showing notes for user {message.chat.id}: {e}")
            bot.send_message(message.chat.id, "❌ *An error occurred while retrieving your notes.*",
                             parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
    def paginate_notes(call):
        page = int(call.data.split("_")[1])
        show_notes(call.message, page)

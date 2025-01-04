import logging
from telebot import types
import traceback
from handlers.database import db


def register_handlers(bot):
    @bot.message_handler(func=lambda msg: msg.text == "🗑️ Delete All Notes")
    def delete_all_notes_prompt(message):
        try:
            # Retrieve the user's notes to confirm if any exist
            notes = db.get_notes(message.chat.id)
            if notes:
                # Confirm action before deletion
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add(types.KeyboardButton("Yes, delete all notes"))
                markup.add(types.KeyboardButton("Main"))
                markup.add(types.KeyboardButton("Cancel"))
                bot.send_message(message.chat.id, "🗑️ Are you sure you want to delete all your notes?",
                                 reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "📭 *You have no notes to delete.*", parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error displaying delete all options for user {message.chat.id}: {e}")
            bot.send_message(message.chat.id, "❌ *An error occurred while retrieving your notes.*",
                             parse_mode="Markdown")

    @bot.message_handler(func=lambda msg: msg.text == "Yes, delete all notes")
    def delete_all_notes_confirm(message):
        try:
            # Delete all notes for the user
            if db.delete_all_notes(message.chat.id):
                bot.send_message(message.chat.id, "🗑️ *All your notes have been deleted successfully!*",
                                 parse_mode="Markdown")
                logging.info(f"User {message.chat.id} deleted all their notes.")
            else:
                bot.send_message(message.chat.id, "❌ *Failed to delete your notes. Please try again later.*",
                                 parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error deleting all notes for user {message.chat.id}: {e}")
            bot.send_message(message.chat.id, "❌ *An error occurred while deleting your notes.*", parse_mode="Markdown")

    @bot.message_handler(func=lambda msg: msg.text == "Cancel")
    def cancel_delete_all_notes(message):
        bot.send_message(message.chat.id, "❌ *Deletion of all notes has been canceled.*", parse_mode="Markdown")

    @bot.message_handler(func=lambda msg: msg.text == "Main")
    def cancel_delete_all_notes(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📝 Add Note", "📋 Show Notes", "✅ Toggle Status", "✏️ Edit Note")
        markup.add("❌ Delete Note", "🗑️ Delete All Notes")
        bot.send_message(
            message.chat.id,
            "*Welcome to your Note Bot!*\n\nChoose an option below:",
            parse_mode="Markdown",
            reply_markup=markup,
        )

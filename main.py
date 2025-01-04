from telebot import TeleBot, types
import sqlite3
from config import TOKEN


bot = TeleBot(TOKEN)

# Create and connect to the database
conn = sqlite3.connect('notes.db', check_same_thread=False)
cursor = conn.cursor()

# Create the notes table
cursor.execute('''
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    note TEXT
)
''')
conn.commit()


# Start the bot and show main menu
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Add Note", "Show Notes", "Edit Note", "Delete Note", "Delete All Notes")
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


# Add a new note
@bot.message_handler(func=lambda msg: msg.text == "Add Note")
def add_note_prompt(message):
    msg = bot.send_message(message.chat.id, "Please enter your note:")
    bot.register_next_step_handler(msg, save_note)


def save_note(message):
    note = message.text.strip()
    if note:
        cursor.execute('INSERT INTO notes (user_id, note) VALUES (?, ?)', (message.chat.id, note))
        conn.commit()
        bot.send_message(message.chat.id, "Note added successfully!")
    else:
        bot.send_message(message.chat.id, "You didn't provide a note.")


# Show notes with pagination
@bot.message_handler(func=lambda msg: msg.text == "Show Notes")
def show_notes(message, page=1, per_page=5):
    cursor.execute('SELECT id, note FROM notes WHERE user_id = ?', (message.chat.id,))
    notes = cursor.fetchall()
    total_notes = len(notes)
    total_pages = (total_notes + per_page - 1) // per_page

    if total_notes == 0:
        bot.send_message(message.chat.id, "You don't have any notes.")
        return

    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, total_notes)
    current_notes = notes[start_index:end_index]

    response = f"Your notes (Page {page}/{total_pages}):\n"
    for note_id, note in current_notes:
        response += f"{note_id}. {note[:50]}...\n"

    markup = types.InlineKeyboardMarkup()
    if page > 1:
        markup.add(types.InlineKeyboardButton("Previous", callback_data=f"page_{page - 1}"))
    if page < total_pages:
        markup.add(types.InlineKeyboardButton("Next", callback_data=f"page_{page + 1}"))

    bot.send_message(message.chat.id, response, reply_markup=markup)


# Handle pagination callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def paginate_notes(call):
    page = int(call.data.split("_")[1])
    show_notes(call.message, page)


# Edit a note
@bot.message_handler(func=lambda msg: msg.text == "Edit Note")
def edit_note_prompt(message):
    cursor.execute('SELECT id, note FROM notes WHERE user_id = ?', (message.chat.id,))
    notes = cursor.fetchall()
    if notes:
        markup = types.InlineKeyboardMarkup()
        for note_id, note in notes:
            markup.add(types.InlineKeyboardButton(f"{note_id}. {note[:20]}...", callback_data=f"edit_{note_id}"))
        bot.send_message(message.chat.id, "Select a note to edit:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "You don't have any notes to edit.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_note_callback(call):
    note_id = int(call.data.split("_")[1])
    msg = bot.send_message(call.message.chat.id, "Enter the updated note:")
    bot.register_next_step_handler(msg, update_note, note_id)


def update_note(message, note_id):
    new_note = message.text.strip()
    cursor.execute('UPDATE notes SET note = ? WHERE id = ? AND user_id = ?', (new_note, note_id, message.chat.id))
    conn.commit()
    bot.send_message(message.chat.id, "Note updated successfully!")


# Delete all notes
@bot.message_handler(func=lambda msg: msg.text == "Delete All Notes")
def delete_all_notes_prompt(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Yes, delete all", callback_data="delete_all_yes"))
    markup.add(types.InlineKeyboardButton("No, cancel", callback_data="delete_all_no"))
    bot.send_message(message.chat.id, "Are you sure you want to delete all notes?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_all_"))
def delete_all_notes_callback(call):
    if call.data == "delete_all_yes":
        cursor.execute('DELETE FROM notes WHERE user_id = ?', (call.message.chat.id,))
        conn.commit()
        bot.edit_message_text("All notes deleted successfully.", call.message.chat.id, call.message.message_id)
    elif call.data == "delete_all_no":
        bot.edit_message_text("Operation canceled.", call.message.chat.id, call.message.message_id)


# Delete a specific note
@bot.message_handler(func=lambda msg: msg.text == "Delete Note")
def delete_note_prompt(message):
    cursor.execute('SELECT id, note FROM notes WHERE user_id = ?', (message.chat.id,))
    notes = cursor.fetchall()
    if notes:
        markup = types.InlineKeyboardMarkup()
        for note_id, note in notes:
            markup.add(types.InlineKeyboardButton(f"{note_id}. {note[:20]}...", callback_data=f"delete_{note_id}"))
        bot.send_message(message.chat.id, "Select a note to delete:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "You don't have any notes to delete.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_note_callback(call):
    note_id = int(call.data.split("_")[1])
    cursor.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, call.message.chat.id))
    if cursor.rowcount > 0:
        conn.commit()
        bot.edit_message_text(f"Note {note_id} deleted successfully.", call.message.chat.id, call.message.message_id)
    else:
        bot.edit_message_text(f"No note found with ID {note_id}.", call.message.chat.id, call.message.message_id)


# Run the bot
bot.polling(non_stop=True)

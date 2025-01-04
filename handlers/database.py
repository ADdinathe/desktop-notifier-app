import sqlite3


class Database:
    def __init__(self, db_path="notes.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            note TEXT,
            status TEXT DEFAULT 'Unchecked'
        )
        ''')
        self.conn.commit()

    def add_note(self, user_id, note):
        self.cursor.execute('INSERT INTO notes (user_id, note) VALUES (?, ?)', (user_id, note))
        self.conn.commit()

    def get_notes(self, user_id):
        self.cursor.execute('SELECT id, note, status FROM notes WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()

    def update_status(self, note_id, new_status, user_id):
        self.cursor.execute('UPDATE notes SET status = ? WHERE id = ? AND user_id = ?', (new_status, note_id, user_id))
        self.conn.commit()

    def delete_note(self, note_id, user_id):
        try:
            self.cursor.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting note {note_id} for user {user_id}: {e}")
            return False

    def delete_all_notes(self, user_id):
        try:
            self.cursor.execute('DELETE FROM notes WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting all notes for user {user_id}: {e}")
            return False

    def get_note_status(self, note_id, user_id):
        try:
            self.cursor.execute('SELECT status FROM notes WHERE id = ? AND user_id = ?', (note_id, user_id))
            result = self.cursor.fetchone()
            if result:
                return result[0]  # Return the status of the note
            return None  # Return None if the note is not found
        except Exception as e:
            print(f"Error retrieving status for note {note_id} (user {user_id}): {e}")
            return None

    def update_note_content(self, note_id, new_content, user_id):
        try:
            self.cursor.execute('UPDATE notes SET note = ? WHERE id = ? AND user_id = ?',
                                (new_content, note_id, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating content for note {note_id} (user {user_id}): {e}")
            return False


db = Database()

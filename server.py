from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all domains

DB_PATH = 'chat_history.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def serve_index():
    # Serve mainpage.html as the index page
    return send_from_directory(app.static_folder, 'mainpage.html')

@app.route('/chat', methods=['POST'])
def save_chat():
    data = request.json
    user_message = data.get('user_message')
    bot_response = data.get('bot_response')
    timestamp = datetime.utcnow().isoformat()

    if not user_message or not bot_response:
        return jsonify({'error': 'Missing user_message or bot_response'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO chats (role, message, timestamp) VALUES (?, ?, ?)', ('user', user_message, timestamp))
    c.execute('INSERT INTO chats (role, message, timestamp) VALUES (?, ?, ?)', ('bot', bot_response, timestamp))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT role, message, timestamp FROM chats ORDER BY id ASC')
    rows = c.fetchall()
    conn.close()

    history = [{'role': row[0], 'message': row[1], 'timestamp': row[2]} for row in rows]
    return jsonify(history)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

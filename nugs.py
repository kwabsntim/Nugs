import os
from flask import Flask, request, render_template, session, redirect, url_for
from flask import abort
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt'}  # You can add more allowed extensions

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def create_db():
    """Creates the database and the necessary tables if they don't exist."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            course TEXT NOT NULL,
            level INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Call this function when the app starts
create_db()

def get_db_connection():
    """Returns a database connection."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the login functionality."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_id'] = 'admin'  # Set the session variable for admin
            return redirect(url_for('upload'))
        else:
            return render_template("admin.html", error="Invalid credentials")
    return render_template("admin.html")




@app.route('/logout')
def logout():
    """Logs the admin out of the session."""
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handles file uploads by the admin."""
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        file = request.files['file']
        course = request.form['course']
        level = request.form['level']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Insert file metadata into the database
            conn = get_db_connection()
            conn.execute("INSERT INTO files (filename, course, level) VALUES (?, ?, ?)",
                         (filename, course, int(level)))
            conn.commit()
            conn.close()
            return redirect(url_for('show_files', course=course, level=level))
        else:
            return render_template("upload.html", error="Invalid file or no file selected")
    
    return render_template("upload.html")
@app.route('/select')
def select():
    return render_template('select.html')
@app.route('/files/<course>/<int:level>')
def show_files(course, level):
    """Displays files for the selected course and level."""
    conn = get_db_connection()
    files = conn.execute("SELECT * FROM files WHERE course = ? AND level = ?", (course, level)).fetchall()
    conn.close()

    if not files:
        return render_template("elect.html", error="No files found for this course and level")

    return render_template("elect.html", files=files, selected_course=course, selected_level=level)

@app.route('/delete_file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    """Deletes the specified file from the database and file system."""
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('home'))  # Redirect to home if the user is not an admin

    conn = get_db_connection()
    file = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()

    if file:
        # Delete the file from the file system
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete file record from the database
        conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('show_files', course=file['course'], level=file['level']))
    else:
        conn.close()
        return "Error: File not found", 404
    
@app.route('/allfiles', methods=['GET', 'POST'])
def admin_files():
    if session.get('user_id') != 'admin':
        return redirect(url_for('login'))  # Protect the route
    conn = get_db_connection()
    files = conn.execute("SELECT * FROM files").fetchall()
    conn.close()
    return render_template("admin_files.html", files=files)
@app.route('/delete_any_file/<int:file_id>', methods=['POST'])
def delete_any_file(file_id):
    if session.get('user_id') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    file = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()

    if file:
        # Remove from file system
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete from database
        conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_files'))
    else:
        conn.close()
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)

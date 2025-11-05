import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# -----------------------------------------------------------
# 🔧 FLASK APP SETUP
# -----------------------------------------------------------
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = "superhemligt"

# tillåt frontend att anropa API:et
CORS(app, supports_credentials=True)

bcrypt = Bcrypt(app)

# -----------------------------------------------------------
# 💌 GMAIL MAIL CONFIG (ändra till din)
# -----------------------------------------------------------
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='familjenskung@gmail.com',        # <-- din Gmail
    MAIL_PASSWORD='rkwvqtsbphcibuls',       # <-- ditt app-lösenord
    MAIL_DEFAULT_SENDER=('Baby Milestone Journal', 'familjenskung@gmail.com')
)
mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

# -----------------------------------------------------------
# 🗃️ DATABASE SETUP
# -----------------------------------------------------------
def init_db():
    with sqlite3.connect("milestones.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                date TEXT,
                description TEXT,
                image TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

# -----------------------------------------------------------
# 👤 REGISTER
# -----------------------------------------------------------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    try:
        with sqlite3.connect("milestones.db") as conn:
            conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        return jsonify({"success": True, "message": "Konto skapat!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "E-postadressen används redan."}), 400

# -----------------------------------------------------------
# 🔑 LOGIN
# -----------------------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    with sqlite3.connect("milestones.db") as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user and bcrypt.check_password_hash(user[2], password):
        return jsonify({"success": True, "message": "Inloggning lyckades!", "user_id": user[0]})
    else:
        return jsonify({"success": False, "message": "Fel e-post eller lösenord"}), 401

# -----------------------------------------------------------
# 💌 GLÖMT LÖSENORD
# -----------------------------------------------------------
@app.route('/api/forgot', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    with sqlite3.connect("milestones.db") as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user:
        token = s.dumps(email, salt='password-reset')
        reset_link = f"http://localhost:5173/reset/{token}"

        html_body = f"""
<div style="font-family: Arial, sans-serif; background-color:#fdf2f8; padding:20px; border-radius:10px; max-width:480px;">
    <h2 style="color:#be185d; margin-top:0;">Baby Milestone Journal 💕</h2>
    <p>Hej!</p>
    <p>Klicka på knappen nedan för att återställa ditt lösenord:</p>
        <a href="{reset_link}"
        style="display:inline-block; background-color:#ec4899; color:white; padding:10px 20px;
            border-radius:8px; text-decoration:none; font-weight:bold;">
        Återställ lösenord
        </a>
    <p style="margin-top:20px; color:#6b7280; font-size:14px;">
        Länken är giltig i 1 timme.
    </p>
</div>
"""

        msg = Message("Återställ ditt lösenord", recipients=[email])
        msg.body = reset_link
        msg.html = html_body
        mail.send(msg)

    # alltid samma svar, av säkerhetsskäl
    return jsonify({"message": "Om e-postadressen finns registrerad har ett mejl skickats."})

# -----------------------------------------------------------
# 🔁 ÅTERSTÄLL LÖSENORD
# -----------------------------------------------------------
@app.route('/api/reset/<token>', methods=['POST'])
def reset_password(token):
    data = request.json
    new_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')

    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
        with sqlite3.connect("milestones.db") as conn:
            conn.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
        return jsonify({"success": True, "message": "Lösenord uppdaterat!"})
    except SignatureExpired:
        return jsonify({"success": False, "message": "Länken har gått ut."}), 400
    except BadSignature:
        return jsonify({"success": False, "message": "Ogiltig länk."}), 400

# -----------------------------------------------------------
# 👶 MILESTONES (GET + POST)
# -----------------------------------------------------------
@app.route('/api/milestones', methods=['GET', 'POST'])
def milestones():
    if request.method == 'POST':
        data = request.form
        user_id = data.get('user_id')
        title = data.get('title')
        date = data.get('date')
        desc = data.get('description')
        image = None

        file = request.files.get('image')
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(upload_path)
            image = filename

        with sqlite3.connect("milestones.db") as conn:
            conn.execute("""
                INSERT INTO milestones (user_id, title, date, description, image)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, title, date, desc, image))
        return jsonify({"success": True})

    # GET – hämta alla för användaren
    user_id = request.args.get('user_id')
    with sqlite3.connect("milestones.db") as conn:
        milestones = conn.execute(
            "SELECT * FROM milestones WHERE user_id=? ORDER BY date DESC",
            (user_id,)
        ).fetchall()

    data = [dict(id=m[0], user_id=m[1], title=m[2],
                 date=m[3], description=m[4], image=m[5]) for m in milestones]
    return jsonify(data)

# -----------------------------------------------------------
# 📸 SERVERA BILDER
# -----------------------------------------------------------
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

# -----------------------------------------------------------
# ⚛️ SERVERA REACT BUILD (PROD)
# -----------------------------------------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    # basmapp till React build
    base = os.path.join(os.path.dirname(__file__), '../frontend/dist')
    index_path = os.path.join(base, 'index.html')
    requested_path = os.path.join(base, path)

    # debug-utskrifter (kan tas bort sen)
    print("Serving React from:", base)
    print("Requested path:", path)

    # om sökvägen finns (t.ex. en .js eller .css-fil)
    if path != "" and os.path.exists(requested_path):
        return send_from_directory(base, path)
    # annars skicka alltid index.html
    elif os.path.exists(index_path):
        return send_from_directory(base, 'index.html')
    else:
        return "index.html saknas i dist", 404


# -----------------------------------------------------------
# 🚀 START APP
# -----------------------------------------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5001)


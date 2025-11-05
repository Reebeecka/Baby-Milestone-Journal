from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3, os
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# --- Flask setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = "superhemligt"

# --- Gmail SMTP Setup ---
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='familjenskung@gmail.com',  # <-- byt till din Gmail-adress
    MAIL_PASSWORD='brspzkmxbareucke',  # <-- klistra in ditt app-lösenord här
    MAIL_DEFAULT_SENDER=('Baby Milestone Journal', 'familjenskung@gmail.com')  # samma adress
)

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

# --- Login / bcrypt setup ---
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
login_manager.login_view = "login"


# --- Initiera databas ---
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


# --- User-klass för Flask-Login ---
class User(UserMixin):
    def __init__(self, id_, email, password):
        self.id = id_
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect("milestones.db") as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            return User(id_=user[0], email=user[1], password=user[2])
    return None


# --- Registrering ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        try:
            with sqlite3.connect("milestones.db") as conn:
                conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "E-postadressen används redan."

    return render_template('register.html')


# --- Inloggning ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect("milestones.db") as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and bcrypt.check_password_hash(user[2], password):
            login_user(User(id_=user[0], email=user[1], password=user[2]))
            return redirect(url_for('index'))
        return "Fel e-post eller lösenord."
    return render_template('login.html')


# --- Utloggning ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# --- Glömt lösenord ---
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        with sqlite3.connect("milestones.db") as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user:
            token = s.dumps(email, salt='password-reset')
            reset_link = url_for('reset_password', token=token, _external=True)

            msg = Message("Återställ ditt lösenord", recipients=[email])
            msg.body = f"Klicka på länken för att återställa ditt lösenord:\n\n{reset_link}\n\nLänken gäller i 1 timme."
            mail.send(msg)

        return "Om e-postadressen finns registrerad har ett mejl skickats med instruktioner."
    return render_template('forgot.html')


# --- Återställ lösenord via token ---
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
    except SignatureExpired:
        return "Länken har gått ut."
    except BadSignature:
        return "Ogiltig länk."

    if request.method == 'POST':
        new_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        with sqlite3.connect("milestones.db") as conn:
            conn.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        return redirect(url_for('login'))

    return render_template('reset.html')


# --- Visa milstolpar ---
@app.route('/')
@login_required
def index():
    with sqlite3.connect("milestones.db") as conn:
        milestones = conn.execute(
            "SELECT * FROM milestones WHERE user_id = ? ORDER BY date DESC",
            (current_user.id,)
        ).fetchall()
    return render_template('index.html', milestones=milestones)


# --- Lägg till milstolpe ---
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_milestone():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        description = request.form['description']
        image = None

        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            image = filename

        with sqlite3.connect("milestones.db") as conn:
            conn.execute("""
                INSERT INTO milestones (user_id, title, date, description, image)
                VALUES (?, ?, ?, ?, ?)
            """, (current_user.id, title, date, description, image))

        return redirect(url_for('index'))
    return render_template('add_milestone.html')


# --- Redigera milstolpe ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_milestone(id):
    with sqlite3.connect("milestones.db") as conn:
        milestone = conn.execute(
            "SELECT * FROM milestones WHERE id = ? AND user_id = ?",
            (id, current_user.id)
        ).fetchone()

    if not milestone:
        return "Den här milstolpen finns inte eller tillhör någon annan."

    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        description = request.form['description']
        image = milestone[5]

        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            image = filename

        with sqlite3.connect("milestones.db") as conn:
            conn.execute("""
                UPDATE milestones
                SET title = ?, date = ?, description = ?, image = ?
                WHERE id = ? AND user_id = ?
            """, (title, date, description, image, id, current_user.id))

        return redirect(url_for('index'))

    return render_template('edit_milestone.html', milestone=milestone)


# --- Ta bort milstolpe ---
@app.route('/delete/<int:id>')
@login_required
def delete_milestone(id):
    with sqlite3.connect("milestones.db") as conn:
        conn.execute(
            "DELETE FROM milestones WHERE id = ? AND user_id = ?",
            (id, current_user.id)
        )
    return redirect(url_for('index'))


# --- Kör appen ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

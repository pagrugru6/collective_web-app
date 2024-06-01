import os
import psycopg2
from flask import Flask, render_template, redirect, url_for, request, jsonify, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from collective.models import Person, Collective, Project, Skill, BelongsTo, Possesses, Participates, Organizes, Requires, CollectiveMessage, ProjectMessage, Invitation, Database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['DATABASE_URL'] = 'postgresql://pacollective:mynameispa@localhost/collective'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Person.get_by_id(user_id)

@app.teardown_appcontext
def close_db(exception):
    Database.close_db()

def init_db():
    with app.app_context():
        conn = psycopg2.connect(app.config['DATABASE_URL'])
        cursor = conn.cursor()
        with open(os.path.join(os.path.dirname(__file__), 'collective', 'schema.sql'), 'r') as schema_file:
            schema_sql = schema_file.read()
        cursor.execute(schema_sql)
        conn.commit()
        cursor.close()
        conn.close()

@app.before_request
def before_request():
    if not hasattr(g, 'initialized'):
        init_db()
        g.initialized = True

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        bio = request.form['bio']
        location = request.form['location']
        Person.create(name, email, username, password, bio, location)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Person.get_by_username(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/collectives', methods=['GET', 'POST'])
@login_required
def collectives():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        Collective.create(name, description, location)
        return redirect(url_for('collectives'))
    collectives = Database.fetchall("SELECT * FROM collectives")
    return render_template('collectives.html', collectives=collectives)

@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        Project.create(name, description)
        return redirect(url_for('projects'))
    projects = Database.fetchall("SELECT * FROM projects")
    return render_template('projects.html', projects=projects)

@app.route('/send_collective_message', methods=['POST'])
@login_required
def send_collective_message():
    sender_id = current_user.id
    collective_id = request.form['collective_id']
    message = request.form['message']
    CollectiveMessage.create(collective_id, sender_id, message)
    return '', 204  # No Content

@app.route('/get_collective_messages', methods=['GET'])
@login_required
def get_collective_messages():
    collective_id = request.args.get('collective_id')
    last_message_id = request.args.get('last_message_id')
    if last_message_id:
        messages = CollectiveMessage.get_messages(collective_id, last_message_id)
    else:
        messages = CollectiveMessage.get_messages(collective_id)
    return jsonify(messages)

@app.route('/send_project_message', methods=['POST'])
@login_required
def send_project_message():
    sender_id = current_user.id
    project_id = request.form['project_id']
    message = request.form['message']
    ProjectMessage.create(project_id, sender_id, message)
    return '', 204  # No Content

@app.route('/get_project_messages', methods=['GET'])
@login_required
def get_project_messages():
    project_id = request.args.get('project_id')
    last_message_id = request.args.get('last_message_id')
    if last_message_id:
        messages = ProjectMessage.get_messages(project_id, last_message_id)
    else:
        messages = ProjectMessage.get_messages(project_id)
    return jsonify(messages)

@app.route('/invite_to_collective', methods=['POST'])
@login_required
def invite_to_collective():
    inviter_id = current_user.id
    collective_id = request.form['collective_id']
    invitee_id = request.form['invitee_id']
    Invitation.create(collective_id, invitee_id, inviter_id)
    return '', 204  # No Content

@app.route('/get_invitations', methods=['GET'])
@login_required
def get_invitations():
    invitee_id = current_user.id
    invitations = Invitation.get_invitations(invitee_id)
    return jsonify(invitations)

if __name__ == "__main__":
    app.run(debug=True)

import os
import psycopg2
from flask import Flask, render_template, redirect, url_for, request, jsonify, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from collective.models import Person, Collective, Project, Skill, BelongsTo, Possesses, Participates, Organizes, Requires, CollectiveMessage, ProjectMessage, Invitation, Database
from werkzeug.security import generate_password_hash, check_password_hash

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

@app.before_request
def before_request():
    pass

@app.route('/')
def startup():
    return render_template('startup.html')

@app.route('/home')
@login_required
def home():
    user_id = current_user.id
    user = Person.get_by_id(user_id)
    collectives = BelongsTo.get_collectives_for_user(user_id)
    projects = Participates.get_projects_for_user(user_id)
    return render_template('home.html', user=user, collectives=collectives, projects=projects)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = current_user.id
    user = Person.get_by_id(user_id)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        bio = request.form['bio']
        location = request.form['location']
        Person.update(user_id, name, email, bio, location)
        return redirect(url_for('home'))
    return render_template('profile.html', user=user)

@app.route('/browse_collectives')
def browse_collectives():
    print("Accessing browse_collectives route")
    collectives = Collective.get_all()
    logged_in = current_user.is_authenticated
    if logged_in:
        print("User is logged in")
    else:
        print("User is not logged in")
    return render_template('browse_collectives.html', collectives=collectives, logged_in=logged_in)

@app.route('/create_collective', methods=['GET', 'POST'])
@login_required
def create_collective():
    print("Accessing create_collective route")
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        Collective.create(name, description, location)
        return redirect(url_for('browse_collectives'))
    return render_template('create_collective.html')

@app.route('/browse_projects')
@login_required
def browse_projects():
    projects = Project.get_all()
    return render_template('browse_projects.html', projects=projects)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        bio = request.form['bio']
        location = request.form['location']
        try:
            Person.create(name, email, username, password, bio, location)
            print(f"User {username} created successfully.")
        except Exception as e:
            print(f"Error creating user: {e}")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Person.get_by_username(username)
        if user is None:
            error = 'User does not exist.'
        elif check_password_hash(user.password, password):
            error = 'Incorrect password.'
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('startup'))

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
    print("Starting Flask application...")
    app.run(debug=True)

@app.route('/collective/<int:collective_id>')
@login_required
def collective_home(collective_id):
    collective = Collective.get_by_id(collective_id)
    is_member = BelongsTo.is_member(current_user.id, collective_id)
    projects = Project.get_by_collective(collective_id) if is_member else []
    messages = CollectiveMessage.get_messages(collective_id) if is_member else []
    return render_template('collective_home.html', collective=collective, is_member=is_member, projects=projects, messages=messages)

@app.route('/project/<int:project_id>')
@login_required
def project_home(project_id):
    project = Project.get_by_id(project_id)
    is_member = Participates.is_member(current_user.id, project_id)
    messages = ProjectMessage.get_messages(project_id) if is_member else []
    return render_template('project_home.html', project=project, is_member=is_member, messages=messages)

@app.route('/join_collective/<int:collective_id>', methods=['POST'])
@login_required
def join_collective(collective_id):
    BelongsTo.create(current_user.id, collective_id)
    return redirect(url_for('collective_home', collective_id=collective_id))

@app.route('/join_project/<int:project_id>', methods=['POST'])
@login_required
def join_project(project_id):
    Participates.create(current_user.id, project_id)
    return redirect(url_for('project_home', project_id=project_id))

@app.route('/create_project/<int:collective_id>', methods=['GET', 'POST'])
@login_required
def create_project(collective_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        Project.create(name, description, collective_id)
        return redirect(url_for('collective_home', collective_id=collective_id))
    return render_template('create_project.html', collective_id=collective_id)
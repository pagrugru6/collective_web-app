import os
import psycopg2
from flask import Flask, render_template, redirect, url_for, request, jsonify, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from collective.models import Person, Collective, Project, Skill, BelongsTo, Possesses, Participates, Organizes, Requires, CollectiveMessage, ProjectMessage, Database
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

@app.route('/')
def startup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
        elif not check_password_hash(user.password, password):
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

@app.route('/browse_collectives')
def browse_collectives():
    print("Accessing browse_collectives route")
    collectives = Collective.get_all()
    logged_in = current_user.is_authenticated
    for collective in collectives:
        print(f"Collective: id={collective.id}, name={collective.name}, description={collective.description}")
    if logged_in:
        print("User is logged in")
    else:
        print("User is not logged in")
    return render_template('browse_collectives.html', collectives=collectives, logged_in=logged_in)

@app.route('/browse_projects')
def browse_projects():
    projects = Project.get_all()
    logged_in = current_user.is_authenticated
    for project in projects:
        print(f"Project: id={project.id}, name={project.name}, description={project.description}")
    if logged_in:
        print("User is logged in")
    else:
        print("User is not logged in")
    return render_template('browse_projects.html', projects=projects, logged_in=logged_in)

@app.route('/create_collective', methods=['GET', 'POST'])
@login_required
def create_collective():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        collective_id = Collective.create(name, description, location)
        return redirect(url_for('collective_home', collective_id=collective_id))
    return render_template('create_collective.html')

@app.route('/collective/<int:collective_id>/create_project', methods=['GET', 'POST'])
@login_required
def create_project(collective_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        project_id = Project.create(name, description)
        # Assuming there is a relationship table `organizes` with collective_id and project_id
        Database.execute(
            "INSERT INTO organizes (collective_id, project_id) VALUES (%s, %s)",
            (collective_id, project_id)
        )
        return redirect(url_for('collective_home', collective_id=collective_id))
    return render_template('create_project.html', collective_id=collective_id)

@app.route('/collective/<int:collective_id>/post_message', methods=['POST'])
@login_required
def post_collective_message(collective_id):
    user_id = current_user.id
    message_content = request.form['message']
    CollectiveMessage.create(collective_id, user_id, message_content)
    return redirect(url_for('collective_home', collective_id=collective_id))

@app.route('/project/<int:project_id>/post_message', methods=['POST'])
@login_required
def post_project_message(project_id):
    user_id = current_user.id
    message_content = request.form['message']
    ProjectMessage.create(project_id, user_id, message_content)
    return redirect(url_for('project_home', project_id=project_id))

@app.route('/collective/<int:collective_id>')
@login_required
def collective_home(collective_id):
    print(f"Accessing collective_home route with id={collective_id}")
    collective = Collective.get_by_id(collective_id)
    if not collective:
        print(f"Collective with id={collective_id} not found")
        return "Collective not found", 404
    is_member = BelongsTo.is_member(current_user.id, collective_id)
    print(f"User is {'a member' if is_member else 'not a member'} of collective {collective_id}")
    projects = Project.get_by_collective(collective_id) if is_member else []
    messages = CollectiveMessage.get_messages(collective_id) if is_member else []
    return render_template('collective_home.html', collective=collective, is_member=is_member, projects=projects, messages=messages)

@app.route('/project/<int:project_id>')
@login_required
def project_home(project_id):
    print(f"Accessing project_home route with id={project_id}")
    project = Project.get_by_id(project_id)
    if not project:
        print(f"Project with id={project_id} not found")
        return "Project not found", 404
    is_participant = Participates.is_participant(current_user.id, project_id)
    print(f"User is {'a participant' if is_participant else 'not a participant'} of project {project_id}")
    messages = ProjectMessage.get_messages(project_id) if is_participant else []
    return render_template('project_home.html', project=project, is_participant=is_participant, messages=messages)

# Route to join a collective
@app.route('/collective/<int:collective_id>/join', methods=['POST'])
@login_required
def join_collective(collective_id):
    user_id = current_user.id
    if not BelongsTo.is_member(user_id, collective_id):
        Database.execute(
            "INSERT INTO belongs_to (person_id, collective_id) VALUES (%s, %s)",
            (user_id, collective_id)
        )
    return redirect(url_for('collective_home', collective_id=collective_id))

# Route to join a project
@app.route('/project/<int:project_id>/join', methods=['POST'])
@login_required
def join_project(project_id):
    user_id = current_user.id
    if not Participates.is_participant(user_id, project_id):
        Database.execute(
            "INSERT INTO participates (person_id, project_id) VALUES (%s, %s)",
            (user_id, project_id)
        )
    return redirect(url_for('project_home', project_id=project_id))

@app.route('/delete_profile', methods=['POST'])
@login_required
def delete_profile():
    user_id = current_user.id
    Database.execute("DELETE FROM persons WHERE id = %s", (user_id,))
    logout_user()
    return redirect(url_for('startup'))

@app.route('/collective/<int:collective_id>/delete', methods=['POST'])
@login_required
def delete_collective(collective_id):
    user_id = current_user.id
    if BelongsTo.is_member(user_id, collective_id):
        Database.execute("DELETE FROM collectives WHERE id = %s", (collective_id,))
        Database.execute("DELETE FROM belongs_to WHERE collective_id = %s", (collective_id,))
        Database.execute("DELETE FROM organizes WHERE collective_id = %s", (collective_id,))
        Database.execute("DELETE FROM collective_messages WHERE collective_id = %s", (collective_id,))
    return redirect(url_for('home'))

@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    user_id = current_user.id
    if Participates.is_participant(user_id, project_id):
        Database.execute("DELETE FROM projects WHERE id = %s", (project_id,))
        Database.execute("DELETE FROM participates WHERE project_id = %s", (project_id,))
        Database.execute("DELETE FROM organizes WHERE project_id = %s", (project_id,))
        Database.execute("DELETE FROM project_messages WHERE project_id = %s", (project_id,))
    return redirect(url_for('home'))

@app.route('/collective/<int:collective_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_collective(collective_id):
    user_id = current_user.id
    if not BelongsTo.is_member(user_id, collective_id):
        return redirect(url_for('home'))
    collective = Collective.get_by_id(collective_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        Database.execute(
            "UPDATE collectives SET name = %s, description = %s, location = %s WHERE id = %s",
            (name, description, location, collective_id)
        )
        return redirect(url_for('collective_home', collective_id=collective_id))
    
    return render_template('edit_collective.html', collective=collective)

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    user_id = current_user.id
    if not Participates.is_participant(user_id, project_id):
        return redirect(url_for('home'))
    project = Project.get_by_id(project_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        Database.execute(
            "UPDATE projects SET name = %s, description = %s WHERE id = %s",
            (name, description, project_id)
        )
        return redirect(url_for('project_home', project_id=project_id))
    
    return render_template('edit_project.html', project=project)



if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True)
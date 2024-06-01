from flask import current_app, g
from flask_login import UserMixin
import psycopg2

class Database:
    @staticmethod
    def get_db():
        if 'db' not in g:
            g.db = psycopg2.connect(current_app.config['DATABASE_URL'])
        return g.db

    @staticmethod
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @staticmethod
    def query(query, params=None):
        conn = Database.get_db()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return cursor

    @staticmethod
    def fetchall(query, params=None):
        conn = Database.get_db()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def fetchone(query, params=None):
        conn = Database.get_db()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

# No need to define db instance here
# db = Database()

class Person(UserMixin):
    def __init__(self, id, name, email, username, password, bio, location):
        self.id = id
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.bio = bio
        self.location = location

    @staticmethod
    def get_by_id(user_id):
        result = Database.fetchone("SELECT * FROM persons WHERE id = %s", (user_id,))
        return Person(*result) if result else None

    @staticmethod
    def get_by_username(username):
        result = Database.fetchone("SELECT * FROM persons WHERE username = %s", (username,))
        return Person(*result) if result else None

    @staticmethod
    def create(name, email, username, password, bio, location):
        Database.query("INSERT INTO persons (name, email, username, password, bio, location) VALUES (%s, %s, %s, %s, %s, %s)",
                       (name, email, username, password, bio, location))

class Collective:
    def __init__(self, id, name, description, location):
        self.id = id
        self.name = name
        self.description = description
        self.location = location

    @staticmethod
    def get_by_id(collective_id):
        result = Database.fetchone("SELECT * FROM collectives WHERE id = %s", (collective_id,))
        return Collective(*result) if result else None

    @staticmethod
    def create(name, description, location):
        Database.query("INSERT INTO collectives (name, description, location) VALUES (%s, %s, %s)",
                       (name, description, location))

class Project:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_by_id(project_id):
        result = Database.fetchone("SELECT * FROM projects WHERE id = %s", (project_id,))
        return Project(*result) if result else None

    @staticmethod
    def create(name, description):
        Database.query("INSERT INTO projects (name, description) VALUES (%s, %s)",
                       (name, description))

class Skill:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_by_id(skill_id):
        result = Database.fetchone("SELECT * FROM skills WHERE id = %s", (skill_id,))
        return Skill(*result) if result else None

    @staticmethod
    def create(name, description):
        Database.query("INSERT INTO skills (name, description) VALUES (%s, %s)",
                       (name, description))

class BelongsTo:
    @staticmethod
    def create(person_id, collective_id):
        Database.query("INSERT INTO belongs_to (person_id, collective_id) VALUES (%s, %s)",
                       (person_id, collective_id))

class Possesses:
    @staticmethod
    def create(person_id, skill_id):
        Database.query("INSERT INTO possesses (person_id, skill_id) VALUES (%s, %s)",
                       (person_id, skill_id))

class Participates:
    @staticmethod
    def create(person_id, project_id):
        Database.query("INSERT INTO participates (person_id, project_id) VALUES (%s, %s)",
                       (person_id, project_id))

class Organizes:
    @staticmethod
    def create(collective_id, project_id):
        Database.query("INSERT INTO organizes (collective_id, project_id) VALUES (%s, %s)",
                       (collective_id, project_id))

class Requires:
    @staticmethod
    def create(project_id, skill_id):
        Database.query("INSERT INTO requires (project_id, skill_id) VALUES (%s, %s)",
                       (project_id, skill_id))


class CollectiveMessage:
    def __init__(self, id, collective_id, sender_id, message, timestamp):
        self.id = id
        self.collective_id = collective_id
        self.sender_id = sender_id
        self.message = message
        self.timestamp = timestamp

    @staticmethod
    def create(collective_id, sender_id, message):
        Database.query(
            "INSERT INTO collective_messages (collective_id, sender_id, message) VALUES (%s, %s, %s)",
            (collective_id, sender_id, message)
        )

    @staticmethod
    def get_messages(collective_id, last_message_id=None):
        if last_message_id:
            return Database.fetchall(
                "SELECT * FROM collective_messages WHERE collective_id = %s AND id > %s ORDER BY timestamp ASC",
                (collective_id, last_message_id)
            )
        else:
            return Database.fetchall(
                "SELECT * FROM collective_messages WHERE collective_id = %s ORDER BY timestamp ASC",
                (collective_id,)
            )

class ProjectMessage:
    def __init__(self, id, project_id, sender_id, message, timestamp):
        self.id = id
        self.project_id = project_id
        self.sender_id = sender_id
        self.message = message
        self.timestamp = timestamp

    @staticmethod
    def create(project_id, sender_id, message):
        Database.query(
            "INSERT INTO project_messages (project_id, sender_id, message) VALUES (%s, %s, %s)",
            (project_id, sender_id, message)
        )

    @staticmethod
    def get_messages(project_id, last_message_id=None):
        if last_message_id:
            return Database.fetchall(
                "SELECT * FROM project_messages WHERE project_id = %s AND id > %s ORDER BY timestamp ASC",
                (project_id, last_message_id)
            )
        else:
            return Database.fetchall(
                "SELECT * FROM project_messages WHERE project_id = %s ORDER BY timestamp ASC",
                (project_id,)
            )

class Invitation:
    def __init__(self, id, collective_id, invitee_id, inviter_id, timestamp):
        self.id = id
        self.collective_id = collective_id
        self.invitee_id = invitee_id
        self.inviter_id = inviter_id
        self.timestamp = timestamp

    @staticmethod
    def create(collective_id, invitee_id, inviter_id):
        Database.query(
            "INSERT INTO invitations (collective_id, invitee_id, inviter_id) VALUES (%s, %s, %s)",
            (collective_id, invitee_id, inviter_id)
        )

    @staticmethod
    def get_invitations(invitee_id):
        return Database.fetchall(
            "SELECT * FROM invitations WHERE invitee_id = %s ORDER BY timestamp ASC",
            (invitee_id,)
        )

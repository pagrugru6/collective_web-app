from flask import current_app
from flask_login import UserMixin
import psycopg2

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(current_app.config['DATABASE_URL'])

    def query(self, query, params=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            self.conn.commit()
            return cursor

    def fetchall(self, query, params=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetchone(self, query, params=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

db = Database()

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
        result = db.fetchone("SELECT * FROM persons WHERE id = %s", (user_id,))
        return Person(*result) if result else None

    @staticmethod
    def create(name, email, username, password, bio, location):
        db.query("INSERT INTO persons (name, email, username, password, bio, location) VALUES (%s, %s, %s, %s, %s, %s)",
                 (name, email, username, password, bio, location))

class Collective:
    def __init__(self, id, name, description, location):
        self.id = id
        self.name = name
        self.description = description
        self.location = location

    @staticmethod
    def get_by_id(collective_id):
        result = db.fetchone("SELECT * FROM collectives WHERE id = %s", (collective_id,))
        return Collective(*result) if result else None

    @staticmethod
    def create(name, description, location):
        db.query("INSERT INTO collectives (name, description, location) VALUES (%s, %s, %s)",
                 (name, description, location))

class Project:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_by_id(project_id):
        result = db.fetchone("SELECT * FROM projects WHERE id = %s", (project_id,))
        return Project(*result) if result else None

    @staticmethod
    def create(name, description):
        db.query("INSERT INTO projects (name, description) VALUES (%s, %s)",
                 (name, description))

class Skill:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_by_id(skill_id):
        result = db.fetchone("SELECT * FROM skills WHERE id = %s", (skill_id,))
        return Skill(*result) if result else None

    @staticmethod
    def create(name, description):
        db.query("INSERT INTO skills (name, description) VALUES (%s, %s)",
                 (name, description))

class BelongsTo:
    @staticmethod
    def create(person_id, collective_id):
        db.query("INSERT INTO belongs_to (person_id, collective_id) VALUES (%s, %s)",
                 (person_id, collective_id))

class Possesses:
    @staticmethod
    def create(person_id, skill_id):
        db.query("INSERT INTO possesses (person_id, skill_id) VALUES (%s, %s)",
                 (person_id, skill_id))

class Participates:
    @staticmethod
    def create(person_id, project_id):
        db.query("INSERT INTO participates (person_id, project_id) VALUES (%s, %s)",
                 (person_id, project_id))

class Organizes:
    @staticmethod
    def create(collective_id, project_id):
        db.query("INSERT INTO organizes (collective_id, project_id) VALUES (%s, %s)",
                 (collective_id, project_id))

class Requires:
    @staticmethod
    def create(project_id, skill_id):
        db.query("INSERT INTO requires (project_id, skill_id) VALUES (%s, %s)",
                 (project_id, skill_id))

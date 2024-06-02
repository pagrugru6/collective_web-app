from flask import current_app, g
from flask_login import UserMixin
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    @staticmethod
    def get_db():
        if 'db' not in g:
            try:
                g.db = psycopg2.connect(current_app.config['DATABASE_URL'])
                print("Database connection established.")
            except Exception as e:
                print(f"Error establishing database connection: {e}")
        return g.db

    @staticmethod
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
            print("Database connection closed.")

    @staticmethod
    def query(query, params=None):
        conn = Database.get_db()
        cursor = None
        try:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except Exception as e:
            print(f"Database query error: {e}")
            raise
        # finally:
        #     if cursor:
        #         cursor.close()

    @staticmethod
    def execute(query, params=None):
        conn = Database.get_db()
        cursor = None
        try:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            print(f"Database execute error: {e}")
            raise
        # finally:
        #     if cursor:
        #         cursor.close()

    @staticmethod
    def fetchone(query, params=None):
        conn = Database.get_db()
        cursor = None
        try:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            result = cursor.fetchone()
            print(f"Query result: {result}")
            return result
        except Exception as e:
            print(f"Database fetchone error: {e}")
            raise
        # finally:
        #     if cursor:
        #         cursor.close()

    @staticmethod
    def fetchall(query, params=None):
        conn = Database.get_db()
        cursor = None
        try:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            results = cursor.fetchall()
            print(f"Query results: {results}")
            return results
        except Exception as e:
            print(f"Database fetchall error: {e}")
            raise
        # finally:
        #     if cursor:
        #         cursor.close()

class Person(UserMixin):
    def __init__(self, name, email, username, password, bio, location):
        self.id = id
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.bio = bio
        self.location = location

    @staticmethod
    def get_by_username(username):
        result = Database.fetchone("SELECT * FROM persons WHERE username = %s", (username,))
        return Person(*result) if result else None

    @staticmethod
    def create(name, email, username, password, bio, location):
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        Database.query(
            "INSERT INTO persons (name, email, username, password, bio, location) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, username, hashed_password, bio, location)
        )

    @staticmethod
    def update(user_username, name, email, bio, location):
        Database.query(
            "UPDATE persons SET name = %s, email = %s, bio = %s, location = %s WHERE username = %s",
            (name, email, bio, location, user_username)
        )

class Project:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def create(name, description):
        cursor = Database.query(
            "INSERT INTO projects (name, description) VALUES (%s, %s) RETURNING id",
            (name, description)
        )
        project_id = cursor.fetchone()[0]
        return project_id

    @staticmethod
    def get_all():
        results = Database.fetchall("SELECT id, name, description FROM projects")
        return [Project(*row) for row in results]

    @staticmethod
    def get_by_collective(collective_id):
        results = Database.fetchall(
            "SELECT p.id, p.name, p.description FROM projects p "
            "JOIN organizes o ON p.id = o.project_id WHERE o.collective_id = %s",
            (collective_id,)
        )
        return [Project(*row) for row in results]

class Collective:
    def __init__(self, id, name, description, location):
        self.id = id
        self.name = name
        self.description = description
        self.location = location

    @staticmethod
    def create(name, description, location):
        result = Database.query(
            "INSERT INTO collectives (name, description, location) VALUES (%s, %s, %s) RETURNING id",
            (name, description, location)
        )
        collective_id = result.fetchone()[0]
        return collective_id

    @staticmethod
    def get_all():
        results = Database.fetchall("SELECT id, name, description, location FROM collectives")
        return [Collective(*row) for row in results]

    @staticmethod
    def get_by_id(collective_id):
        print(f"Fetching collective with id={collective_id}")
        result = Database.fetchone("SELECT id, name, description, location FROM collectives WHERE id = %s", (collective_id,))
        if result:
            print(f"Collective found: {result}")
            return Collective(*result)
        print("Collective not found")
        return None

    
class Project:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def create(name, description):
        result = Database.query(
            "INSERT INTO projects (name, description) VALUES (%s, %s) RETURNING id",
            (name, description)
        )
        project_id = result.fetchone()[0]
        return project_id

    @staticmethod
    def get_all():
        results = Database.fetchall("SELECT id, name, description FROM projects")
        return [Project(*row) for row in results]

    @staticmethod
    def get_by_collective(collective_id):
        results = Database.fetchall(
            "SELECT p.id, p.name, p.description FROM projects p "
            "JOIN organizes o ON p.id = o.project_id WHERE o.collective_id = %s",
            (collective_id,)
        )
        return [Project(*row) for row in results]

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
    def create(person_username, collective_id):
        Database.query(
            "INSERT INTO belongs_to (person_username, collective_id) VALUES (%s, %s)",
            (person_username, collective_id)
        )

    @staticmethod
    def is_member(person_username, collective_id):
        result = Database.fetchone(
            "SELECT 1 FROM belongs_to WHERE person_username = %s AND collective_id = %s",
            (person_username, collective_id)
        )
        return result is not None

    @staticmethod
    def get_collectives_for_user(person_username):
        return Database.fetchall(
            "SELECT c.id, c.name, c.description, c.location FROM collectives c JOIN belongs_to b ON c.id = b.collective_id WHERE b.person_username = %s",
            (person_username,)
        )

class Possesses:
    @staticmethod
    def create(person_username, skill_id):
        Database.query("INSERT INTO possesses (person_username, skill_id) VALUES (%s, %s)",
                       (person_username, skill_id))

class Participates:
    @staticmethod
    def create(person_username, project_id):
        Database.query(
            "INSERT INTO participates (person_username, project_id) VALUES (%s, %s)",
            (person_username, project_id)
        )

    @staticmethod
    def is_member(person_username, project_id):
        result = Database.fetchone(
            "SELECT 1 FROM participates WHERE person_username = %s AND project_id = %s",
            (person_username, project_id)
        )
        return result is not None

    @staticmethod
    def get_projects_for_user(person_username):
        return Database.fetchall(
            "SELECT p.id, p.name, p.description FROM projects p JOIN participates pa ON p.id = pa.project_id WHERE pa.person_username = %s",
            (person_username,)
        )

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
    def __init__(self, collective_id, timestamp, sender_username, message):
        self.collective_id = collective_id
        self.timestamp = timestamp
        self.sender_username = sender_username
        self.message = message

    @staticmethod
    def create(collective_id, sender_username, message):
        Database.execute(
            "INSERT INTO collective_messages (collective_id, sender_username, message) VALUES (%s, %s, %s)",
            (collective_id, sender_username, message)
        )

    @staticmethod
    def get_messages(collective_id):
        results = Database.fetchall(
            "SELECT collective_id, timestamp, sender_username, message FROM collective_messages WHERE collective_id = %s ORDER BY timestamp",
            (collective_id,)
        )
        return [CollectiveMessage(*row) for row in results]

class ProjectMessage:
    def __init__(self, project_id, timestamp, sender_username, message):
        self.project_id = project_id
        self.timestamp = timestamp
        self.sender_username = sender_username
        self.message = message

    @staticmethod
    def create(project_id, sender_username, message):
        Database.execute(
            "INSERT INTO project_messages (project_id, sender_username, message) VALUES (%s, %s, %s)",
            (project_id, sender_username, message)
        )

    @staticmethod
    def get_messages(project_id):
        results = Database.fetchall(
            "SELECT project_id, timestamp, sender_username, message FROM project_messages WHERE project_id = %s ORDER BY timestamp",
            (project_id,)
        )
        return [ProjectMessage(*row) for row in results]
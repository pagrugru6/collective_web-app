import os
import psycopg2
from flask import Flask
from bank.models import db

app = Flask(__name__)
app.config['DATABASE_URL'] = 'your_database_url_here'

def init_db():
    conn = psycopg2.connect(app.config['DATABASE_URL'])
    cursor = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__), 'bank', 'schema.sql'), 'r') as schema_file:
        schema_sql = schema_file.read()
    cursor.execute(schema_sql)
    conn.commit()
    cursor.close()
    conn.close()

@app.before_first_request
def setup():
    init_db()

# Rest of your Flask app setup

if __name__ == "__main__":
    app.run(debug=True)

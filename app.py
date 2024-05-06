import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import secrets
import cohere

app = Flask(__name__)
app.secret_key = secrets.token_hex(160) # Set a secret key for CSRF protection

class Form(FlaskForm):
    text = StringField('Enter text to search', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create a database connection
def create_connection():
    conn = sqlite3.connect('app.db', check_same_thread=False)
    return conn

# Create a table
def create_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inputs_outputs
                 (id INTEGER PRIMARY KEY, input TEXT, output TEXT)''')
    conn.commit()

# Insert data
def insert_data(conn, input_text, output_text):
    c = conn.cursor()
    c.execute("INSERT INTO inputs_outputs (input, output) VALUES (?, ?)", (input_text, output_text))
    conn.commit()

# Initialize the database and table
conn = create_connection()
create_table(conn)

@app.route('/', methods=['GET', 'POST'])
def home():
    form = Form()
    co = cohere.Client('KFk7bjuBvoXzC38rDhCIy9806IvSCwAT5ipMzEir')

    if form.validate_on_submit():
        text = form.text.data
        response = co.generate(
            model='command-nightly',
            prompt=text,
            max_tokens=1000,
            temperature=0.9,
            k=0,
            p=0.75,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        output = response.generations[0].text
        insert_data(conn, text, output) # Insert data into the database
        return render_template('home.html', form=form, output=output)

    return render_template('home.html', form=form, output=None)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('hospitals.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS hospitals
                 (name TEXT, address TEXT, phone TEXT, email TEXT)''')
    
    # Adding some values to the database
    hospitals = [
        ('Hospital A', '123 Main St', '123-456-7890', 'contact@hospitala.com'),
        ('Hospital B', '456 Elm St', '987-654-3210', 'contact@hospitalb.com'),
        ('Hospital C', '789 Oak St', '555-555-5555', 'contact@hospitalc.com')
    ]
    c.executemany('INSERT INTO hospitals (name, address, phone, email) VALUES (?, ?, ?, ?)', hospitals)
    conn.commit()
    conn.close()

# Define routes
@app.route('/')
def index():
    return render_template('base.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/services')
def services():
    return redirect(url_for('hospitals'))

@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form['Name']
    email = request.form['Email']
    message = request.form['Message']
    # Add your form submission logic here
    return redirect(url_for('my_maps'))

@app.route('/my_maps')
def my_maps():
    mapbox_access_token = 'pk.eyJ1Ijoicm9oaXRqZCIsImEiOiJjbHZ2M2YwaG8wM2dzMm1uMjYwbmI0cWpiIn0.3eDYbXGmCOFqwPXWfp6bjw'
    return render_template('index.html', mapbox_access_token=mapbox_access_token)

@app.route('/hospitals')
def hospitals():
    conn = get_db_connection()
    hospitals = conn.execute('SELECT * FROM hospitals').fetchall()
    conn.close()
    return render_template('hospitals.html', hospitals=hospitals)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

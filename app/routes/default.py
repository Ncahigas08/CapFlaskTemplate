from app import app
from flask import render_template

# This is for rendering the home page
#index 
@app.route('/')
def index():
    return render_template('index.html')

#
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')




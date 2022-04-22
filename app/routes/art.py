from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Art
from app.classes.forms import ArtForm
from flask_login import login_required
import datetime as dt


#new artwork
@app.route('/art/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def artNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = ArtForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new post form. 
        # Post() is a mongoengine method for creating a new post. 'newPost' is the variable 
        # that stores the object that is the result of the Post() method.  
        newArt = Art(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            title = form.title.data,
            description = form.description.data,
            artist = current_user.id,
            tag = form.tag.data,
            modifyDate = dt.datetime.utcnow
        )
                # This updates the profile image
        if form.picture.data:
            newArt.picture.put(form.picture.data, content_type = 'image/jpeg')
        # This is a method that saves the data to the mongoDB database.
        newArt.save()

        # Once the new post is saved, this sends the user to that post using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a post so we want 
        # to send them to that post. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('art',artID=newArt.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at postform.html to 
    # see how that works.
    return render_template('postArt.html',form=form)

@app.route('/art/<artID>')
def art(artID):
    thisArt = Art.objects.get(id=artID)
    return render_template('art.html', art = thisArt)
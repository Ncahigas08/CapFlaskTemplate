from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Art
from app.classes.forms import ArtForm, CommentArtForm
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


#Delete Art Post
@app.route('/art/delete/<artID>')
# Only run this route if the user is logged in.
@login_required
def artDelete(artID):
    # retrieve the post to be deleted using the postID
    deleteArtPost = Art.objects.get(id=artID)
    # check to see if the user that is making this request is the author of the post.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteArtPost.author:
        # delete the post using the delete() method from Mongoengine
        deleteArtPost.delete()
        # send a message to the user that the post was deleted.
        flash('The Post was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a post you don't own.")
    # Retrieve all of the remaining posts so that they can be listed.
    apost = Art.objects()  
    # Send the user to the list of remaining posts.
    return render_template('gallery.html',gallery=gallery)

# This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new post based on what the user put in the form.
# Because this route includes a form that both gets and posts data it needs the 'methods'
# in the route decorator.












@app.route('/art/<artID>')
def art(artID):
    thisArt = Art.objects.get(id=artID)
    return render_template('art.html', art = thisArt)

# COMMENTING FOR ART FORM
@app.route('/commentArt/newArt/<artID>', methods=['GET', 'POST'])
@login_required
def CommentArtNew(artID):
    art = Art.objects.get(id=artID)
    artForm = CommentArtForm()
    if artForm.validate_on_submit():
        newComment = CommentArtForm(
            author = current_user.id,
            art = artID, 
            acontent = art.acontent.data
        )
        newComment.save()
        return redirect(url_for('art',artID=artID))
    return render_template('commentArtForm.html', form=form,art=art)


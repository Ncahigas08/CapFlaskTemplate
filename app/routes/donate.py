from xml.etree.ElementTree import Comment
from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Donate, CommentDonate
from app.classes.forms import DonateForm, CommentDonateForm
from flask_login import login_required
import datetime as dt



@app.route('/donate/list')
# This means the user must be logged in to see this page
@login_required
def donateList():
    # This retrieves all of the 'posts' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'posts'.
    donation = Donate.objects()
    # This renders (shows to the user) the posts.html template. it also sends the posts object 
    # to the template as a variable named posts.  The template uses a for loop to display
    # each post.
    return render_template('donation.html',donation=donation)


#new artwork
@app.route('/donate/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def donateNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = DonateForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new post form. 
        # Post() is a mongoengine method for creating a new post. 'newPost' is the variable 
        # that stores the object that is the result of the Post() method.  
        newDonate = Donate(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            title = form.title.data,
            description = form.description.data,
            artist = current_user.id,
            modifyDate = dt.datetime.utcnow
        )
                # This updates the profile image
        
        # This is a method that saves the data to the mongoDB database.
        newDonate.save()

        # Once the new post is saved, this sends the user to that post using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a post so we want 
        # to send them to that post. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('donate',donateID=newDonate.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at postform.html to 
    # see how that works.
    return render_template('postDonate.html',form=form)


#Delete Art Post
@app.route('/donate/delete/<donateID>')
# Only run this route if the user is logged in.
@login_required
def donateDelete(donateID):
    # retrieve the post to be deleted using the postID
    deleteDonatePost = Donate.objects.get(id=donateID)
    # check to see if the user that is making this request is the author of the post.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteDonatePost.artist:
        # delete the post using the delete() method from Mongoengine
        deleteDonatePost.delete()
        # send a message to the user that the post was deleted.
        flash('The Post was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a post you don't own.")
    # Retrieve all of the remaining posts so that they can be listed.
    dpost = Donate.objects()  
    # Send the user to the list of remaining posts.
    return render_template('donation.html',dpost=dpost)

# This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new post based on what the user put in the form.
# Because this route includes a form that both gets and posts data it needs the 'methods'
# in the route decorator.





#edit
@app.route('/donate/edit/<donateID>', methods=['GET', 'POST'])
@login_required
def donateEdit(donateID):
    editDonatePost = Donate.objects.get(id=donateID)
    # if the user that requested to edit this post is not the author then deny them and
    # send them back to the post. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editDonatePost.artist:
        flash("You can't edit a post you don't own.")
        return redirect(url_for('donate',donateID=donateID))
    # get the form object
    form = DonateForm()
    # If the user has submitted the form then update the post.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editDonatePost.update(
            title = form.title.data,
            description = form.description.data,
            modifyDate = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated post using a redirect.
        return redirect(url_for('donate',donateID=donateID))

    # if the form has NOT been submitted then take the data from the editPost object
    # and place it in the form object so it will be displayed to the user on the template.
    form.title.data = editDonatePost.title
    form.description.data = editDonatePost.description

    # Send the user to the post form that is now filled out with the current information
    # from the form.
    return render_template('postDonate.html',form=form)


# COMMENTING FOR ART FORM
@app.route('/commentDonate/newDonate/<donateID>', methods=['GET', 'POST'])
@login_required
def CommentDonateNew(donateID):
    donate = Donate.objects.get(id=donateID)
    form = CommentDonateForm()
    if form.validate_on_submit():
        newDonateComment = CommentDonate(
            author = current_user.id,
            donate = donateID, 
            dcontent = form.dcontent.data
        )
        newDonateComment.save()
        return redirect(url_for('donate',donateID=donateID))
    return render_template('commentDonateForm.html', form=form,donate=donate)

#edit art
@app.route('/commentDonate/editDonate/<commentDonateID>', methods=['GET', 'POST'])
@login_required
def commentDonateEdit(commentDonateID):
    editDonateComment = CommentDonate.objects.get(id=commentDonateID)
    if current_user != editDonateComment.author:
        flash("You can't edit a comment you didn't write.")
        return redirect(url_for('donate',donateID=editDonateComment.donate.id))
    donate = Donate.objects.get(id=editDonateComment.donate.id)
    form = CommentDonateForm()
    if form.validate_on_submit():
        editDonateComment.update(
            dcontent = form.dcontent.data,
            modifydate = dt.datetime.utcnow
        )
        return redirect(url_for('donate',donateID=editDonateComment.donate.id))

    form.dcontent.data = editDonateComment.dcontent

    return render_template('commentDonateForm.html',form=form,donate=donate)   


#delete art
@app.route('/commentDonate/deleteDonate/<commentID>')
@login_required
def commentDonateDelete(commentDonateID): 
    deleteDonateComment = CommentDonate.objects.get(id=commentDonateID)
    deleteDonateComment.delete()
    flash('The comments was deleted.')
    return redirect(url_for('donate',donateID=deleteDonateComment.post.id)) 


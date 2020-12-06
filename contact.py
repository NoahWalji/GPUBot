## Import the Email Helper and Flask
import smtplib

from flask import Flask, render_template, request, Blueprint

## Flask Blueprint
contactPage = Blueprint('contactPage', __name__, template_folder='templates', static_folder="static")

## Main render for the contact form page
@contactPage.route("/contact")
def contact():
    return render_template('contact-form.html')


## Runs whenever someone submits a contact form
@contactPage.route("/contact", methods=["POST"])
def contactSubmission():
    ## Sets the results of the form to the variables
    senderEmail = request.form.get("senderEmail")
    senderSubject = request.form.get("senderSubject")
    senderContents = request.form.get('senderContents')

    ## If any are empty, refuse and produce error
    if (not senderEmail or not senderSubject or not senderContents):
        return render_template('contact-form.html', message= "Error: Please fill out all fields and try again.   ")

    ## Attempt to take contact data, subject and message and send to GPUBot email AND send a confirmation email to the sender
    try:
        ## Produce a message for the team to receive on their email
        message = 'Subject: {}\n\n{}'.format("[GPUBot Client]: " + senderSubject, "Sender Email: " + senderEmail + "\n" + senderContents)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        ## Login to the Sender Email and send the contact email to the team
        server.login("gpubotsender@gmail.com", "cp317assignment")
        server.sendmail("gpubotsender@gmail.com", "gpubotreceiver@gmail.com", message)

        ## From the same email, send the confirmation message to the sender
        message = 'Subject: {}\n\n{}'.format("[GPUBot Client]: " + senderSubject, "Thank you for reaching out to the GPUBot team. We have received your message and will get back to you as soon as possible.")
        server.sendmail("gpubotsender@gmail.com", senderEmail, message)
    
    ## If it fails to send either of the two emails, send an error message
    except:
        return render_template('contact-form.html', message= "Error: Please fill out all fields and try again.   ")

    ## If successful send a successful message
    return render_template('contact-form.html', message= "Success: We have received your message! Please allow us 48 hours to respond.   ")
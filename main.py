## Imports
from flask import Flask, render_template, request
from contact import contactPage
from search import searchPage


## Register the Contact Form in the Main
app = Flask(__name__)
app.register_blueprint(contactPage, url_prefix="")
app.register_blueprint(searchPage, url_prefix="")

if __name__ == '__main__':
    app.run(debug=True,threaded=True)

    

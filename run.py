#!tlkenv/bin/python
#this script starts the development web server with the application

#imports the app variable from the app package
from app import app
#invokes run method of app variable to start server (the app variable holds 
#the Flask instance - assigned in __init__.py)
app.run(debug=True)
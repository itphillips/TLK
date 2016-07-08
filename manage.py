##on 9/6/15, i put the "Manage" functionality into TLK.py--this script is no longer necessary
from flask.ext.script import Manager
from app import app

manager = Manager(app)
app.config['DEBUG'] = True # Ensures debugger will load

if __name__ == '__main__':
	manager.run()
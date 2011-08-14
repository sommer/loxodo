import os
import sys
from optparse import OptionParser
import getpass
import readline
import cmd
import re
import time

from ...db.vault import Vault
from ...config import config
from flask import Flask, session, redirect, url_for, escape, request

DB_PATH="/tmp/test4.db"
DB_FORMAT="v4"

class Webloxodo:
  def __init__(self):
    self.vault = None
    self.vault_file=DB_PATH
    self.vault_format=DB_FORMAT
    self.password = None

app = Flask(__name__)

webloxo = Webloxodo()

@app.route('/')
def index():
    if 'logged_in' in session:
        return 'Logged in as %s' % escape(session['logged_in'])
    return 'You are not authenticated to vault'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
      return 'You have been authenticated to vault already.'
    if request.method == 'POST':
        webloxo.vault = Vault(request.form['password'], filename=webloxo.vault_file, format=webloxo.vault_format)
        print request.form['password']
        print webloxo.vault 
        print webloxo.vault_file
        if webloxo.vault != None:
          session['logged_in'] = request.form['password']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=password>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if its there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "Loxodo.frontends.web.loxodo":
    app.debug = True
    app.run()

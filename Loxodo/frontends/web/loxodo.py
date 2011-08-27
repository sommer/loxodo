import os
import sys
from optparse import OptionParser
import getpass
import readline
import cmd
import re
import time
import hashlib
import base64

from flask import Flask, session, redirect, url_for, escape, request, render_template

from ...db.vault import Vault
from ...config import config

DB_PATH="/tmp/test-v41.db"
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
        name = escape(session['logged_in'])
    else:
        name = None
    return render_template('index.html', name=name)

@app.route('/list')
def list():
  # It might be a good idea to encode passwords in base64 so we do not have
  # them in plaintext in html and use javascript to decode them.
  if ('logged_in' in session) and (webloxo.vault):
    vault_records = webloxo.vault.records[:]
    return render_template('liste.html', vault_records=vault_records)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
      return 'You have been authenticated to vault already.'
    if request.method == 'POST':
        webloxo.password=request.form['password'].encode('utf-8','replace')
        webloxo.vault_file=request.form['vault_path']
        webloxo.vault = Vault(webloxo.password, filename=webloxo.vault_file, format=webloxo.vault_format)
        if webloxo.vault != None:
          session['logged_in'] = request.form['password']
        return redirect(url_for('index'))
    return render_template('open.html', vault_p=DB_PATH)

@app.route('/logout')
def logout():
    # remove the username from the session if its there
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    str_time = time.gmtime(value)
    return time.strftime(format, str_time)

def get_html_id(str):
    return base64.b64encode(hashlib.sha256(str.encode('utf-8','replace')).digest())[3:12]

if __name__ == "Loxodo.frontends.web.loxodo":
    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.filters['get_html_id'] = get_html_id

    app.debug = False
    app.run()

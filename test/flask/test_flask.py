# BrowserID Relying Party Library
# Flask shortcuts test
#
# Copyright (c) 2011 Zach "theY4Kman" Kanzler <they4kman@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import os.path

from browseridrpy.flask_shortcuts import BrowserIDRPyFlask
import flask
from flask import Flask, request, redirect, url_for, session, render_template

app = Flask('browseridrpy-flask-test')

if not os.path.exists('secret_key'):
  with open('secret_key', 'w') as fp:
    app.secret_key = os.urandom(36)
    fp.write(app.secret_key)
else:
  with open('secret_key', 'r') as fp:
    app.secret_key = fp.read()

@app.route('/')
def index():
  return render_template('index.htm')

bid = BrowserIDRPyFlask(app, login_redirect='/')
app.debug = True
app.run()


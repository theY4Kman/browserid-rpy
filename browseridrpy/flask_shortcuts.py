# BrowserID Relying Party Library
# Flask shortcuts
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

import browseridrpy as bidrpy
import flask

def safestring(f):
  def safe(*args, **kwds):
    return flask.Markup(f(*args, **kwds))
  return safe

class BrowserIDRPyFlaskError(Exception):
  pass


class BrowserIDRPyFlask:
  """Handles the routing for BrowserID RPy"""
  
  def __init__(self, app, login_redirect='/', logout_redirect='/'):
    self.app = app
    self.login_redirect = login_redirect
    self.logout_redirect = logout_redirect
    
    self.inject_bidrpy = app.context_processor(self.inject_bidrpy)
    self.login = app.route('/login/', methods=['POST'])(self.login)
    self.logout = app.route('/logout/')(self.logout)
    
    bidrpy.include_script = safestring(bidrpy.include_script)
    bidrpy.include_javascript = safestring(bidrpy.include_javascript)
    bidrpy.include_signin_button = safestring(bidrpy.include_signin_button)
    bidrpy.include_login_callback = safestring(bidrpy.include_login_callback)
    bidrpy.include_login_handler = self.include_login_handler
  
  def inject_bidrpy(self):
    return { 'bidrpy': bidrpy }
  
  def include_login_handler(self):
    return flask.Markup("""\
<script type="text/javascript">
  function post(path, params)
  {
    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", path);

    for (var key in params)
    {
      var field = document.createElement("input");
      field.setAttribute("type", "hidden");
      field.setAttribute("name", key);
      field.setAttribute("value", params[key]);

      form.appendChild(field);
    }

    document.body.appendChild(form);
    form.submit();
  }
  
  function loginSuccess(assertion)
  {
    post('%s', {'assertion': assertion})
  }
</script>
""" % flask.url_for('login')) + bidrpy.include_login_callback()
  
  def login(self):
    if not flask.request.form.has_key('assertion'):
      raise BrowserIDRPyFlaskError('No assertion passed')
    
    a = flask.session['assertion'] = bidrpy.verify_assertion(
      flask.request.form['assertion'], flask.request.environ.get('HTTP_HOST',
      ''))
    flask.session['logged_in'] = a.verified
    
    return flask.redirect(self.login_redirect)
  
  def logout(self):
    if flask.session.has_key('assertion'):
      del flask.session['assertion']
    
    if flask.session.has_key('logged_in'):
      del flask.session['logged_in']
    
    return flask.redirect(self.logout_redirect)

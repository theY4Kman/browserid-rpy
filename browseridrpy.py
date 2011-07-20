# BrowserID Relying Party Library
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

import json
from datetime import datetime
from urllib import quote_plus
from urllib2 import urlopen
from xml.dom import minidom

class AssertionError(Exception):
  pass

class Assertion:
  """Handles the verification of an assertion."""
  
  def __init__(self, assertion, audience):
    self.assertion = assertion
    self.audience = audience
    
    self.verified = False
    self.response = None
    self.status = ''
    self.reason = None
    self.issuer = ''
    
    self.email = ''
    # Unix timestamp
    self._valid_until = None
    # Datetime object
    self.valid_until = None
    
    self.pubkeys = None
    
    self.verify_assertion(self.assertion, self.audience)
    
  def verify_assertion(self, assertion, audience):
    url = 'https://browserid.org/verify?assertion=%s&audience=%s' % (
      quote_plus(assertion), audience)
    http_resp = urlopen(url)
    self.response = json.loads(http_resp.read())
    
    self.status = self.response['status']
    
    if self.status == 'okay':
      self.email = self.response['email']
      self._valid_until = int(float(self.response['valid-until'])/10.0)
      self.valid_until = datetime.fromtimestamp(self._valid_until)
      self.issuer = self.response['issuer']
      
      url = 'https://browserid.org/users/%s.xml' % self.email
      http_resp = urlopen(url)
      try:
        xml = minidom.parseString(http_resp.read())
      except ExpatError:
        raise AssertionError('Could not parse %s as XML' % url)
      
      doc = xml.documentElement
      pubkeys = []
      for node in doc.childNodes:
        if node.nodeName == '#text':
          continue
        
        elif node.nodeName == 'Subject':
          if node.firstChild is None or node.firstChild.nodeName != '#text':
            raise AssertionError('Invalid XML document')
          
          value = node.firstChild.nodeValue
          if value != 'acct:%s' % self.email:
            raise AssertionError('Account name in BrowserID database does not'
              ' match user\'s email')
        
        elif node.nodeName == 'Link':
          if not node.hasAttributes() or not (node.attributes.has_key('rel')
              and node.attributes.has_key('value')):
            raise AssertionError('Invalid XML document')
          
          rel = node.attributes['rel'].nodeValue
          if rel == 'public-key':
            pubkey = node.attributes['value'].nodeValue
            pubkeys.append(pubkey)
      
      self.pubkeys = pubkeys
      self.verified = True
    
    else:
      self.reason = self.response['reason']


def verify_assertion(assertion, audience):
  """Takes an assertion and an audience and returns an Assertion object with all
  the details and user information."""
  return Assertion(assertion, audience)

def is_verified(assertion, audience):
  """Takes an assertion and an audience and returns whether the user has been
  verified."""
  return Assertion(assertion, audience).verified

def include_script():
  """Returns the HTML to include the BrowserID verify.js script"""
  return '<script type="text/javascript" ' \
    'src="https://browserid.org/include.js"></script>'

def include_login_callback(onsuccess='loginSuccess(assertion)',
    onfailure='loginFailure()'):
  """Returns the HTML to handle a click on the Sign In button returned by
  include_signin_button(). The JavaScript code in `onsuccess` is executed if
  the login succeeds, and `onfailure` is called if the login fails."""
  return """\
<script type="text/javascript">
function handleLogin()
{
  navigator.id.getVerifiedEmail(function(assertion) {
    if (assertion)
    {
      %s
    }
    else
    {
      %s
    }
  });
}
</script>""" % (onsuccess, onfailure)

def include_javascript():
  """Returns all the JavaScript necessary to handle BrowserID logins. Assumes
  you have already defined the JavaScript functions loginSuccess(assertion) and
  loginFailure()"""
  return '%s\n%s' % (include_script(), include_login_callback())

def include_signin_button(src, code='handleLogin()'):
  """Returns the HTML necessary to show a sign-in button using the image source
  URL in `src`. The JavaScript in `code` is called when the user clicks it."""
  return """\
<a href="javascript:void()" onclick="%s">
  <img src="%s" />
</a>""" % (src, code)

BrowserID RPy
=============

A Python library that contacts the browserid.org verification service and parses the response for you. It even retrieves the public keys.


How Do I Use It?
-----------------

### As a library

If you already have your web application frontend completed and have the assertion passed by the BrowserID verify.js and the audience, using the library is very simple. To just check whether an assertion has been verified:

    import browseridrpy as rp
    if rp.is_verified(assertion, audience):
      # Assertion verified!
      ...

If you want more detail than that, you can use the `verify_assertion` function to access the underlying `Assertion` object:

    import browseridrpy as rp
    brassert = rp.verify_assertion(assertion, audience)
    
    if brassert.verified:
      # Assertion verified!
      print 'Email:', brassert.email
      print 'Public keys:', brassert.pubkeys
    
    else:
      # Assertion verification failed
      print 'Reason:', brassert.reason

### With [Flask](http://flask.pocoo.org/)

browseridrpy includes Flask shortcuts to make integration easy. You'll need an image for the sign-in button. BrowserID provides a few official-looking ones on [this page](https://browserid.org/developers). In your Python module, import the `flask_shortcuts` module and create a new `BrowserIDRPyFlask` object. This will route `/login/` and `/logout/` to handle logging in and out:

    import flask
    from browseridrpy.flask_shortcuts import BrowserIDRPyFlask
    
    app = Flask()
    bidrpy_flask = BrowserIDRPyFlask(app, login_redirect='/url/to/redirect/after/login', logout_redirect='/url/to/redirect/after/logout')

Then, in your template, use these simple functions to add the JavaScript to handle logging in and the HTML for the sign-in button:

    <!-- Place this in your <head> -->
    <head>
      {{ include_login_handler() }}
    </head>
    
    <!-- And this where you want your login button in the body -->
    <body>
    {% if not session.logged_in %}
      {{ include_signin_button('/url/to/signin_button.png') }}
    {% else %}
      Logged in as {{ session.assertion.email }}. <a href="{{ url_for('logout') }}">Logout</a>.
    {% endif %}
    </body>

That's it! Flask shortcuts uses sessions, so before you can use it, you'll need to define a `secret_key` in your app. See [the Flask docs](http://flask.pocoo.org/docs/quickstart/#sessions) on how to generate a good secret key and assign it. When the user signs in, two entries are added to the session dictionary:

    * `logged_in`: a boolean value; True if the user was verified, False if they're not.
    * `assertion`: a `browseridrpy.Assertion` object. It has three useful attributes:
        * `email`: the email address of the user
        * `pubkeys`: the public keys of the user
        * `valid_until`: a `datetime` object representing the time when the assertion expired. This is not really useful, but fun debug information.
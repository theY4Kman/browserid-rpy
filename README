BrowserID RPy
=============

A Python library that contacts the browserid.org verification service and parses the response for you. It even retrieves the public keys.


How Do I Use It?
-----------------

### As a library

If you already have your web application frontend completed and have the assertion passed by the BrowserID verify.js and the audience, using the library is very simple. To just check whether an assertion has been verified:

    import browserid-rpy as rp
    if rp.is_verified(assertion, audience):
      # Assertion verified!
      ...

If you want more detail than that, you can use the `verify_assertion` function to access the underlying `Assertion` object:

    import browserid-rpy as rp
    brassert = rp.verify_assertion(assertion, audience)
    
    if brassert.verified:
      # Assertion verified!
      print 'Email:', brassert.email
      print 'Public keys:', brassert.pubkeys
    
    else:
      # Assertion verification failed
      print 'Reason:', brassert.reason
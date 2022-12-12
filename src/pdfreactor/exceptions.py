"""
pdfreactor.exception: Exception classes

Hierarchy:

   Exception                            (built-in standard exception)
   `- PDFreactorWebserviceException     (base for this package)
      |- ClientException
      |  |- InvalidServiceException
      |  `- UnreachableServiceException
      |
      |  .----- urllib.error.HTTPError
      `- ServerException

Currently we use only ServerException and UnreachableServiceException actively.
The subclasses of ServerException (from the Java API) have been removed;
instead, we provide read-only properties for ServerExceptions:

- errorId (taken from the X-RO-Error-ID header)
- result (the complete result text)
- pdfreactor_error (if result is a JSON object, the 'error' value)
- pdfreactor_says (to retain information previously injected by the
  PDFreactor._createServerException method)
"""


__all__ = [
    'PDFreactorWebserviceException',
      'ClientException',
        'UnreachableServiceException',
      'ServerException',  # an HTTPError
    ]

# Python compatibility:
import sys
if sys.version_info[0] == 2:
    from urllib2 import HTTPError
    from BaseHTTPServer import BaseHTTPRequestHandler
else:
    from urllib.error import HTTPError
    from http.server import BaseHTTPRequestHandler

import json


class PDFreactorWebserviceException(Exception):
    def __init__(self, message):
        super(PDFreactorWebserviceException, self).__init__(message or "Unknown PDFreactor Web Service error")


class ServerException(HTTPError, PDFreactorWebserviceException):
    """
    There was some error while processing an HTTP request to the PDFreactor server

    We inherit from PDFreactorWebserviceException mainly for systematic reasons;
    for functionality, we rely on the HTTPError details.
    """

    def __init__(self, *args, **kwargs):
        """
        We support the same arguments as the HTTPError "constructor"
        (which isn't a real constructor in Python but rather an initializator);
        for convenience, we accept alternatively an HTTPError object.
        In this case it must be the only given argument!
        """
        if args:
            if not args[1:] and not kwargs and isinstance(args[0], HTTPError):
                e = args[0]
                args = e.url, e.code, e.msg, e.hdrs, e.fp
            HTTPError.__init__(self, *args, **kwargs)
            # super(HTTPError, self).__init__(*args, **kwargs)
        else:
            HTTPError.__init__(self, *args, **kwargs)
            # super(HTTPError, self).__init__(**kwargs)

    @property
    def errorId(self):
        if self.hdrs is None:
            return None
        assert self.headers is not None, 'With .hdrs not None, we have .headers!'
        h = self.headers
        val = h.get('X-RO-Error-ID')
        if val:
            return val
        return '<NO X-RO-Error-ID header found!>'

    @property
    def result(self):
        return self.read().decode('utf-8')

    @property
    def pdfreactor_error(self):
        text = self.result
        if not text:
            return '<result attribute is empty>'
        elif text.startswith(u'<'):
            return '<XML text: %(text)r>' % locals()
        try:
            rslt = json.loads(text)
            if isinstance(rslt, dict):
                return rslt.get('error', '<no error key in response text>')
            else:
                # limit the amount of text; this is about error processing only:
                body = txt[:200]
                tail = txt[200:] and '[...]' or ''
                return ('<no JSON object in response text: %(body)r%(tail)s>'
                        % locals())
        except ValueError:
            return '<no-JSON value %(text)r>' % locals()

    @property
    def pdfreactor_says(self):
        code = self.code
        if code == 400:
            return 'Invalid client data. '+self.pdfreactor_error
        elif code == 401:
            return 'Unauthorized. '+self.pdfreactor_error
        elif code == 404:
            return 'Document with the given ID was not found. '+self.pdfreactor_error
        elif code == 413:
            return 'The configuration is too large to process.'
        elif code in (422, 500):
            return self.pdfreactor_error
        elif code == 503:  # includes Asynchronous conversions, of course:
            return 'PDFreactor Web Service is unavailable.'
        elif code > 400:
            return 'PDFreactor Web Service error (status: %s).' % (self.code,)


class ClientException(PDFreactorWebserviceException):
    def __init__(self, message):
        super(ClientException, self).__init__(message)


class UnreachableServiceException(ClientException):
    def __init__(self, e, url=None):
        super(UnreachableServiceException, self).__init__(str(e))
        self.reason = e
        self.url = url  # the URL we tried (but we didn't get an HTTPError)
        self.args = (e, url)

    def __str__(self):
        url = self.url
        urlinfo = ('; NO URL GIVEN?!' if not url
                   else ' at %(url)s.' % locals())
        reason = ('Reason: ' + str(self.reason)
                  if hasattr(self, 'reason')
                  else 'Error: ' + super(UnreachableServiceException, self).__str__())
        return (self.__class__.__name__
                + ': '
                + 'Error connecting to PDFreactor Web Service'
                + urlinfo
                + '\nPlease make sure the PDFreactor Web Service is installed and running!'
                + '\n('+reason+')')


class InvalidServiceException(ClientException):
    def __init__(self, message):
        super(InvalidServiceException, self).__init__(message)


Code2Descriptions = BaseHTTPRequestHandler.responses

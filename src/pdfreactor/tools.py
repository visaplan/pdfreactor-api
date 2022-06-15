"""
pdfreactor.tools: utility functions
"""

from sys import version_info
if version_info[0] == 2:
    from urllib import quote
else:
    from urllib.parse import quote


def quoted_key(val):
    """
    Quote the given license key for use in the query string (unless quoted)

    Let's assume our license key would look like so:

    >>> key='<license><to>Universal Exports Unltd.</to></license>'

    (Of course real license keys are much longer and look slightly different,
    but you get the idea. For this doctest, we wanted something fitting in a
    line.)

    If we'd simply add this value to our query string, we'd get an error
    because of the contained space character(s), e.g.:
    
      ServerException: HTTP Error 400: Illegal character SPACE=' '

    thus, we need to quote it.

    >>> qkey=quoted_key(key)
    >>> qkey
    '%3Clicense%3E%3Cto%3EUniversal%20Exports%20Unltd.%3C/to%3E%3C/license%3E'

    Wait -- what if we are given pre-quoted values
    (as would have been necessary for the original Python API by RealObjects)?
    Such value we'll take as they are:

    >>> quoted_key(qkey)
    '%3Clicense%3E%3Cto%3EUniversal%20Exports%20Unltd.%3C/to%3E%3C/license%3E'

    Of course we do very superficial tests only; following the GIGO priciple,
    if you don't specify reasonable data, you should know what you do ...

    >>> junk = '%3C'+key[1:]
    >>> quoted_key(junk)
    '%3Clicense><to>Universal Exports Unltd.</to></license>'

    This won't work, of course.
    That's not our fault; you have been warned:
    Either specify something properly quoted, or just the raw value.

    Finally, since the API key is optional, we accept empty values as well
    and return None:

    >>> quoted_key('')
    >>> quoted_key(None)

    """
    if not val:
        return None
    if val.startswith('%3C'):
        return val
    return quote(val)


if __name__ == '__main__':
    from doctest import testmod
    testmod()

"""
pdfreactor._args: options processing helpers
"""

def _sacs(*args, **kwargs):
    """
    Accept two arguments (stream, connectionSettings) and return a 2-tuple
    (stream, connectionSettings)

    Both can be given named; if given unnamed, a dict coming first is prevented
    from being used as a stream.

    The API methods convertAsBinary and getDocumentAsBinary
    both accept a `stream` option which must not be a dict,
    and which might be followed by a connectionSettings dict.
    In Java, we have multiple signatures with type information;
    in Python we have named options instead.

    The first unnamed option is the config dict (which may be None)
    or the documentId; this is handled by the respective method code before
    _sacs is called.

    >>> _sacs()
    (None, None)

    >>> _sacs(None)
    (None, None)

    >>> _sacs({'my': 'connection-settings'})
    (None, {'my': 'connection-settings'})

    >>> _sacs(None, {'some': 'connection-settings'})
    (None, {'some': 'connection-settings'})
    >>> _sacs(None, {'other': 'connection-settings'})
    (None, {'other': 'connection-settings'})

    If a dict is explicitly given as the stream option, this is an error:
    >>> _sacs(None, stream={'rather': 'connection-settings'})
    Traceback (most recent call last):
      ...
    ValueError: stream option must not be a dict!

    Everything can be given by name:
    >>> _sacs(connectionSettings={'my': 'connection'},
    ...       stream=1)
    (1, {'my': 'connection'})

    """
    have_stream = 0
    have_connection = 0
    pop = kwargs.pop
    if 'stream' in kwargs:
        stream = pop('stream')
        have_stream = 1
    if 'connectionSettings' in kwargs:
        connectionSettings = pop('connectionSettings')
        have_connection = 1
    if kwargs:
        unknown = sorted(kwargs.keys())
        many = unknown[1:]
        raise TypeError(('Unsupported keyword arguments (%s [...])' if many
                         else 'Unsupported keyword argument (%s)'
                         ) % (unknown[0],))
    for a in args:
        if not have_stream:
            if isinstance(a, dict):
                if have_connection:
                    raise ValueError('stream option must not be a dict!')
                else:
                    connectionSettings = a
                    have_connection = 1
            else:
                stream = a
                have_stream = 1
        elif not have_connection:
            connectionSettings = a
            have_connection = 1
        else:
            raise TypeError('Surplus unnamed argument %s' % (type(a),))

    if not have_stream:
        stream = None
    elif isinstance(stream, dict):
        raise ValueError('stream option must not be a dict!')
    if not have_connection:
        connectionSettings = None
    return stream, connectionSettings

if __name__ == '__main__':
    from doctest import testmod
    testmod()

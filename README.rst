.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============
pdfreactor-api
==============

Python API for PDFreactor (https://www.pdfreactor.com), a HTML-to-PDF processor.

This distribution package is based on *(and replaces)*
the original API module by RealObjects_.
To make use of it, you need

- a running *PDFreactor* server
- the keys needed to access it;
  depending on the server configuration:

  - the license key (from *RealObjects*; see https://www.pdfreactor.com/buy/)
    (unless installed on the server)

    and / or
  - an API key, if required by the server.


Features
========

- The module ``pdfreactor.api`` contains the Python API version 8
  (based on ``wrappers/python/lib/PDFreactor.py`` from the PDFreactor tarball),
  suitable to talk to PDFreactor server versions 8 to 11.


Modifications
-------------

Here is an overview of the modifications in our distribution,
compared to the original ``PDFreactor.py``.

Structural changes
~~~~~~~~~~~~~~~~~~

- The original `PDFreactor` module from the server distribution tarball is
  called `pdfreactor.api` here.

- The exception classes have been moved
  to the `pdfreactor.exceptions` module.


Compatible changes
~~~~~~~~~~~~~~~~~~

Most code reduction measures don't affect the usage of the PDFreactor class:

- Generic changes to the code, e.g. Python version switches and imports
  (which are executed at runtime in Python) have been moved out of the methods
  to the top of the module.

- Code to handle options is replaced by methods and a helper function:

  - For all methods which use a `config` argument:
    If none is given, create one, to take our client information.

  - The `connectionSettings` option is used by several methods and processed by
    an appropriate method.

  - A few methods accept an optional `stream` argument before another option.
    This is handled by a special function as well.
    Every legitimate usage should continue to work.


Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Reduced the number of exception classes:

  - All classes which inherit from *ServerException* have been **removed**,
    as well as the `PDFreactor._createServerException` method.
  - *ServerException* is an `HTTPError`_ now
    and sports a few additional
    read-only properties to provide the same information.

    This allowed us to greatly simplify the error handling code in the
    conversion methods.

  - If you wish to use all *(remaining)* exception classes of the package,
    import from the `pdfreactor.exceptions` module.


Installation
============

Simply install using ``pip``::

    pip install pdfreactor-api

Or, to integrate in a project built using `zc.buildout`_,
add to your ``buildout.cfg`` script::

    [buildout]
    ...
    eggs =
        pdfreactor-api

and then run ``bin/buildout``.


Related packages
----------------

- pdfreactor.plone_, a Plone_ integration
- pdfreactor.parsecfg_, a configuration parser


Documentation
=============

We expect most questions to be subject to the PDFreactor API documentation;
see:

- `PDFreactor Support Center`_
- `PDFreactor Web service documentation`_


Examples
--------

Some sample scripts by *RealObjects* are (minimally modified)
contained in the ``docs/sample/`` directory:

simple.py
    A sample demonstrating the simple integration of PDFreactor into Python applications
async.py
    A sample demonstrating an asynchronous integration which is recommended for medium to large documents
stream.py
    A sample demonstrating how converted PDFs can be streamed, thus conserving memory


Contribute
==========

(To this API distribution package:)

- Issue Tracker: https://github.com/visaplan/pdfreactor-api/issues
- Source Code: https://github.com/visaplan/pdfreactor-api


Support
=======

If you are having issues *concerning this API distribution*
(e.g. because of a new or modified API version by *RealObjects*),
please let us know;
please use the `issue tracker`_ mentioned above.

For issues regarding the PDFreactor itself, please refer to *RealObjects*.


License
=======

The project is licensed under the MIT License.

.. _HTTPError: https://docs.python.org/3/library/urllib.error.html#urllib.error.HTTPError
.. _`issue tracker`: https://github.com/visaplan/pdfreactor-api/issues
.. _pdfreactor.parsecfg: https://pypi.org/project/pdfreactor.parsecfg
.. _pdfreactor.plone: https://pypi.org/project/pdfreactor.plone
.. _PDFreactor Support Center: https://www.pdfreactor.com/support/
.. _PDFreactor Web service documentation: https://www.pdfreactor.com/product/doc/webservice/
.. _Plone: https://plone.org
.. _RealObjects: https://www.realobjects.com/
.. _zc.buildout: https://pypi.org/project/zc.buildout

.. vim: tw=79 cc=+1 sw=4 sts=4 si et

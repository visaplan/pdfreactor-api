.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============
pdfreactor-api
==============

Python API for PDFreactor (https://www.pdfreactor.com), a HTML-to-PDF processor.

This distribution package is based on the original API module by RealObjects.
To make use of it, you need

- a license key (from `RealObjects`_; see https://www.pdfreactor.com/buy/)
- a running PDFreactor server.

.. _RealObjects: https://www.realobjects.com/


Features
--------

- The module ``pdfreactor.api`` contains the Python API version 8
  (based on ``wrappers/python/lib/PDFreactor.py`` from the PDFreactor tarball),
  suitable to talk to PDFreactor server versions 8 to 11.


Examples
--------

Some sample scripts are contained in the ``docs/sample/`` directory:

simple.py
    A sample demonstrating the simple integration of PDFreactor into Python applications
async.py
    A sample demonstrating an asynchronous integration which is recommended for medium to large documents
stream.py
    A sample demonstrating how converted PDFs can be streamed, thus conserving memory


Documentation
-------------

- `PDFreactor Support Center`_
- `PDFreactor Web service documentation`_

.. _PDFreactor Support Center: https://www.pdfreactor.com/support/
.. _PDFreactor Web service documentation: https://www.pdfreactor.com/product/doc/webservice/

Installation
------------

Simply install using ``pip``::

    pip install pdfreactor-api

Or, to integrate in a project built using `zc.buildout`_,
add to your ``buildout.cfg`` script::

    [buildout]

    ...

    eggs =
        pdfreactor-api

and then run ``bin/buildout``.

.. _zc.buildout: https://pypi.org/project/zc.buildout


Contribute
----------

(To this API distribution package:)

- Issue Tracker: https://github.com/visaplan/pdfreactor-api/issues
- Source Code: https://github.com/visaplan/pdfreactor-api


Support
-------

If you are having issues, please let us know;
please use the `issue tracker`_ mentioned above.


License
-------

The project is licensed under the MIT License.

.. _`issue tracker`: https://github.com/visaplan/PACKAGE/issues

.. vim: tw=79 cc=+1 sw=4 sts=4 si et

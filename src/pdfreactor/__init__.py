# Yes, we are aware of the "recommended approach for the highest level of
# compatibility"; see:
# https://packaging.python.org/en/latest/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages
# ... but it didn't work for us, in our Zope / Plone environment;
# so for now, we stick with the solution which is as well used by Products.CMFPlone.
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

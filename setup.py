# -*- coding: utf-8 -*- vim: et ts=8 sw=4 sts=4 si tw=79 cc=+1
"""Installer for the pdfreactor-api package."""
from __future__ import absolute_import
from __future__ import print_function

from setuptools import find_packages, setup
from os.path import isfile, dirname, abspath, join
from os import chdir, curdir

package_name = 'pdfreactor-api'

mydir = abspath(dirname(__file__))
def read(fn):
    with open(join(mydir, fn)) as fo:
        return fo.read().strip()
# -------------------------------------------- [ get the version ... [
def read_version(fn, sfn):
    backto = abspath(curdir)
    chdir(mydir)
    main = read(fn)
    if sfn is not None and isfile(sfn):
        suffix = valid_suffix(read(sfn))
    else:
        suffix = ''
    chdir(backto)
    return main + suffix
    # ... get the version ...
def valid_suffix(suffix):
    """
    Enforce our suffix convention
    """
    suffix = suffix.strip()
    if not suffix:
        return suffix
    allowed = set('edv.0123456789rcpost')
    disallowed = set(suffix).difference(allowed)
    if disallowed:
        disallowed = ''.join(sorted(disallowed))
        raise ValueError('Version suffix contains disallowed characters'
                         ' (%(disallowed)s)'
                         % locals())
    chunks = suffix.split('.')
    chunk = chunks.pop(0)
    if chunk and not chunk.startswith('rc') and not chunk.startswith('post'):
        raise ValueError('Version suffix must start with "."'
                         ' (%(suffix)r)'
                         % locals())
    if not chunks:
        raise ValueError('Version suffix is too short'
                         ' (%(suffix)r)'
                         % locals())
    for chunk in chunks:
        if not chunk:
            raise ValueError('Empty chunk %(chunk)r in '
                             'version suffix %(suffix)r'
                             % locals())
        char = chunk[0]
        if char in '0123456789':
            raise ValueError('Chunk %(chunk)r of version suffix %(suffix)r'
                             ' starts with a digit'
                             % locals())
        char = chunk[-1]
        if char not in '0123456789':
            raise ValueError('Chunk %(chunk)r of version suffix %(suffix)r'
                             ' doesn\'t end with a digit'
                             ' (normalization would append a "0")'
                             % locals())
    return suffix  # ... valid_suffix
    # ... get the version ...
    # ... get the version ...
VERSION = read_version('VERSION',
                       'VERSION_SUFFIX')
# -------------------------------------------- ] ... get the version ]


# ------------------------------------------- [ for setup_kwargs ... [
long_description = '\n\n'.join([
    read('README.rst'),
    read('CONTRIBUTORS.rst'),
    read('CHANGES.rst'),
])

# see as well --> src/pdfreactor-api/configure.zcml:
namespace = 'pdfreactor'
packages = find_packages('src')

def github_urls(package, **kwargs):
    pop = kwargs.pop
    pkg_list = package.split('.')
    res = {}
    readthedocs = pop('readthedocs', False)
    if readthedocs:
        if readthedocs in (1, True):
            readthedocs = ''.join(pkg_list)
        res['Documentation'] = \
            'https://%(readthedocs)s.readthedocs.io' % locals()
        assert 'docs' not in kwargs
    else:
        docs = pop('docs', None)
        if docs is None:
            res['Documentation'] = 'https://pypi.org/project/%(package)s' \
                                   % locals()
        elif docs:
            res['Documentation'] = docs
    if not pop('github', 1):
        assert not kwargs
        return res
    pop_user = pop('pop_user', False)
    if pop_user:
        assert 'pick_user' not in kwargs
        assert 'user' not in kwargs
        user = pkg_list.pop(0)
        package = '.'.join(pkg_list)
    else:
        pick_user = pop('pick_user', 'user' not in kwargs)
        given_user = pop('user', None)
        if pick_user:
            user = pkg_list[0]
            if given_user is not None and given_user != user:
                raise ValueError('given user %(given_user)r mismatches '
                                 'user picked from package %(user)r!'
                                 % locals())
        elif given_user is not None:
            user = given_user
        else:
            raise ValueError('no user given nor picked!')
    if pop('travis', False):  # reqires github to be trueish
        res.update({  # CHECKME: is there a de-facto standard key for this?
            'Tests': 'https://travis-ci.org/%(user)s/%(package)s' % locals()
            })
    base = 'https://github.com/%(user)s/%(package)s' % locals()
    res.update({
        'Source': base,
        'Tracker': base + '/issues',
        })
    return res
project_urls = github_urls(package_name,
                           user='visaplan')
# ------------------------------------------- ] ... for setup_kwargs ]

setup_kwargs = dict(
    name=package_name,
    version=VERSION,
    description="Python API for PDFreactor",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    author='Tobias Herp',
    author_email='tobias.herp@visaplan.com',
    project_urls=project_urls,
    license='MIT License',
    packages=packages,
    namespace_packages=[namespace],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
)
if 0:
    from pprint import pprint
    del setup_kwargs['long_description']
    pprint(setup_kwargs)
    raise SystemExit(1)
setup(**setup_kwargs)

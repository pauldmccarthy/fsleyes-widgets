#!/usr/bin/env python
#
# setup.py - setuptools configuration for installing the fsleyes-widgets
# package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


from __future__ import print_function

import               os
import os.path    as op
import subprocess as sp
import               shutil
import               pkgutil

from setuptools import setup
from setuptools import find_packages
from setuptools import Command


basedir = op.dirname(__file__)

# Dependencies are listed in requirements.txt
install_requires = open(op.join(basedir, 'requirements.txt'), 'rt').readlines()

packages = find_packages(
    exclude=('doc', 'tests', 'dist', 'build', 'fsleyes_widgets.egg-info'))

# Extract the vesrion number from fsleyes_widgets/__init__.py
version = {}
with open(op.join(basedir, "fsleyes_widgets", "__init__.py"), 'rt') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)
            break
version = version.get('__version__')

with open(op.join(basedir, 'README.md'), 'rt') as f:
    readme = f.read()


class doc(Command):
    """Build the API documentation. """
    
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        docdir  = op.join(basedir, 'doc')
        destdir = op.join(docdir, 'html')

        if op.exists(destdir):
            shutil.rmtree(destdir)

        env   = dict(os.environ)
        ppath = [op.join(pkgutil.get_loader('fsleyes_widgets').filename, '..')]
        
        env['PYTHONPATH'] = op.pathsep.join(ppath)

        print('Building documentation [{}]'.format(destdir))

        sp.call(['sphinx-build', docdir, destdir], env=env) 


setup(

    name='fsleyes-widgets',

    version=version,

    description='A collection of wxPython widgets used by FSLeyes',
    long_description=readme,

    url='https://git.fmrib.ox.ac.uk/paulmc/fsleyes-widgets',

    author='Paul McCarthy',

    author_email='pauldmccarthy@gmail.com',

    license='Apache License Version 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    packages=packages,

    cmdclass={
        'doc' : doc
    },

    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'mock', 'pytest-cov', 'pytest-runner'],
    test_suite='tests',
)

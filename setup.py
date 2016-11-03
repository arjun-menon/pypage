#!/usr/bin/env python

from setuptools import setup

repo_url = 'https://github.com/arjun-menon/pypage'

version_tag = open('docs/version.txt').read().strip()
assert version_tag[0] == 'v'
version = version_tag[1:]

download_url = repo_url + '/archive/' + version_tag + '.tar.gz'

setup(name='pypage',
      version=version,
      description=' Light-weight Python Templating Engine',
      long_description=open('README.rst').read(),
      url=repo_url,
      download_url=download_url,
      author='Arjun G. Menon',
      author_email='contact@arjungmenon.com',
      keywords='templating enigne text processing static generator',
      license='Apache',
      py_modules=['pypage'],
      entry_points={
          'console_scripts': ['pypage=pypage:main'],
      },
      classifiers=[
          'Topic :: Text Processing',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Text Processing :: Markup :: HTML',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Intended Audience :: Developers',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ])

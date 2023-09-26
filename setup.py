#!/usr/bin/env python

from setuptools import setup

from pypage import pypage_version as version

repo_url = 'https://github.com/arjun-menon/pypage'
download_url = '%s/archive/v%s.tar.gz' % (repo_url, version)


def get_long_desc():
    doc_file_name = 'README.rst'
    exclude_lines_with_words = ['toctree', 'maxdepth']

    with open(doc_file_name) as f:
        lines = f.readlines()
        return ''.join(line for line in lines if not any(word in line for word in exclude_lines_with_words))


setup(name='pypage',
      version=version,
      description=' Light-weight Python Templating Engine',
      long_description=get_long_desc(),
      url=repo_url,
      download_url=download_url,
      author='Arjun G. Menon',
      author_email='contact@arjungmenon.com',
      keywords=[
          'templating engine text processing static generator',
          'templating engine',
          'text processing',
          'template',
          'templates'
      ],
      license='Apache-2.0',
      py_modules=['pypage'],
      entry_points={
          'console_scripts': ['pypage=pypage:main'],
      },
      classifiers=[
          'Topic :: Text Processing',
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
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
          'Programming Language :: Python :: 3',
      ])

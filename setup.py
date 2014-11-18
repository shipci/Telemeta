# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests' ,  
                          '--cov' 'telemeta']
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


CLASSIFIERS = ['Environment :: Web Environment',
'Framework :: Django',
'Intended Audience :: Science/Research',
'Intended Audience :: Education',
'Programming Language :: Python',
'Programming Language :: JavaScript',
'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
'Topic :: Multimedia :: Sound/Audio',
'Topic :: Multimedia :: Sound/Audio :: Analysis',
'Topic :: Multimedia :: Sound/Audio :: Players',
'Topic :: Scientific/Engineering :: Information Analysis',
'Topic :: System :: Archiving',  ]


setup(
  name = "Telemeta",
  url = "http://telemeta.org",
  description = "Open web audio application with semantics",
  long_description = open('README.rst').read(),
  author = "Guillaume Pellerin",
  author_email = "yomguy@parisson.com",
  version = '1.5',
  install_requires = [
        'django==1.6.8',
        'django-registration',
        'django-extensions',
        'django-timezones',
        'django-jqchat',
        'django-debug-toolbar',
        'django-extra-views',
        'django-breadcrumbs',
        'django-bootstrap3',
        'django-bootstrap-pagination',
        'timeside>=0.5.6',
        'south',
        'sorl-thumbnail',
        'docutils',
        'psutil',
        'pyyaml',
        'python-ebml',
  ],
  cmdclass={'test': PyTest},
  tests_require=['pytest'],
  dependency_links = ['https://github.com/yomguy/django-json-rpc/tarball/0.6.2',
                      'https://github.com/yomguy/django-dynamic-formset/tarball/master',
                      ],
  platforms=['OS Independent'],
  license='CeCILL v2',
  classifiers = CLASSIFIERS,
  packages = find_packages(),
  include_package_data = True,
  zip_safe = False,
)

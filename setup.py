"""Setup file for python-orcid."""

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)

setup(author='Mateusz Susik',
      author_email='mateuszsusik@protonmail.ch',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Utilities'
      ],
      cmdclass={'test': PyTest},
      description='A python wrapper over the ORCID API',
      install_requires=['html5lib', 'beautifulsoup4', 'requests'],
      keywords=['orcid', 'api', 'wrapper'],
      license='BSD',
      long_description=open('README.rst', 'r').read(),
      name='orcid',
      packages=['orcid'],
      tests_require=['pytest', 'coverage', 'httpretty'],
      url='https://github.com/ORCID/python-orcid',
      version='1.0.3'
      )

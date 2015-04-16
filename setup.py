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
      author_email='mateuszsusik@gmail.com',
      classifiers=[],
      cmdclass={'test': PyTest},
      description='A python wrapper over ORCID API',
      install_requires=['jinja2', 'lxml', 'requests'],
      keywords=['orcid', 'api', 'wrapper'],
      name='orcid',
      package_data={'orcid': ['templates/*.xml']},
      packages=['orcid'],
      tests_require=['pytest'],
      url='https://github.com/MSusik/python-orcid',
      version='0.0'
      )

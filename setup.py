"""Setup file for python-orcid."""

from setuptools import setup
setup(author='Mateusz Susik',
      author_email='mateuszsusik@gmail.com',
      classifiers=[],
      description='A python wrapper over ORCID API',
      install_requires=['jinja2', 'lxml', 'requests'],
      keywords=['orcid', 'api', 'wrapper'],
      name='orcid',
      package_data={'orcid': ['templates/*.xml']},
      packages=['orcid'],
      url='https://github.com/MSusik/python-orcid',
      version='0.0'
      # TO DO
      # download_url='https://github.com/.../tarball/0.1',
      )

"""Setup file for python-orcid."""

from distutils.core import setup
setup(name='orcid',
      packages=['orcid'],
      version='0.0',
      description='A python wrapper over ORCID API',
      author='Mateusz Susik',
      author_email='mateuszsusik@gmail.com',
      url='https://github.com/MSusik/python-orcid',
      # TO DO
      # download_url='https://github.com/.../tarball/0.1',
      keywords=['orcid', 'api', 'wrapper'],
      classifiers=[],
      package_data={'orcid': ['templates/*.xml']}
      )

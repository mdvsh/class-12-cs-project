from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(name='app',
      version='0.0.0',
      author='Madhav and Mehar',
      description='A Terminal User Interface wrapped around an International Admissions Dashboard for Counselor/Teachers/Students',
      long_description='finna speedrun',
      entry_points={
          'console_scripts': [
              'app = app.__main__:main'
          ]
      })

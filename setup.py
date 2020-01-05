from setuptools import setup

setup(name='influxtap',
      version='0.1.0',
      packages=['influxtap'],
      entry_points={
          'console_scripts': [
              'influxtap=influxtap.__main__:main'
          ]
      },
      )


from setuptools import setup

setup(
        name='influxtap',
        description='Daemon-like utility to monitor website responses and push the data into InfluxDB.',
        license='MIT',
        version='0.1.0',
        python_requires='>=3.0',
        author='artanicus',
        author_email='influxtap@nocturnal.fi',
        url='https://github.com/Artanicus/influxtap',
        packages=['influxtap'],
        install_requires=['requests', 'pyyaml', 'absl-py', 'influxdb'],
        entry_points={
          'console_scripts': [
              'influxtap=influxtap.__main__:main'
          ]
        },
      )


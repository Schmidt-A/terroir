from setuptools import setup

setup(
    name='terroir',
    version='0.9',
    description=(
        'Utilities for parsing wine stock at given stores, and fetching review'
        '/rating data from Vivino.'
    ),
    author='Allisa Schmidt',
    author_email='allisa.schmidt@gmail.com',
    packages=['terroir'],
    entry_points={
        'console_scripts': [
            'terroir = terroir:main',
        ],
    },
)
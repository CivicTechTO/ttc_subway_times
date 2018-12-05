"""Packaging logic for ttc_api_scraper."""
from __future__ import generator_stop

import sys

from setuptools import find_packages, setup


def _req_reader(filename):
    with open(filename) as f:
        return [
            requirement
            for requirement in f.read().splitlines()
            if requirement and requirement.strip() and not requirement.strip().startswith('#')
        ]


with open('README.md', 'r') as f:
    long_description = f.read()

requires = _req_reader('requirements.txt')
tests_require = _req_reader('requirements.test.txt')
setup_requires = []
extras_require = {
    'test': tests_require,
}

# Only require pytest-runner for certain setup.py commands
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name='ttc_api_scraper',
    version='0.3',
    description="Script to pull data from the TTC's Subway API and store them in a database",
    long_description=long_description,
    url='https://github.com/CivicTechTO/ttc_subway_times',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requires,
    setup_requires=setup_requires + pytest_runner,
    tests_require=tests_require,
    extras_require=extras_require,
    python_requires='>=3.5.0,<3.7.0',
    entry_points='''
        [console_scripts]
        ttc_api_scraper=ttc_api_scraper.__init__:main
        ''',
    data_files=[
        ('.', ['requirements.txt', 'requirements.test.txt']),
    ],
)

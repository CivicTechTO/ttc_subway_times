import sys

from setuptools import find_packages, setup


def req_reader(filename):
    with open(filename) as f:
        return [
            requirement
            for requirement in f.read().splitlines()
            if requirement and requirement.strip() and not requirement.strip().startswith('#')
        ]


with open('README.md', 'r') as f:
    long_description = f.read()

requires = req_reader('requirements.txt')
tests_require = req_reader('requirements.test.txt')
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
    packages=find_packages(),
    install_requires=requires,
    setup_requires=setup_requires + pytest_runner,
    tests_require=tests_require,
    extras_require=extras_require,
    python_requires='>=3,<3.7.0',
    entry_points='''
        [console_scripts]
        ttc_api_scraper=ttc_api_scraper:main
        '''
)

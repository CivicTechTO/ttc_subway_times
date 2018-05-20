from setuptools import setup, find_packages

setup(
    name='ttc_api_scraper',
    version='0.3',
    description="Script to pull data from the TTC's Subway API and store them in a database",
    packages=find_packages(),
    install_requires=[
        'click',
        'psycopg2',
        'aiohttp',
        'async_timeout',
        'requests'
    ],
    python_requires='>=3',
    entry_points='''
        [console_scripts]
        ttc_api_scraper=ttc_api_scraper:main
        '''
)
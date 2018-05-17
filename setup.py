
from setuptools import setup

requires = [
    'flask',
    'Flask-SQLAlchemy',
    'oursql',
    'flask-cors',
    'flask-testing',
    'requests',
    'Flask-OAuthlib'
]

setup(
    name='Outreach',
    version='2.0',
    install_requires=requires
)

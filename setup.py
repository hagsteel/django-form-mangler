import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="form mangler",
    version="0.1.0",
    author="Jonas Hagstedt",
    author_email="hagstedt@gmail.com",
    description=("Django forms widget mangler"),
    license="BSD",
    keywords="django signup registration",
    url = "https://github.com/jonashagstedt/django-form-mangler",
    packages=['form_mangler', ],
    long_description=read('README.md'),
    install_requires=[
        "Django >= 1.4"
    ],
    classifiers=[
        "Development Status :: Beta",
        "Topic :: Registration",
        "License :: OSI Approved :: BSD License",
    ],
)

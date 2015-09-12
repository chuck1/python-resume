#!/usr/bin/env python

import os

from distutils.core import setup
#from setuptools import setup, find_packages

template_files = list(os.path.join('templates',x) for x in os.listdir('templates'))

setup(
    name='python_resume',
    version='1.1',
    description='Python Resume Generator',
    author='Charles Rymal',
    author_email='charlesrymal@gmail.com',
    url='https://www.github.com/chuck1/python-resume/',
    packages=['python_resume', 'python_resume.user'],
    #package_data={'python_resume':['templates/*']},
    data_files=[
        ('python_resume/templates', template_files),
            ],
    )


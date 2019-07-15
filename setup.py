#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['suds-py3', 'requests', 'requests_ntlm', 'suds-requests @ https://github.com/genusistimelord/suds_requests3/archive/master.zip' ]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pySSRS2',
    version='2.0.0',
    description=('Python SSRS integration'
                 'using SOAP RPCs'),
    long_description=readme + '\n\n' + history,
    author="Fabricio Roberto reinert and Andrew Wheeler",
    author_email='genusistimelord@gmail.com',
    url='https://github.com/genusistimelord/PySSRS/',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='SSRS, Microsoft, Python, SOAP, RPC, Reporting, Services',
    classifiers=[
        'Development Status :: 2 - Release',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests.test_app.tests',
    tests_require=test_requirements
)

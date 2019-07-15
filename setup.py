#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = ['suds-py3', 'requests', 'requests_ntlm', 'suds_requests4' ]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pySSRS2',
    version='2.0.0',
    description=('Python SSRS integration'
                 'using SOAP RPCs'),
    long_description='Fixed version of pySSRS please see git for documentation',
    author="Fabricio Roberto reinert and Andrew Wheeler",
    author_email='genusistimelord@gmail.com',
    url='https://github.com/genusistimelord/PySSRS/',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='SSRS, Microsoft, Python, SOAP, RPC, Reporting, Services',
	python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests.test_app.tests',
    tests_require=test_requirements
)

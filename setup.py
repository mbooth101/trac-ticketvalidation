#!/usr/bin/env python
# Copyright (C) 2010 Mat Booth <mat@matbooth.co.uk>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from setuptools import setup

setup(
    name='TicketValidation',
    version='0.0.1',
    author='Mat Booth',
    author_email='mat@matbooth.co.uk',
    url='https://github.com/mbooth101/trac-ticketvalidation',
    license='BSD',
    description='Support for conditional required and hidden fields in Trac',
    long_description='This plugin adds capability to make built-in and custom ticket fields required or hidden based on a configurable boolean condition.',
    packages=['ticketvalidation'],
    package_data={
        'ticketvalidation' : [
            'htdocs/css/*.css',
            'htdocs/js/*.js',
            'templates/*.html',
            'templates/*.xml',
            ]
        },
    entry_points={
        'trac.plugins': [
           'ticketvalidation.admin = ticketvalidation.admin',
           'ticketvalidation.rules = ticketvalidation.rules',
           ]
        },
    install_requires = [
        'pyparsing>=1.5',
        ],
    )

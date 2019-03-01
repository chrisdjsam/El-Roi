#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'face_recognition_models>=0.3.0',
    'Click>=6.0',
    'dlib>=19.7',
    'numpy',
    'Pillow'
]

test_requirements = [
    'tox',
    'flake8==2.6.0'
]

setup(
    name='El_Roi',
    version='1.2.3',
    description="Recognize faces from Python or from the command line",
    long_description=readme + '\n\n' + history,
    author="Christopher David",
    author_email='chris.dj.sam@gmail.com',
    url='https://github.com/chrisdjsam/El-Roi.git',
    packages=[
        'El_Roi',
    ],
    package_dir={'El_Roi',},
    package_data={},
    entry_points={
        'console_scripts': [
            'imageparser=roi_server_api:main'
        ]
    },
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='face_recognition',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: ',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ]
)

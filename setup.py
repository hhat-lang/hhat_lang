#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open("requirements_dev.txt", "r") as req_dev_file:
    requirements_dev = req_dev_file.read().splitlines()

test_requirements = ['pytest>=3', ]

setup(
    author="Eduardo Maschio",
    author_email='eduardo.maschio@theqube.io',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A core programming language",
    entry_points={
        'console_scripts': [
            'hhat_lang=hhat_lang.cli:main',
        ],
    },
    install_requires=requirements_dev,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='hhat_lang',
    name='hhat_lang',
    packages=find_packages(include=['hhat_lang', 'hhat_lang.*']),
    package_data={"": ["*.hht", "new_grammar.txt"]},
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Doomsk/hhat_lang',
    version='0.1.0',
    zip_safe=False,
)

#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="DaveDeCoder",
    author_email='entrinen@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="simple image cache for holding images in memory",
    entry_points={
        'console_scripts': [
            'image_cache_lru=image_cache_lru.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='image_cache_lru',
    name='image_cache_lru',
    packages=find_packages(include=['image_cache_lru', 'image_cache_lru.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/davedecoder/image_cache_lru',
    version='0.1.0',
    zip_safe=False,
)

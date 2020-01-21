from io import open
from setuptools import find_packages, setup
from version import get_version

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='unladen-chant',
    version=get_version(),
    description='A somewhat arbitrary and heavily opinionated python3 scripting framework which is pretty tedious to use and hard to understand',
    long_description=readme,
    author='mettatw',
    author_email='mettatw@users.noreply.github.com',
    maintainer='mettatw',
    maintainer_email='mettatw@users.noreply.github.com',
    url='https://github.com/mettatw/unladen-chant',
    license='Apache-2.0',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=['colorama', 'tqdm'],
    tests_require=['pytest', 'pytest-forked', 'pytest-cov'],

    packages=find_packages(),
)

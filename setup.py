from setuptools import setup

setup(
    name='Win69Updater',
    version='1.0',
    py_modules=['win69updater'],
    entry_points={
        'console_scripts': [
            'win69updater=win69updater:main',
        ],
    },
)

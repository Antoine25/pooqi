"""
For development purposes, install it with pip install -user -e
or python setup.py develop
"""

from setuptools import setup, find_packages
requirements = ["pandas", "configparser", "PyQt5", "pyqtgraph", "scipy"]

setup(
    version="0.0.1",
    name="pooqi",
    description="Python plotter",
    author="AN",
    packages=find_packages(where='src'),
    include_package_data=True,
    package_dir={
        '': 'src',
    },
    install_requires=requirements,
    entry_points={
        'console_scripts': ['pooqi=pooqi.main:main']
    },
)

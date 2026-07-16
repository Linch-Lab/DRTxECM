__authors__ = 'Francesco Ciucci, Adeleke Maradesa'

__date__ = '26th Jan., 2024'

import setuptools
from os.path import exists, join

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError:
        return ''

entry_points={
        "console_scripts": [
            "launchGUI=pyDRTtools.cli:main",
        ],
    }

dependencies = [
    "cvxopt~=1.3",  # cvxopt optimizer
    "requests~=2.28",  
    "scipy==1.10.0",
    "numpy==1.24.1",
    "scikit-learn>=1.2.1",
    "PyQt5==5.15.9",
    "matplotlib==3.7.3",
    "pandas==1.5.3",
]

setuptools.setup(
    name = "DRTxECM",
    version = "0.2",
    author = "Linch-Lab",
    author_email = "amaradesa@connect.ust.hk",
    description = "DRTxECM: A DRTtools fork with ECM fitting extension — DRT-to-ECM parameter estimation and CPE phase-angle free fitting for Electrochemical Impedance Spectroscopy Data",
    long_description = readme(),
    long_description_content_type = "text/markdown",
    ###
    url = "https://github.com/Linch-Lab/DRTxECM",
    project_urls = {
        "Source Code": "https://github.com/Linch-Lab/DRTxECM",
        "Bug Tracker": "https://github.com/Linch-Lab/DRTxECM/issues",
    },
    entry_points=entry_points,
    #install_requires=dependencies,
    install_requires=[
		'click','ipython'],
    python_requires = ">=3",
    
    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
          
    ],
    packages=['pyDRTtools'],
    include_package_data=True,
    package_data={'pyDRTtools': ['EIS data/*']},  # Specify package data
)

#!/usr/bin/env python3
"""
Setup script for the MPGA GUI application.
"""

from setuptools import setup, find_packages
import os

# Read the version number from __init__.py
with open(os.path.join(os.path.dirname(__file__), '__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

# Read README.md for long description
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='mpga_gui',
    version=version,
    description='GUI for the MultiParametricGA Optimizer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/mpga_gui',
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.0',
        'numpy>=1.18.0',
        'matplotlib>=3.2.0',
    ],
    entry_points={
        'console_scripts': [
            'mpga-gui=mpga_gui.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
    ],
    python_requires='>=3.6',
)

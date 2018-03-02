"""
astrometrica2ades - Converter from Astrometrica output to ADES format
Author
    Tim Lister (tlister@lco.global)
February 2018
"""
from setuptools import setup
import os

setup(name='astrometrica2ades',
      author=['Tim Lister',],
      author_email=['tlister@lco.global',],
      version="0.0.3",
      packages=['astrometrica2ades'],
      package_dir={'astrometrica2ades': 'astrometrica2ades'},
      package_data={'astrometrica2ades': [os.path.join('data', 'config.ini'),
                                          os.path.join('tests', 'data', 'Astrometrica.log'),
                                          os.path.join('tests', 'data', 'MPCReport.txt'),
                                          os.path.join('tests', 'data', 'MPCReport.psv'),
                                          ]},
      setup_requires=['pytest-runner'],
      install_requires=['lxml', 'sphinx', 'sphinx-automodapi', 'numpydoc'],
      tests_require=['pytest'],
      entry_points={'console_scripts': ['astrometrica2ades=astrometrica2ades.main:convert',
                                        ]})

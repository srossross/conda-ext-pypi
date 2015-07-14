'''
'''

import versioneer
from setuptools import setup, find_packages

setup(
    name='conda-ext-pypi',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Sean Ross-Ross',
    author_email='srossross@gmail.com',
    url='http://github.com/anaconda-server/conda-ext-pypi',
    description='Added pip package installs to conda install2',
    packages=find_packages(),
    install_requires=['conda-install2'],
    entry_points={
          'conda.install2.file_type': ['pypi = conda_ext_pypi.pypi_file:PyPIFile'],
          'conda.install2.index': ['pypi = conda_ext_pypi.pypi_index:PyPI'],
    },

)

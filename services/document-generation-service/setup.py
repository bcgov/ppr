from glob import glob
from os.path import basename, splitext
from setuptools import setup, find_packages
from typing import Final


PACKAGE_NAME: Final = 'document-generation-service'


def read_requirements(filename):
    """
    Get application requirements from
    the requirements.txt file.
    :return: Python requirements
    """
    with open(filename, 'r') as req:
        requirements = req.readlines()
    install_requires = [r.strip() for r in requirements if r.find('git+') != 0]
    return install_requires


def read(filepath):
    """
    Read the contents from a file.
    :param str filepath: path to the file to be read
    :return: file contents
    """
    with open(filepath, 'r') as file_handle:
        content = file_handle.read()
    return content


setup(
    name=PACKAGE_NAME,
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,
    license=read('LICENSE'),
    long_description=read('README.md'),
    setup_requires=["pytest-runner", ],
    tests_require=["pytest", ],
)

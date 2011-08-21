from setuptools import setup, find_packages
from simplepyged import __version__

setup(
    name='simplepyged',
    version=__version__,
    description='A simple Python GEDCOM parser',
    long_description=open('README.rst', 'r').read(),
    keywords='gedcom, genealogy',
    author=u'Nikola Škorić',
    author_email='nskoric@gmail.com',
    url='https://github.com/dijxtra/simplepyged/',
    license='GPL',
    package_dir={'simplepyged': 'simplepyged'},
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Sociology :: Genealogy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)


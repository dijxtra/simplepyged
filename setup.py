from setuptools import setup, find_packages
from simplepyged import __version__

setup(
    name='simplepyged',
    version=__version__,
    description='A simple Python GEDCOM parser',
    long_description=open('README.rst', 'r').read(),
    keywords='gedcom, genealogy',
    author=u'Nikola Škorić',
    author_email='',
    url='codekoala at gmail co://github.com/dijxtra/simplepyged/',
    license='GPL',
    package_dir={'simplepyged': 'simplepyged'},
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)


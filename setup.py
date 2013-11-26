from setuptools import setup, find_packages
from setuptools.command.test import test

from django_hstore import get_version


class TestCommand(test):
    def run(self):
        from tests.runtests import runtests
        runtests()


setup(
    name='django-hstore',
    version=get_version(),
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.md').read(),
    author='Anthony Lukach',
    author_email='anthony.lukach@gmail.com',
    license='BSD',
    url='https://github.com/alukach/django-hstore',
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
    cmdclass={"test": TestCommand},
)


import transactional_email
from setuptools import setup, find_packages


def read(f):
    return open(f, 'r', encoding='utf-8').read()


setup(
    name='django-transactional-email',
    version=transactional_email.__version__,
    description='Create, configure and send transactional e-mails with Django.',
    long_description=read('README.md'),
    author='Maarten Huijsmans',
    author_email='maarten@lukin.be',
    url='https://github.com/lukin0110/django-transactional-email/',
    platforms='any',
    packages=find_packages(),
    license='Apache License 2.0',
    zip_safe=False,
    python_requires=">=3.6",
    package_data={
        'transactional_email': [],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
    ],
    install_requires=[],
)

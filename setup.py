from setuptools import setup, find_packages

version = '0.13'

long_description = (
    open('README.rst').read() + '\n\n' + open('CHANGES.rst').read() + '\n')

setup(
    name='imio.zamqp.pm',
    version=version,
    description="PloneMeeting specific methods to use amqp",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='Plone Python IMIO',
    author='IMIO',
    author_email='support@imio.be',
    url='https://github.com/imio/',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['imio', 'imio.zamqp'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'collective.dms.scanbehavior',
        'imio.helpers[pdf]',
        'imio.zamqp.core',
        'Products.PloneMeeting',
    ],
    extras_require={'test': ['Products.PloneMeeting[test]']},
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)

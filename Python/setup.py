#RoboDK API for Python module
#https://robodk.com/doc/en/PythonAPI/index.html
#https://robodk.com/doc/en/RoboDK-API.html#PythonAPI
#https://robodk.com/offline-programming
#https://robodk.com/doc/en/Post-Processors.html

from __future__ import print_function  # (Must be always at the top)
from setuptools import setup  # Always prefer setuptools over distutils
from pathlib import Path

VERSION = '5.6.8'

this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

setup(
    name='robodk',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION,
    description='RoboDK tools for simulating and programming industrial robots (implements the RoboDK API)',
    long_description_content_type='text/markdown',
    long_description=LONG_DESCRIPTION,

    # The project's main homepage.
    url='https://robodk.com/doc/en/PythonAPI/index.html',
    author='RoboDK Inc.',
    author_email='info@robodk.com',

    # Choose your license
    license='Apache Software License',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Scientific/Engineering :: Visualization',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: OS Independent',
        'Framework :: Robot Framework',
        'Framework :: Robot Framework :: Library',
        'Framework :: Robot Framework :: Tool',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: C',
        'Programming Language :: C#',
        'Programming Language :: C++',
        'Programming Language :: Visual Basic',
    ],

    # What does your project relate to?
    keywords='industrial robot, simulation, offline programming, robot programming, robotics, online programming, 3D simulator, post processors',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(),
    packages=['robodk', 'robolink', 'pylint_robodk'],

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'apps': ['PySide2==5.15.*'],
        'cv': ['opencv-contrib-python', 'numpy'],
        'lint': ['astroid'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
)

print("")
print("=============================")
print("RoboDK package (v%s) for Python Installed successfully!" % VERSION)
print("-----------------------------")
print("")
print(LONG_DESCRIPTION)
print("-----------------------------")
print("RoboDK package (v%s) for Python Installed successfully!" % VERSION)
print("=============================")

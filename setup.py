"""medleydb setup script"""
from setuptools import setup
import glob
import imp

version = imp.load_source('medleydb.__version___', 'medleydb/version.py')

data_files = []
data_files.append(('medleydb/resources', glob.glob('medleydb/resources/*')))
data_files.append(('medleydb/data', glob.glob('medleydb/data/*')))


if __name__ == "__main__":
    setup(
        name='medleydb',

        version=version.version,

        description='Python module for the MedleyDB dataset',

        author='Rachel Bittner',

        author_email='rachel.bittner@nyu.edu',

        url='https://github.com/rabitt/medleydb',

        download_url='http://github.com/rabitt/medleydb/releases',

        packages=['medleydb'],

        data_files=data_files,

        classifiers=[
            "License :: The MIT License (MIT)",
            "Programming Language :: Python",
            "Development Status :: 3 - Alpha",
            'Intended Audience :: Telecommunications Industry',
            'Intended Audience :: Science/Research',
            'Environment :: Console',
            'Environment :: Plugins',
            'Topic :: Multimedia :: Sound/Audio :: Analysis',
            'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis'
            'Topic :: Scientific/Engineering :: Information Analysis',
        ],

        keywords='dataset multitrack music',

        license='MIT',

        install_requires=[
            'sox',
            'pyyaml',
            'numpy',
            'six',
            'librosa',
            'pydrive'
        ],

        extras_require={
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
            ],
            'docs': [
                'sphinx==1.2.3',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
        }
    )

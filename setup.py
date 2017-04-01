"""medleydb setup script"""
from setuptools import setup
import imp
import os

version = imp.load_source('medleydb.__version___', 'medleydb/version.py')

package_data = ['resources/*']
os.chdir('medleydb')
package_data.extend(['{0}/*'.format(root)
                    for root, dirs, files in os.walk('data')])
os.chdir('..')

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

        package_data={'medleydb': package_data},

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
            'sox >= 1.2.3',
            'pyyaml >= 3.11',
            'numpy >= 1.8.0',
            'six >= 1.3',
            'librosa >= 0.5.0',
            'pydrive >= 1.3.1',
            'scipy >= 0.13.0',
            'scikit-learn >= 0.18'
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

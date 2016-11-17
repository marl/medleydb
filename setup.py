"""medleydb setup script"""
from setuptools import setup
import glob
import os

metadata = glob.glob("Metadata/*.yaml")

annotation_dirs = glob.glob("Annotations/*")

data_files = [('Metadata', metadata)]
data_files.append(('medleydb/resources', glob.glob('medleydb/resources/*')))
for d in annotation_dirs:
    d_name = os.path.basename(d)
    files = glob.glob(os.path.join(d, "*.*"))
    data_files.append(("Annotations/%s" % d_name, files))
    sub_dir = glob.glob(os.path.join(d, "*_PITCH"))
    if len(sub_dir) > 0:
        sub_dir = sub_dir[0]
        sub_dir_name = os.path.basename(sub_dir)
        sub_dir_files = glob.glob(os.path.join(sub_dir, "*.*"))
        data_files.append(
            ("Annotations/%s/%s" % (d_name, sub_dir_name), sub_dir_files)
        )


if __name__ == "__main__":
    setup(
        name='medleydb',

        version='1.2',

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
            'librosa'
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

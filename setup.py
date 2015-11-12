from setuptools import setup

if __name__ == "__main__":
    setup(
        name='medleydb',

        version='0.2.1',

        description='Python module for the MedleyDB dataset',

        author='Rachel Bittner',

        author_email='rachel.bittner@nyu.edu',

        url='https://github.com/rabitt3/medleydb',

        download_url='http://github.com/rabitt3/medleydb/releases',

        packages=['medleydb', 'medleydb.sql'],

        package_data={'medleydb': ['taxonomy.yaml']},

        long_description="""A python module for audio and music processing.""",

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

        install_requires=['pyyaml'],

        extras_require={
            'sql': [
                'SQLAlchemy'
            ],
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
        },

        entry_points={'console_scripts': [
            'medleydb-export=medleydb.sql:export'
        ]}
    )

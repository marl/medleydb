from setuptools import setup

setup(
    name='medleydb',
    version='0.1.0',
    description='Python module for the MedleyDB dataset',
    author='Rachel Bittner',
    author_email='rachel.bittner@nyu.edu',
    url='https://github.com/rabitt3/medleydb',
    download_url='http://github.com/rabitt3/medleydb/releases',
    packages=['medleydb'],
    package_data={'': ['example_data/*']},
    long_description="""A python module for audio and music processing.""",
    classifiers=[
        "License :: The MIT License (MIT)",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis"
    ],
    keywords='dataset multitrack music',
    license='MIT',
    install_requires=[
        'pyyaml'
    ]
)
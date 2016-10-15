medleydb
========

Annotations and Python tools for MedleyDB. [Read the Docs here](http://medleydb.readthedocs.org).

[![Documentation Status](https://readthedocs.org/projects/medleydb/badge/?version=latest)](http://medleydb.readthedocs.io/en/latest/?badge=latest)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/marl/medleydb/master/LICENSE.md)
[![PyPI](https://img.shields.io/pypi/pyversions/Django.svg?maxAge=2592000)]()

[![Build Status](https://travis-ci.org/marl/medleydb.svg?branch=medleydb_v1.1)](https://travis-ci.org/marl/medleydb)
[![Coverage Status](https://coveralls.io/repos/marl/medleydb/badge.svg?branch=medleydb_v1.1&service=github)](https://coveralls.io/github/marl/medleydb?branch=medleydb_v1.1)

Created by Rachel Bittner rachel (dot) bittner (at) nyu (dot) edu.

This code is released along with MedleyDB:

http://medleydb.weebly.com (or http://marl.smusic.nyu.edu/medleydb)

This code is a component of the work presented in the following publications:

R. Bittner, J. Salamon, M. Tierney, M. Mauch, C. Cannam and J. P. Bello,
"[MedleyDB: A Multitrack Dataset for Annotation-Intensive MIR Research](http://marl.smusic.nyu.edu/medleydb_webfiles/bittner_medleydb_ismir2014.pdf)", in
15th International Society for Music Information Retrieval Conference,
Taipei, Taiwan, Oct. 2014.

R. Bittner, J. Wilkins, H. Yip and J. P. Bello,
"[MedleyDB 2.0: New Data and a System for Sustainable Data Collection](https://wp.nyu.edu/ismir2016/wp-content/uploads/sites/2294/2016/08/bittner-medleydb.pdf)", in
Proceedings of the 17th International Society for Music Information Retrieval Conference Late Breaking and Demo Papers,
New York City, USA, Aug. 2016.

Annotations
===========
As of v1.2, this repository contains the most up to date version of the
medleydb annotations. If you find any problems with an annotation, or would
like to contribute annotations, please report an issue submit a pull request. :)

Setup
=====

First clone this repository:

```bash
git clone https://github.com/rabitt/medleydb.git
```

Install the package

```bash
cd medleydb
pip install -e .
```

Next, set the environment variable MEDLEYDB_PATH to the local path where
the MedleyDB directory (or MedleyDB_sample) lives:

```bash
export MEDLEYDB_PATH="path/to/your/copy/of/MedleyDB"
```

To avoid doing this step every time, copy the line above to ```~/.bash_profile```
or ```~/.bashrc```.

Dependencies
------------

* Python, will be installed by pip
  * [librosa](https://bmcfee.github.io/librosa/)
  * [numpy](http://www.numpy.org/)
  * [pyyaml](http://pyyaml.org/)
  * [sox](http://sox.sourceforge.net/)

If you use homebrew, you can install sox by doing:

```bash
brew install sox  # install the binary
pip install sox  # install the python package
```

medleydb
========

Python tools for using MedleyDB.

Created by Rachel Bittner rachel (dot) bittner (at) nyu (dot) edu
and Justin Salamon justin (dot) salamon (at) nyu (dot) edu.

This code is released along with MedleyDB:

http://medleydb.weebly.com (or http://marl.smusic.nyu.edu/medleydb)

This code is a component of the work presented in the following publication:

R. Bittner, J. Salamon, M. Tierney, M. Mauch, C. Cannam and J. P. Bello,
"[MedleyDB: A Multitrack Dataset for Annotation-Intensive MIR Research](http://marl.smusic.nyu.edu/medleydb_webfiles/bittner_medleydb_ismir2014.pdf)", in
15th International Society for Music Information Retrieval Conference,
Taipei, Taiwan, Oct. 2014.

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

Optionally, you may also install the SQL submodule using

```bash
pip install -e .[sql]
```

And run the database export once

```bash
medleydb-export
```

This will create a `database.sql` file in your `MEDLEYDB_PATH`.

Dependencies
------------

* Python, will be installed by pip
  * [pyyaml](http://pyyaml.org/)
  * [sqlalchemy](http://www.sqlalchemy.org/) (optional)
* Additional
  * [sox](http://sox.sourceforge.net/) (optional)

If you use homebrew, you can install sox by doing:

```bash
brew install sox
```

Usage and Examples
==================

To load the module:

```python
import medleydb as mdb
```

Loading and accessing the full dataset
------------
Load the dataset to a list of MultiTrack objects:

```python
mtrack_generator = mdb.load_all_multitracks()
```

Some attributes of a multitrack:

```python
multitrack_1 = next(mtrack_generator)
multitrack_2 = next(mtrack_generator)

multitrack_1.has_bleed
multitrack_2.has_bleed

multitrack_1.artist
multitrack_2.artist

multitrack_1.is_instrumental
multitrack_2.is_instrumental

multitrack_1.load_melody_annotations()
multitrack_1.melody1_annotation
```

Some attributes of a particular stem:

```python
example_stem = multitrack_1.stems[0]
example_stem.instrument
example_stem.pitch_annotation
```

Loading a subset of the dataset
-------------
A subset of the dataset can be loaded by passing a list of track folder paths:

```python
import glob
import os
import medleydb as mdb

example_list = glob.glob(os.path.join(mdb.AUDIO_PATH, 'ClaraBerry*'))
dataset_subset = mdb.load_multitracks(example_list)
```

Getting filepaths for audio of a chosen instrument
---------------
The following code will get a list of paths to stems that are labeled as a clarinet:

```python
import medleydb as mdb

dataset = mdb.load_all_multitracks()
clarinet_files = mdb.get_files_for_instrument('clarinet')
```

To see a full list of possible instrument labels:

```python
import medleydb as mdb

instruments = mdb.get_valid_instrument_labels()
print instruments
```

medleydb
========

Tools for interacting with MedleyDB.

Created by Rachel Bittner rachel (dot) bittner (at) nyu (dot) edu>
and Justin Salamon justin (dot) salamon (at) nyu (dot) edu

This code is released as part of the MedleyDB library for working
with the MedleyDB dataset: 

http://marl.smusic.nyu.edu/medleydb

This code is a component of the work presented in the following publication:

R. Bittner, J. Salamon, M. Tierney, M. Mauch, C. Cannam and J. P. Bello,
"MedleyDB: A Multitrack Dataset for Annotation-Intensive MIR Research", in
15th International Society for Music Information Retrieval Conference,
Taipei, Taiwan, Oct. 2014.

Setup
========
First clone this repository:
```
git clone https://github.com/rabitt3/medleydb.git
```

MedleyDB must exist for this code to work. To configure, change the following
line in multitrack/config.yaml:

	MEDLEYDB_DIR : 'path/to/your/version/of/MedleyDB'

This will also work for the sample:

	MEDLEYDB_DIR : 'path/to/your/version/of/MedleyDB_sample'

Usage
========
**This will only work once the config.yaml file has been modified**

To load the module:
```python
from medleydb import multitrack as M
```

To load the dataset to a dictionary (keyed by track id):
```python
dataset = M.dataset_utils.load_dataset()
```

To access particular attributes of a single track:
```python
multitrack_1 = dataset['LizNelson_Rainfall']
multitrack_2 = dataset['Phoenix_ScotchMorris']
```

Some attributes of a multitrack:
```python
multitrack_1.has_bleed
multitrack_2.has_bleed
multitrack_1.artist
multitrack_2.artist
multitrack_1.is_instrumental
multitrack_2.is_instrumental
multitrack_1.melody1_annotation
```

To access a particular stem:
```python
example_stem = multitrack_1.stems[0]
example_stem.instrument
example_stem.pitch_annotation
```

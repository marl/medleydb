"""If metadata doesn't have version information, adds it
"""
from __future__ import print_function

import glob
import os
import yaml

from medleydb import METADATA_PATH


def main():
    """Loops over all metadata files and adds version information
    """
    metadata_files = glob.glob(os.path.join(METADATA_PATH, '*.yaml'))
    for fpath in metadata_files:
        with open(fpath, 'r') as fhandle:
            data = yaml.load(fhandle)

        if 'version' not in data.keys():
            data['version'] = 1.2
            with open(fpath, 'w') as fhandle:
                yaml.dump(data, fhandle, indent=2, default_flow_style=False)
        else:
            print("%s has version" % fpath)


if __name__ == "__main__":
    main()

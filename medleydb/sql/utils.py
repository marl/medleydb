import os
import csv
import medleydb.multitrack


def get_rankings(stem):
    """ Get ranking of a single stem.

    """
    rankings_fname = medleydb.multitrack._RANKING_FMT % stem.track.track_id
    rankings_fpath = os.path.join(
        medleydb.multitrack.RANKINGS_DIR,
        rankings_fname
    )

    annotation = []
    with open(rankings_fpath) as f_handle:
        linereader = csv.reader(f_handle)
        for line in linereader:
            annotation.append(line)

    rankings = dict(annotation)
    return rankings.get(stem.annotation_path, None)

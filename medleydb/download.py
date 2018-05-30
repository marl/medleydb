#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Methods for downloading audio from google drive."""
from medleydb import MEDLEYDB_PATH
from medleydb import AUDIO_PATH
from medleydb import GRDIVE_CONFIG_PATH
from medleydb import METADATA_PATH
from medleydb.multitrack import _METADATA_FMT

import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

GAUTH = None
DRIVE = None

FOLDER_MIME = 'application/vnd.google-apps.folder'
BASEDIR_WRITEABLE = False
DOWNLOADED_FILEPATHS = []

GDRIVE_FOLDERS = {
    'V1': '0B72xIeDqCfuUdFhhWUJOb0l2eDg',
    'V2': '0B72xIeDqCfuURlo2M3U4eXhiRmM',
    'EXTRA': '0B72xIeDqCfuULUkySDVQUXhIWGs',
    'BACH10': '0B72xIeDqCfuUQ3FXY2I1cGV4d2c'
}


def authorize_google_drive():
    global GAUTH
    global DRIVE
    if GAUTH is None or DRIVE is None:
        GAUTH = GoogleAuth()
        # Creates local webserver and auto handles authentication.
        GAUTH.LoadClientConfigFile(client_config_file=GRDIVE_CONFIG_PATH)
        GAUTH.LocalWebserverAuth()
        DRIVE = GoogleDrive(GAUTH)
        return True
    else:
        return True


def purge_downloaded_files():
    """Delete all files downloaded this session.
    """
    for fpath in DOWNLOADED_FILEPATHS:
        if os.path.exists(fpath):
            os.remove(fpath)


def check_basedir_writeable():
    """Check if the AUDIO_PATH exists and is writeable.
    If it doesn't exist, this tries to create it.

    Returns
    -------
    status : bool
        True on success

    """
    if MEDLEYDB_PATH is None:
        raise EnvironmentError(
            "The environment variable MEDLEYDB_PATH must be set "
            "to use the download module."
        )

    if not os.path.exists(MEDLEYDB_PATH):
        try:
            os.mkdir(MEDLEYDB_PATH)
        except:
            raise EnvironmentError(
                "The value set for the MEDLEYDB_PATH does not exist and "
                "cannot be created."
            )

    if not os.path.exists(AUDIO_PATH):
        os.mkdir(AUDIO_PATH)

    global BASEDIR_WRITEABLE
    BASEDIR_WRITEABLE = True
    return True


def make_mtrack_basedir(mtrack):
    """Create a multitrack objects' Audio directory structure if it doesn't
    already exist.

    Returns
    -------
    status : bool
        True on success

    """
    if not BASEDIR_WRITEABLE:
        check_basedir_writeable()

    if not os.path.exists(mtrack.audio_path):
        os.mkdir(mtrack.audio_path)

    if not os.path.exists(mtrack._stem_dir_path):
        os.mkdir(mtrack._stem_dir_path)

    if not os.path.exists(mtrack._raw_dir_path):
        os.mkdir(mtrack._raw_dir_path)

    return True


def _download_metadata(track_id, dataset_version):
    """Download a multitracks metadata to the metadata path.

    Parameters
    ----------
    track_id : str
        a track_id
    dataset_version : str
        dataset version identifier string ('V1', 'V2', etc.)

    Returns
    -------
    status : bool
        True on success

    """
    metadata_path = os.path.join(METADATA_PATH, _METADATA_FMT % track_id)
    if os.path.exists(metadata_path):
        return True

    try:
        top_folderid = GDRIVE_FOLDERS[dataset_version]
    except KeyError:
        raise IOError("Unable to find data in Google Drive for this version.")

    file_list = get_named_child(top_folderid, track_id)
    correct_file = [f for f in file_list if f['title'] == track_id]

    if len(correct_file) == 0:
        raise IOError("Could not find multitrack")
    else:
        mtrack_file = correct_file[0]

    metadata_file_list = get_named_child(mtrack_file['id'], 'METADATA')
    if len(metadata_file_list) > 0:
        metadata_file = metadata_file_list[0]
    else:
        folder_file_list = get_files_in_folder(mtrack_file['id'])
        print(len(folder_file_list))
        for fobject in folder_file_list:
            print(fobject['title'])
        raise IOError("Could not find Metadata")

    download_file(metadata_file['id'], metadata_path)

    DOWNLOADED_FILEPATHS.append(metadata_path)

    return True


def download_mix(mtrack):
    """Download a multitracks mix to the mix_path.

    Parameters
    ----------
    mtrack : MultiTrack
        A multitrack object

    Returns
    -------
    status : bool
        True on success

    """

    if os.path.exists(mtrack.mix_path):
        return True

    try:
        top_folderid = GDRIVE_FOLDERS[mtrack.dataset_version]
    except KeyError:
        raise IOError("Unable to find data in Google Drive for this version.")

    file_list = get_named_child(top_folderid, mtrack.title)
    correct_file = [f for f in file_list if f['title'] == mtrack.track_id]

    if len(correct_file) == 0:
        raise IOError("Could not find multitrack")
    else:
        mtrack_file = correct_file[0]

    mix_file_list = get_named_child(mtrack_file['id'], 'MIX')
    if len(mix_file_list) > 0:
        mix_file = mix_file_list[0]
    else:
        raise IOError("Could not find Mix")

    make_mtrack_basedir(mtrack)
    download_file(mix_file['id'], mtrack.mix_path)

    DOWNLOADED_FILEPATHS.append(mtrack.mix_path)

    return True


def download_stem(mtrack, stemid):
    """Download a multitrack's stem to the stem's audio path.

    Parameters
    ----------
    mtrack : MultiTrack
        A multitrack object
    stemid : int
        The stem id to download

    Returns
    -------
    status : bool
        True on success

    """
    stem = mtrack.stems[stemid]

    if os.path.exists(stem.audio_path):
        return True

    try:
        top_folderid = GDRIVE_FOLDERS[mtrack.dataset_version]
    except KeyError:
        raise IOError("Unable to find data in Google Drive for this version.")

    file_list = get_named_child(top_folderid, mtrack.track_id)
    correct_file = [f for f in file_list if f['title'] == mtrack.track_id]

    if len(correct_file) == 0:
        raise IOError("Could not find multitrack")
    else:
        mtrack_file = correct_file[0]

    stem_file_list = get_named_child(mtrack_file['id'], 'STEMS')
    if len(stem_file_list) > 0:
        stem_folder = stem_file_list[0]
    else:
        raise IOError("Could not find stems folder")

    stem_file_list2 = get_named_child(
        stem_folder['id'], os.path.basename(stem.audio_path)
    )
    if len(stem_file_list2) > 0:
        stem_file = stem_file_list2[0]
    else:
        raise IOError("Could not find stem file")

    make_mtrack_basedir(mtrack)
    download_file(stem_file['id'], stem.audio_path)

    DOWNLOADED_FILEPATHS.append(stem.audio_path)

    return True


def download_raw(mtrack, stemid, rawid):
    """Download a specific raw file to the raw track's audio path.

    Parameters
    ----------
    mtrack : MultiTrack
        A multitrack object
    stemid : int
        The raw track's stem id
    rawid : int
        The raw track's id

    Returns
    -------
    status : bool
        True on success

    """
    raw_track = mtrack.raw_audio[stemid][rawid]

    if os.path.exists(raw_track.audio_path):
        return True

    try:
        top_folderid = GDRIVE_FOLDERS[mtrack.dataset_version]
    except KeyError:
        raise IOError("Unable to find data in Google Drive for this version.")

    file_list = get_named_child(top_folderid, mtrack.track_id)
    correct_file = [f for f in file_list if f['title'] == mtrack.track_id]

    if len(correct_file) == 0:
        raise IOError("Could not find multitrack")
    else:
        mtrack_file = correct_file[0]

    raw_file_list = get_named_child(mtrack_file['id'], 'RAW')
    if len(raw_file_list) > 0:
        raw_folder = raw_file_list[0]
    else:
        raise IOError("Could not find raws folder")

    raw_file_list2 = get_named_child(
        raw_folder['id'], os.path.basename(raw_track.audio_path)
    )
    if len(raw_file_list2) > 0:
        raw_file = raw_file_list2[0]
    else:
        raise IOError("Could not find raw file")

    make_mtrack_basedir(mtrack)
    download_file(raw_file['id'], raw_track.audio_path)

    DOWNLOADED_FILEPATHS.append(raw_track.audio_path)

    return True


def get_named_child(parent_id, child_name):
    """Get a file given the id of a parent folder and the title

    Parameters
    ----------
    parent_id : str
        Google drive id of parent folder
    child_name : str
        File name of the child to find.

    Returns
    -------
    file_list : list
        List of files matching the query.

    """
    authorize_google_drive()
    query = "title contains '{}' and trashed=false".format(
        child_name
    )
    file_list = DRIVE.ListFile(
        {'q': query}
    ).GetList()
    return file_list


def get_files_in_folder(folderid):
    """get a list of the files in a google drive folder given the folder id
    """
    authorize_google_drive()
    file_list = DRIVE.ListFile(
        {'q': "'{}' in parents and trashed=false".format(folderid)}
    ).GetList()
    return file_list


def is_folder(file_object):
    """Determine if a google drive file object is a folder or not
    """
    return file_object['mimeType'] == FOLDER_MIME


def download_file(fileid, save_path):
    """Download a google drive fileid to the specified save path.

    Returns
    -------
    status : bool
        True on success

    """
    authorize_google_drive()
    file_object = DRIVE.CreateFile({'id': fileid})
    file_object.GetContentFile(save_path)
    return True


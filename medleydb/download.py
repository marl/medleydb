#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Methods for downloading audio from google drive."""
from medleydb import GDRIVE 

import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

GAUTH = GoogleAuth()
# Creates local webserver and auto handles authentication.
GAUTH.LocalWebserverAuth()
DRIVE = GoogleDrive(GAUTH)
FOLDER_MIME = 'application/vnd.google-apps.folder'


def download_mix(mtrack):
    try:
        top_folderid = GDRIVE[mtrack.dataset_version]
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

    save_path = download_file(
        mix_file['id'], '/Users/rabitt/Desktop/testdownload.wav'
    )
    return save_path



def download_stem(mtrack, stemid):
    pass


def download_raw(mtrack, stemid, rawid):
    pass


def get_named_child(parent_id, child_name):
    """Get a file given the id of a parent folder and the title"""
    query = "'{}' in parents and title contains '{}' and trashed=false".format(
        parent_id, child_name
    )
    file_list = DRIVE.ListFile(
        {'q': query}
    ).GetList()
    return file_list


def get_files_in_folder(folderid):
    file_list = DRIVE.ListFile(
        {'q': "'{}' in parents and trashed=false".format(folderid)}
    ).GetList()
    return file_list


def is_folder(file_object):
    return file_object['mimeType'] == FOLDER_MIME


def download_file(fileid, save_path):
    file_object = DRIVE.CreateFile({'id': fileid})
    file_object.GetContentFile(save_path)
    return save_path


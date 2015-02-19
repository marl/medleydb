#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utils needed from internal MARL repository.
This module requires that SoX is installed.
"""

import logging
import os
import tempfile as tmp
import subprocess

logging.basicConfig(level=logging.DEBUG)

# Error Message for SoX
__NO_SOX = """SoX could not be found!

    If you do not have SoX, proceed here:
     - - - http://sox.sourceforge.net/ - - -

    If you do (or think that you should) have SoX, double-check your
    path variables.
    """


def _sox_check():
    """Test for SoX.
    """
    if not len(os.popen('sox -h').readlines()):
        logging.warning(__NO_SOX)
        return False
    return True


_HAS_SOX = _sox_check()


def assert_sox():
    """Assert that SoX is present and can be called.
    """
    if _HAS_SOX:
        return
    assert False, "SoX assertion failed.\n" + __NO_SOX


def sox(args):
    """Pass an argument list to SoX.

    Args:
        args (list): Argument list for SoX. The first item can, but does not
            need to, be 'sox'.

    Returns:
        status (bool): True on success.

    """
    assert_sox()
    if args[0].lower() != "sox":
        args.insert(0, "sox")
    else:
        args[0] = "sox"

    try:
        logging.info("Executing: %s", "".join(args))
        process_handle = subprocess.Popen(args, stderr=subprocess.PIPE)
        status = process_handle.wait()
        logging.info(process_handle.stdout)
        return status == 0
    except OSError as error_msg:
        logging.error("OSError: SoX failed! %s", error_msg)
    except TypeError as error_msg:
        logging.error("TypeError: %s", error_msg)
    return False


def rm_silence(input_file, output_file,
               sil_pct_thresh=0.1, min_voicing_dur=0.5):
    """Remove silence from an audio file.

    Args:
        input_file (str): Path to input audio file.
        output_file (str): Path to output audio file.
        sil_pct_thresh (float, optional): Silence threshold as percentage of
            maximum sample amplitude.
        min_voicing_duration (float, optional): Minimum amout of time required
            to be considered non-silent.

    Returns:
        status (bool): True on success.

    """
    args = [input_file, output_file]
    args.append("silence")

    args.append("1")
    args.append("%f" % min_voicing_dur)
    args.append("%f%%" % sil_pct_thresh)

    args.append("-1")
    args.append("%f" % min_voicing_dur)
    args.append("%f%%" % sil_pct_thresh)

    return sox(args)


def fade(input_file, output_file, fade_in_time=1, fade_out_time=8,
         fade_shape='q'):
    """Add a fade in or fade out to an audio file. Fade shape is 1/4 sine wave.

    Args:
        input_file (str): Audio file.
        output_file (str): File for writing output.
        fade_in_time (float, optional): Number of seconds of fade in.
        fade_out_time (float, optional): Number of seconds of fade out.
        fade_shape (str, optional): Shape of fade.
            'q' for quarter sine (default),
            'h'for half sine,
            't' for linear,
            'l' for logarithmic
            'p' for inverted parabola.

    Returns:
        status (bool): True on success.

    """
    fade_shapes = ['q', 'h', 't', 'l', 'p']
    assert fade_shape in fade_shapes, "Invalid fade shape."
    assert fade_in_time >= 0, "Fade in time must be nonnegative."
    assert fade_out_time >= 0, "Fade out time must be nonnegative."
    return sox(['sox', input_file, output_file, 'fade', '%s' % fade_shape,
                '%0.8f' % fade_in_time, '0', '%0.8f' % fade_out_time])


def quick_play(input_file, duration=5, use_fade=False, remove_silence=False):
    """Play a short excerpt of an audio file.

    Examples:
        # preview an audio file:
        >>> quick_play('never_gonna_give_you_up.wav')
        # preview an audio file that has long sections of silence:
        >>> quick_play('tuba_stem.wav', remove_silence=True)
        # preview 10 seconds of audio with a fade in and out:
        >>> quick_play('fancy_audio.wav', duration=10, use_fade=True)

    Args:
        input_file (str): Audio file to play.
        duration (float, optional): Length of excerpt in seconds.
        use_fade (bool, optional): If true, apply a fade in and fade out.
        remove_silence (bool, optional): If true, forces entire segment to have
            sound by removing silence.

    """
    ext = os.path.splitext(input_file)[-1]
    tmp_file = tmp.mktemp(suffix=".%s" % ext.strip("."), dir=tmp.gettempdir())
    if remove_silence:
        rm_silence(input_file, tmp_file)
    else:
        tmp_file = input_file

    if not use_fade:
        play(tmp_file, end_t=duration)
    else:
        tmp_file2 = tmp.mktemp(suffix=".%s" % ext.strip("."),
                               dir=tmp.gettempdir())
        fade(tmp_file, tmp_file2, fade_in_time=0.5, fade_out_time=1)
        play(tmp_file2, end_t=duration)


def play(input_file, start_t=0, end_t=None):
    """Play an audio file.

    Specify start/end time to play a particular segment of the audio.

    Examples:
        # to play the whole song:
        >>> play('never_gonna_give_you_up.wav')
        # to play from second 30 to second 60:
        >>> play('never_gonna_give_you_up.wav', start_t=30, end_t=60)

    Args:
        input_file (str): Audio file to play.
        start_t (float, optional): Play start time.
        end_t (float, optional): Play end time.

    Returns:
        status (bool): True if successful.

    """
    assert_sox()

    args = ["play", "--norm", "--no-show-progress", input_file, 'trim',
            "%f" % start_t]
    if end_t:
        args.append("=%f" % end_t)

    logging.info("Executing: %s", "".join(args))
    process_handle = subprocess.Popen(args, stderr=subprocess.PIPE)
    status = process_handle.wait()
    logging.info(process_handle.stdout)

    return status == 0

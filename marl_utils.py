import logging


logging.basicConfig(level=logging.DEBUG)


# Error Message for SoX
__NO_SOX = """SoX could not be found!

    If you do not have SoX, proceed here:
     - - - http://sox.sourceforge.net/ - - -

    If you do (or think that you should) have SoX, double-check your
    path variables."""

def _sox_check():
    """Test for SoX."""

    if not len(os.popen('sox -h').readlines()):
        logging.warning(__NO_SOX)
        return False
    return True


has_sox = _sox_check()


def assert_sox():
    """Assert that SoX is present and can be called."""
    if has_sox:
        return
    assert False, "SoX assertion failed.\n" + __NO_SOX


def play_excerpt(input_file, duration=5, use_fade=False, remove_silence=False):
    """Play an excerpt of an audio file.

    Parameters
    ----------
    input_file : str
        Audio file to play.
    duration : float
        Length of excerpt in seconds.
    use_fade : bool
        If true, apply a fade in and fade out.
    remove_silence: bool
        If true, forces entire segment to have sound by removing silence.
    """
    ext = fu.fileext(input_file)
    tmp_file = temp_file(ext)
    if remove_silence:
        rm_silence(input_file, tmp_file)
    else:
        tmp_file = input_file

    if not use_fade:
        play(tmp_file, end_t=duration)
    else:
        tmp_file2 = temp_file(ext)
        fade(tmp_file, tmp_file2, fade_in_time=0.5, fade_out_time=1)
        play(tmp_file2, end_t=duration)


def play(input_file, start_t=0, end_t=None):
    """Play an audio file.
    Specify start/end time to play a particular segment of the audio.

    Parameters
    ----------
    input_file : str
        Audio file to play.
    start_t : float
        Play start time.
    end_t : float
        Play end time.

    Returns
    -------
    status : bool
        True if successful.
    """
    assert_sox()

    args = ["play"]
    args.append("--norm")
    args.append("--no-show-progress")
    args.append(input_file)
    args.append('trim')
    args.append("%f" % start_t)
    if end_t:
        args.append("=%f" % end_t)

    logging.info("Executing: %s", "".join(args))
    process_handle = subprocess.Popen(args, stderr=subprocess.PIPE)
    status = process_handle.wait()
    logging.info(process_handle.stdout)

    return status == 0
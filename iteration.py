#!/usr/bin/env python
import os
import subprocess
import time
import sys


def git_version():
    """ Produces version string to be used as a point release number
    When working directory is clean will return latest hg revision number
    otherwise will produce revision number followed by constantly increasing
    number and letter M: <revision>-<running-number>M
    """
    try:
        description = subprocess.check_output(
            'git describe --long --tags --dirty=M --match=0.0.0'.split(),
        ).strip()
    except subprocess.CalledProcessError, e:
        sys.stderr.write(
            "***WARNING: Failed to read git revision number. "
            "Make sure the repo is tagged. returning 0***\n")
        return "0"

    _rest, offset, commit = description.rsplit('-', 2)

    if commit.endswith('M'):
        # simple way of getting continuously increasing number:
        # time.strftime('%Y%m%d%H%M%S')
        build_number = time.strftime('%Y%m%d%H%M%S')
        version_template = "{offset}.{build_number}M"
    else:
        version_template = "{offset}"
    return version_template.format(**locals())


if __name__ == "__main__":
    sys.stdout.write(git_version())

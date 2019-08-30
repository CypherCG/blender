#!/usr/bin/env python3
#
# "make update" for all platforms, updating svn libraries and tests and Blender
# git repository and submodules.
#
# For release branches, this will check out the appropriate branches of
# submodules and libraries.

import argparse
import os
import re
import shutil
import subprocess
import sys

from make_utils import call

# Parse arguments

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only-code", action="store_true")
    parser.add_argument("--svn-command", default="svn")
    parser.add_argument("--git-command", default="git")
    return parser.parse_args()

args = parse_arguments()
only_code = args.only_code
git_command = args.git_command
svn_command = args.svn_command

if shutil.which(git_command) is None:
    sys.stderr.write("git not found, can't update code\n")
    sys.exit(1)

if shutil.which(svn_command) is None:
    sys.stderr.write("svn not found, can't update libraries\n")
    sys.exit(1)

def print_stage(text):
    print("")
    print(text)
    print("")

# Test if we are building a specific release version.
try:
    branch = subprocess.check_output([git_command, "rev-parse", "--abbrev-ref", "HEAD"])
except subprocess.CalledProcessError as e:
    sys.stderr.write("Failed to get Blender git branch\n")
    sys.exit(1)

branch = branch.strip().decode('utf8')
release_version = re.search("^blender-v(.*)-release$", branch)
if release_version:
    release_version = release_version.group(1)
    print("Using Release Blender v" + release_version)

# Setup for precompiled libraries and tests from svn.
if not only_code:
    lib_dirpath = os.path.join('..', 'lib')

    if release_version:
        svn_branch = "tags/blender-" + release_version + "-release"
    else:
        svn_branch = "trunk"
    svn_url = "https://svn.blender.org/svnroot/bf-blender/" + svn_branch + "/lib/"

    # Checkout precompiled libraries
    if sys.platform == 'darwin':
        lib_platform = "darwin"
    elif sys.platform == 'win32':
        # Windows checkout is usually handled by bat scripts since python3 to run
        # this script is bundled as part of the precompiled libraries. However it
        # is used by the buildbot.
        lib_platform = "win64_vc14"
    else:
        # No precompiled libraries for Linux.
        lib_platform = None

    if lib_platform:
        lib_platform_dirpath = os.path.join(lib_dirpath, lib_platform)

        if not os.path.exists(lib_platform_dirpath):
            print_stage("Checking out Precompiled Libraries")

            svn_url_platform = svn_url + lib_platform
            call([svn_command, "checkout", svn_url_platform, lib_platform_dirpath])

    # Update precompiled libraries and tests
    print_stage("Updating Precompiled Libraries and Tests")

    if os.path.isdir(lib_dirpath):
      for dirname in os.listdir(lib_dirpath):
        if dirname == ".svn":
            continue

        dirpath = os.path.join(lib_dirpath, dirname)
        svn_dirpath = os.path.join(dirpath, ".svn")
        svn_root_dirpath = os.path.join(lib_dirpath, ".svn")

        if os.path.isdir(dirpath) and \
           (os.path.exists(svn_dirpath) or os.path.exists(svn_root_dirpath)):
            call([svn_command, "cleanup", dirpath])
            call([svn_command, "switch", svn_url + dirname, dirpath])
            call([svn_command, "update", dirpath])

# Update blender repository and submodules.
print_stage("Updating Blender Git Repository and Submodules")

call([git_command, "pull", "--rebase"])
call([git_command, "submodule", "update", "--init", "--recursive"])

if not release_version:
    # Update submodules to latest master if not building a specific release.
    # In that case submodules are set to a specific revision, which is checked
    # out by running "git submodule update".
    call([git_command, "submodule", "foreach", "git", "checkout", "master"])
    call([git_command, "submodule", "foreach", "git", "pull", "--rebase", "origin", "master"])
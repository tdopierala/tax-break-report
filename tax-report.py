# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
Tax Break Script v1.6 (tax-report.py)

Usage:
python tax-report.py -s YYYY-MM-DD -e YYYY-MM-DD -a USERNAME -d PROJECT_DIR -o OUTPUT_DIR -f -v

Options:
  -s START, --start=START       Start date. DEFAULT: First day of the current month.
  -e END, --end=END             End date. DEFAULT: Today.
  -a AUTHOR, --author=AUTHOR    Commit author's git username. DEFAULT: user.name from .gitconfig.
  -d DIR, --dir=DIR             Project directory (relative path). DEFAULT: DEFAULT_PROJECT_DIRECTORY global variable's value.
  -o OUT, --out=OUT             Output directory. DEFAULT: Today.
  -c COMMIT, --commit=COMMIT    SHA of a specific commit to be saved. DEFAULT: None.
  -b BRANCH, --branch=BRANCH    Name of the branch. DEFAULT: None (all branches are taken into account).
  -f, --full                    Save full paths to files. DEFAULT: False.
  -v, --verbose                 Print additional information.
  --debug                       Print additional information and debug messages.
  
Example:
  python tax-report.py -a tdopierala -d admin -s 2018-06-01 -f
'''

import os
import sys
import platform
from datetime import date
import subprocess
import optparse
import logging


DEFAULT_PROJECT_DIRECTORY = "project"
EXCLUDED_DIRS = [ "node_modules", "package-lock.json", "favicon.ico" ]

RETARDED = sys.version_info < (3, 0, 0, 0, 0)
SHELL_ON = platform.system() == 'Linux'
MAX_ABS_PATH_LEN = 250


def save_content_to_file(content, path):
    with open(path, "wb") as f:
        if not RETARDED:
            f.write(bytes(content, "UTF-8"))
        else:
            f.write(content)


def save_diff(githash, path):
    logging.debug("Running: git show {0}".format(githash))
    file_content = subprocess.check_output("git show {0}".format(githash), shell = SHELL_ON).decode()
    logging.info("Saving diff from hash: {0}".format(githash))
    save_content_to_file(file_content, os.path.join(path, "diff.diff"))


def save_complete_modified_files(githash, path, save_full):
    logging.debug("Running: git show --pretty="" --name-status {0}".format(githash))
    files = subprocess.check_output("git show --pretty="" --name-status {0}".format(githash), shell = SHELL_ON).decode().split("\n")[:-1]
    files = [(x.split("\t")[0], x.split("\t")[-1]) for x in files]
    logging.debug("File list: {0}".format(files))
    for (status, file) in files:
        logging.debug("{0} - {1}".format(status, file))
        if len(list(filter(lambda x: file.startswith(x + "/"), EXCLUDED_DIRS))):
            logging.info("Skipping {0} (excluded directory).".format(file))
            continue
        try:
            if status != "D":
                logging.debug("Running: git show {0}:\"{1}\"".format(githash, file))
                file_content = subprocess.check_output("git show {0}:\"{1}\"".format(githash, file), shell = SHELL_ON).decode()
            else:
                logging.debug("Running: git show {0}~1:\"{1}\"".format(githash, file))
                file_content = subprocess.check_output("git show {0}~1:\"{1}\"".format(githash, file), shell = SHELL_ON).decode()
                file += ".DELETED"
            file_path = os.path.join(path, os.path.basename(file))
            if save_full:
                file_path = os.path.join(path, os.path.relpath(file))
                file_path_len = len(os.path.abspath(file_path))
                if(file_path_len <= MAX_ABS_PATH_LEN):
                    if not os.path.exists(os.path.dirname(file_path)):
                        os.makedirs(os.path.dirname(file_path))
                else:
                    logging.warning("Absolute path too long ({0} characters): {1}".format(file_path_len, file_path))
                    file_path = os.path.join(path, os.path.basename(file))
            logging.info("Saving file {0} to {1}".format(file, file_path))
            save_content_to_file(file_content, file_path)
        except subprocess.CalledProcessError:
            logging.error("Cannot read file {0}".format(file))
        except UnicodeDecodeError:
            logging.error("Cannot decode file {0}".format(file))


def provide_python_2_compatibility():
    if not RETARDED:
        logging.info("Using Python 3.x")
        return
    logging.info("Using Python 2.x")
    reload(sys)
    sys.setdefaultencoding('utf8')


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-s", "--start", type = "string", default = str(date.today().replace(day = 1)), help = "Start date. DEFAULT: First day of the current month.")
    parser.add_option("-e", "--end", type = "string", default = str(date.today()), help = "End date. DEFAULT: Today.")
    parser.add_option("-a", "--author", type = "string", default = None, help = "Commit author's git username. DEFAULT: user.name from .gitconfig.")
    parser.add_option("-d", "--dir", type = "string", default = DEFAULT_PROJECT_DIRECTORY, help = "Project directory (relative path). DEFAULT: DEFAULT_PROJECT_DIRECTORY global variable's value.")
    parser.add_option("-o", "--out", type = "string", default = str(date.today()), help = "Output directory. DEFAULT: Today.")
    parser.add_option("-c", "--commit", type = "string", default = None, help = "SHA of a specific commit to be saved. DEFAULT: None.")
    parser.add_option("-b", "--branch", type = "string", default = None, help = "Name of the branch. DEFAULT: --branches (all branches are taken into account).")
    parser.add_option("-f", "--full", action = "store_true", dest = "full", default = False, help = "Save full paths to files. DEFAULT: False.")
    parser.add_option("-v", "--verbose", action = "store_const", dest = "log_level", const = logging.INFO, default = logging.WARNING, help = "Print additional informations.")
    parser.add_option("--debug", action = "store_const", dest = "log_level", const = logging.DEBUG, default = logging.WARNING, help = "Print additional informations and debug messages.")
    opt, _ = parser.parse_args()

    logging.basicConfig(format = "%(levelname)s: %(message)s", stream = sys.stdout, level = opt.log_level)
    logging.info("Verbose mode is ON.")
    logging.debug('Debug mode is ON.')
    
    provide_python_2_compatibility()
    
    os.chdir(opt.dir)
    
    if not opt.author:
        try:
            command = "git config --global user.name"
            logging.debug("Running: {0}".format(command))
            opt.author = subprocess.check_output(command, shell = SHELL_ON).decode("UTF-8").replace("\n", "")
            logging.debug("Author name retrieved: {0}".format(opt.author))
        except subprocess.CalledProcessError:
            logging.error("Cannot retrieve user.name from .gitconfig.")
            exit()
    
    if opt.commit:
        logging.info("Saving only the following commit: {0}".format(opt.commit))
        log = [opt.commit + "--"]
        try:
            logging.debug("Running: git show -s --format=%cd --date=short {0}".format(opt.commit))
            log[0] += subprocess.check_output("git show -s --format=%cd --date=short {0}".format(opt.commit), shell = SHELL_ON).decode()
        except subprocess.CalledProcessError:
            logging.error("Unknown commit SHA: {0}".format(opt.commit))
            exit()
    else:
        if not opt.branch:
            command = "git log --branches --since=\"{0} 00:00:00\" --until=\"{1} 23:59:59\" --author=\"{2}\" --date=short-local --pretty=format:%H--%ad".format(opt.start, opt.end, opt.author)
            logging.debug("Running: {0}".format(command))
            log = subprocess.check_output(command, shell = SHELL_ON).decode().split()
        else:
            try:
                command = "git log {0} --first-parent --since=\"{1} 00:00:00\" --until=\"{2} 23:59:59\" --author=\"{3}\" --date=short-local --pretty=format:%H--%ad".format(opt.branch, opt.start, opt.end, opt.author)
                logging.debug("Running: {0}".format(command))
                log = subprocess.check_output(command, shell = SHELL_ON).decode().split()
            except subprocess.CalledProcessError:
                logging.error("Unknown branch name: {0}".format(opt.branch))
                exit()

    for commit in log:
        logging.info("******************************************************\n\n")
        githash, date = commit.split("--")
        logging.info("Commit {0} from {1}".format(githash, date))
        out_path = os.path.join(os.pardir, opt.out, str(githash))
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        save_diff(githash, out_path)
        save_complete_modified_files(githash, out_path, opt.full)

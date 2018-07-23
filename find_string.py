#!/usr/bin/env python
"""Find a given string in any file in this branch (can limit file types and directories searched)

usage: ./bin/find_string_in_branch "<string>" [-e <file extension limiter>] [-d <directory limiter>] [-i] [-c]

Created by: Teddy Williams
Date: 6/29/18

Arguments:
    <string>: This is the string that is searched for across all directories/files

Optional Arguments (can be combined):
    -e <file extension>:    limits string search to only specific file extensions
        example:            ./find_string.py "interesting string" -e .py

    -d <directory>:         limits string search to a specific sub-directory of main branch
        example:            ./find_string.py "interesting string" -d test/functional

    -i:                     will ignore everything after '#' in a line
        example:            ./find_string.py "interesting string" -i

    -c:                     make search case insensitive
        example:            ./find_string.py "interesting string" -i

    -h                      Display this help message
        example:            ./find_string.py -h
"""


from __future__ import print_function
from collections import OrderedDict
import os
import sys


def traverse_files(dir_path, string, file_extension='', ignore_comments=False,
                   case_insensitive=False, dictionary={}):
    """ Traverse all directories in branch, loop through all files therein. """
    for root, dirs, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith(file_extension):
                file_path = root + '/' + file_name
                search_file(file_path, string, ignore_comments, case_insensitive, dictionary)


def search_file(file_path, string, ignore_comments, case_insensitive, dictionary):
    """ Search through files to find string instances. Add file name and line numbers where string was found """
    with open(file_path, 'r') as f:
        line_count = 0
        for line in f:
            line_count += 1
            if case_insensitive:
                string = string.lower()
                line = line.lower()
            if string in line:
                if ignore_comments and "#" in line:
                    pre_comment_line = line.split('#')[0]
                    if string in pre_comment_line:
                        add_to_dictionary(file_path, line_count, dictionary)
                else:
                    add_to_dictionary(file_path, line_count, dictionary)


def add_to_dictionary(file_path, line_count, dictionary):
    """ Add the line file and line of string occurrence to specified dictionary"""
    if file_path in file_line_dict:
        dictionary[file_path].append(line_count)
    else:
        dictionary[file_path] = [line_count]


if __name__ == "__main__":
    # Create dict to hold the string's file names and line locations
    file_line_dict = dict()

    # Default to look in all directories and files
    file_extension = ''
    directory = ''

    usage_string = 'Usage: ./bin/find_string_in_branch "<string>" ' \
                   '[-e <file extension limiter>] [-d <directory limiter>] [-i] [-c]'

    # Default arguments
    case_insensitive = False
    ignore_comments = False

    # sort command line arguments to get string (and optional limiting file_extension and directory)
    if len(sys.argv) == 1 or len(sys.argv) > 8:
        sys.exit(usage_string)
    # print help message if called for
    if sys.argv[1] == '-h':
        sys.exit(__doc__)
    # Sort through args in for loop
    for index, arg in enumerate(sys.argv):
        try:
            if arg == '-e':
                file_extension = sys.argv[index+1]
                if file_extension[0] != '.':
                    sys.exit("{} is not a recognized file extension".format(file_extension))
            if arg == '-d':
                directory = sys.argv[index+1]
                directory = '/' + directory.strip('/')
            if arg == '-i':
                ignore_comments = True
            if arg == '-c':
                case_insensitive = True
            if arg == '-i' or arg == '-c':
                try:
                    if (sys.argv[index+1][0] != '-') and (len(sys.argv[index+1]) != 2):
                        sys.exit(usage_string)
                except IndexError:
                    pass  # means no more arguments after '-i' or '-c' which is okay
            if arg[0] == '-' and arg not in ('-e', '-d', '-i', '-c'):
                sys.exit(usage_string)
            if arg[0] != '-' and index > 1:
                if sys.argv[index-1] not in ('-e', '-d', '-i', '-c'):
                    sys.exit(usage_string)

        except IndexError:
            sys.exit(usage_string)

    string = sys.argv[1]

    # Want to look at all files relative to where this script is run
    root_dir_path = str(os.path.realpath(os.getcwd()))
    # Then limit path to specified sub-directory
    dir_path = root_dir_path + directory

    traverse_files(dir_path, string, file_extension, ignore_comments, case_insensitive, file_line_dict)

    if len(file_line_dict) == 0:
        print('\n"{}" not found'.format(string))
    else:
        # Order our dictionary alphabetically by document names
        ordered_file_line_dict = OrderedDict(sorted(file_line_dict.items()))
        print('\n{} files with "{}" found:\n'.format(len(file_line_dict), string))
        for index, key in enumerate(ordered_file_line_dict):
            print('{}. {} -> lines: {}'.format(
                index + 1, key[len(root_dir_path)+1:], ordered_file_line_dict[key]))
        print()

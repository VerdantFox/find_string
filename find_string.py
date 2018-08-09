#!/usr/bin/env python
"""Find a given string in any file in this branch (can limit file types and directories searched)

usage: ./bin/find_string_in_branch "<string>" [-e <file extension limiter>] [-d <directory limiter>] [-i] [-c] [-s]

Created by: Teddy Williams
Date: 6/29/18
Last updated: 8/9/18

Arguments:
    <string>: This is the string that is searched for across all directories/files

Optional Arguments (can be combined):
    -e, --extension <file extension>:   limits string search to only specific file extensions
        example:                        find_string.py "interesting string" -e .py

    -d, --directory <directory>:        limits string search to a specific sub-directory of main branch
        example:                        find_string.py "interesting string" -d test/functional

    -i:                                 will ignore everything after '#' in a line
        example:                        find_string.py "interesting string" -i

    -c:                                 make search case insensitive
        example:                        find_string.py "interesting string" -c

    -s:                                 will show the line containing found string
        example:                        find_string.py "interesting string" -s

    --help                              Display help message
        example:                        find_string.py -h
"""
from __future__ import print_function
from collections import OrderedDict
import os
import click


options_string = '[-e <file extension limiter>] [-d <directory limiter>] [-i] [-c] [-s]'


@click.command(options_metavar=options_string)
@click.argument('string_to_find', nargs=1, metavar="'<string to find>'")
@click.option('-e', '--extension', 'extension', default='', metavar='<file extension>')
@click.option('-d', '--directory', 'directory', default='', metavar='<relative directory>')
@click.option('-i', '--ignore-comments', 'ignore_comments', is_flag=True)
@click.option('-c', '--case-insensitive', 'case_insensitive', is_flag=True)
@click.option('-s', '--show-line', 'show_line', is_flag=True)
def find_string(string_to_find, extension, directory, ignore_comments, case_insensitive, show_line):
    """Find a string in file system relative to current working directory"""
    string_to_find = str(string_to_find)
    extension = str(extension)
    directory = str(directory)

    # prep args
    if extension != '' and extension[0] != '.':
        raise click.BadParameter("'{}' is not a recognized file extension. (example extension = '.py')".format(extension))
    if directory != '':
        directory = '/' + directory.strip('/')
    # Create dict to hold the string's file names and line locations
    file_line_dict = dict()
    # Want to look at all files relative to where this script is run
    root_dir_path = str(os.path.realpath(os.getcwd()))
    # Then limit path to specified sub-directory
    dir_path = root_dir_path + directory
    # Check if directory exists
    if not os.path.isdir(dir_path):
        raise click.BadParameter("The directory {} does not exist!".format(dir_path))

    traverse_files(dir_path, string_to_find, extension,
                   ignore_comments, case_insensitive, file_line_dict)
    print_output(file_line_dict, string_to_find, root_dir_path, show_line)
    return file_line_dict


def traverse_files(dir_path, string_to_find, extension, ignore_comments,
                   case_insensitive, file_line_dict):
    """ Traverse all directories in branch, loop through all files therein. """
    for root, dirs, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith(extension):
                file_path = root + '/' + file_name
                search_file(file_path, string_to_find, ignore_comments,
                            case_insensitive, file_line_dict, extension)


def search_file(file_path, string_to_find, ignore_comments, case_insensitive, file_line_dict, extension):
    """ Search through files to find string instances. Add file name and line numbers where string was found """
    if ignore_comments and extension == '':
        split_filename = file_path.split('/')[-1].split('.')
        if len(split_filename) > 1:
            extension = split_filename[-1]
            extension = '.' + extension
    in_comment = False
    with open(file_path, 'r') as f:
        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1 and ignore_comments and extension == '':
                if '#!' in line:
                    if 'bash' in line:
                        extension = '.sh'
                    elif 'python' in line:
                        extension = '.py'
            if case_insensitive:
                string_to_find = string_to_find.lower()
                line = line.lower()
            if string_to_find in line:
                if ignore_comments:
                    if extension == '.py' or extension == '.sh':
                        if '"""' in line and in_comment is False:
                            in_comment = True
                        if not in_comment:
                            if "#" in line:
                                pre_comment_line = line.split('#')[0]
                                if string_to_find in pre_comment_line:
                                    add_to_dictionary(file_path, line, line_count, file_line_dict)
                            else:
                                add_to_dictionary(file_path, line, line_count, file_line_dict)
                        if '"""' in line and in_comment is True:
                            in_comment = False
                    elif extension == '.xqy':
                        if '(:' in line:
                            in_comment = True
                            pre_comment_line = line.split('(:')[0]
                            if string_to_find in pre_comment_line:
                                add_to_dictionary(file_path, line, line_count, file_line_dict)
                        if not in_comment:
                            add_to_dictionary(file_path, line, line_count, file_line_dict)
                        if ':)' in line:
                            in_comment = False
                    else:
                        add_to_dictionary(file_path, line, line_count, file_line_dict)
                else:
                    add_to_dictionary(file_path, line, line_count, file_line_dict)


def add_to_dictionary(file_path, line, line_count, file_line_dict):
    """ Add the line file and line of string occurrence to specified dictionary"""
    if file_path in file_line_dict:
        file_line_dict[file_path].append((line_count, line))
    else:
        file_line_dict[file_path] = [(line_count, line)]


def print_output(file_line_dict, string, root_dir_path, show_line):
    if len(file_line_dict) == 0:
        click.echo('\n"{}" not found\n'.format(string))
    else:
        # Order our dictionary alphabetically by document names
        ordered_file_line_dict = OrderedDict(sorted(file_line_dict.items()))
        click.echo('\n{} files with "{}" found:\n'.format(len(file_line_dict), string))
        for index, key in enumerate(ordered_file_line_dict):
            if show_line:
                click.echo('{}. {}:'.format(index + 1, key[len(root_dir_path)+1:],))
                # for i, line_number, line in enumerate(ordered_file_line_dict[key]):
                for line_number, line in ordered_file_line_dict[key]:
                    line = line.strip('\t').strip('\n').strip(' ')
                    click.echo('\tline {line_number}: {line}'.format(
                        line_number=line_number, line=line))
            else:
                click.echo('{}. {} -> lines: {}'.format(
                    index + 1,
                    key[len(root_dir_path)+1:],
                    [ordered_file_line_dict[key][i][0] for i, j in enumerate(ordered_file_line_dict[key])],
                ))
        click.echo()


if __name__ == "__main__":
    find_string()

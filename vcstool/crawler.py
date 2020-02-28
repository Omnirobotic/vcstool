import os
import re

from . import vcstool_clients


def find_repositories(paths, nested=False):
    current_directory = os.curdir
    vcs_ignore_path = os.path.join(current_directory, ".vcsignore")
    exclude_list = []
    if os.path.exists(vcs_ignore_path):
        exclude_list = [line.rstrip('\n') for line in open(vcs_ignore_path)]

    repos = []
    visited = []
    for path in paths:
        _find_repositories(path, repos, visited, exclude_list, nested=nested)
    return repos


def _find_repositories(path, repos, visited, exclude, nested=False):
    abs_path = os.path.abspath(path)
    if abs_path in visited:
        return
    visited.append(abs_path)

    client = get_vcs_client(path)
    if client:
        repos.append(client)
        if not nested:
            return

    try:
        listdir = os.listdir(path)
    except OSError:
        listdir = []
    for name in sorted(listdir):
        if True not in [re.search(regex, name).span(0)[1] != 0 for regex in exclude]:
            subpath = os.path.join(path, name)
            if not os.path.isdir(subpath):
                continue
            _find_repositories(subpath, repos, visited, exclude, nested=nested)


def get_vcs_client(path):
    for client_class in vcstool_clients:
        if client_class.is_repository(path):
            return client_class(path)
    return None

import os
import zipfile
import pathlib
import logging
# from importlib.abc import Traversable # since python 3.11

logger = logging.getLogger('restim.funscript')


def case_insensitive_compare(a, b):
    return a.lower() == b.lower()


def split_funscript_path(path):
    a, b = os.path.split(path)
    parts = b.split('.')
    extension = parts[-1]
    if len(parts) == 1:
        return parts[0], '', ''
    if len(parts) == 2:
        return parts[0], '', extension
    return '.'.join(parts[:-2]), parts[-2], extension


class Resource:
    def __init__(self, path):
        self.path = path  # Traversable, since python 3.11

    def open(self, *args, **kwargs):
        return self.path.open(*args, **kwargs)

    def is_funscript(self):
        return case_insensitive_compare(self.path.suffix, '.funscript')

    def funscript_type(self):
        try:
            return self.path.suffixes[-2][1:].lower()
        except IndexError:
            return ''

    def name(self):
        return self.path.name

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return self.path.__repr__()


def collect_funscripts(
        dirs: list[str],
        media: str
) -> list[Resource]:
    """
    Search the directories in order for funscripts. Stop searching when at least one funscript is found in a directly.
    If a directory is found with the same name as the media, search that directory too.
    zipfiles are supported.
    :param dirs:
    :param media:
    :return:
    """

    dir_stack = dirs[:]
    new_dirs = []
    collected_files = []

    media_prefix, _, media_extension = split_funscript_path(media)

    while dir_stack and len(collected_files) == 0:
        try:
            current_dir = os.path.expanduser(dir_stack[0])
            del dir_stack[0]

            logger.info(f'detecting funscripts from {current_dir}')

            try:
                is_zip = True
                traversable = zipfile.Path(current_dir)
            except (PermissionError, FileNotFoundError):
                is_zip = False
                traversable = pathlib.Path(current_dir)

            for node in traversable.iterdir():
                full_path = os.path.join(current_dir, node.name)
                if not is_zip and node.is_dir(): # do not support dir-in-zip
                    if case_insensitive_compare(node.name, media_prefix):
                        new_dirs.append(full_path)
                else:
                    a, b, c = split_funscript_path(full_path)
                    if case_insensitive_compare(a, media_prefix):
                        if not is_zip and zipfile.is_zipfile(full_path):    # do not support zip-in-zip
                            new_dirs.append(full_path)
                        elif case_insensitive_compare(c, 'funscript'):
                            collected_files.append(Resource(node))

        except OSError as e:    # unreachable network?
            pass

        dir_stack = new_dirs + dir_stack
        new_dirs = []



    return collected_files

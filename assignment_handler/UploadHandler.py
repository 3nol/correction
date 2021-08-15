import os
from SSHConnector import TitanConnector


def path_without_root(path: str, root: str) -> str:
    """A quick hack to remove a Base-Path from a path and later replace it with a remote path"""

    return os.sep.join([i for i in path.split(os.sep) if i not in root.split(os.sep)])


def upload_folder_structure(local_dir: str, remote_dir: str, connector: TitanConnector, with_files=True):
    """Walks a folder structure top down first creating all remote dirs then copying the files"""

    for root, dirs, files in os.walk(local_dir, topdown=True):
        for name in dirs:
            if not name[0] == '.':
                print(os.path.join(remote_dir, path_without_root(os.path.join(root, name), local_dir)))
                print(connector.run_command(
                    f'mkdir {os.path.join(remote_dir, path_without_root(os.path.join(root, name), local_dir))}'
                    , close_connection=False))
    if with_files:
        for root, dirs, files in os.walk(local_dir, topdown=True):
            for name in files:
                if not name[0] == '.':
                    print(os.path.join(remote_dir, name))
                    connector.put_file(os.path.join(root, name),
                                       os.path.join(remote_dir, path_without_root(os.path.join(root, name), local_dir)))

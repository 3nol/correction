import paramiko
import os


def tailing_os_sep(path: str, should_have_sep: bool) -> str:
    if path[-1] != os.sep and should_have_sep:
        return path + os.sep
    elif path[-1] == os.sep and not should_have_sep:
        return path[0:-1]
    return path


class SSHConnector:
    """Connector for the TitanServer (Generic SSH connector)"""

    def __init__(self, pop: str, pw: str, server: str, port: int = 22, local_location: str = ""):
        self.pop = pop
        self.pw = pw
        self.server = server
        self.port = port
        self.ssh = None
        self.local_location = tailing_os_sep(local_location, True)

    def init_connection(self):
        """Creates an SSH Connection to the specified host"""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        self.ssh.connect(hostname=self.server, port=self.port, username=self.pop, password=self.pw)

    def close_connection(self):
        """Closes an open ssh connection"""
        if self.ssh:
            self.ssh.close()
        self.ssh = None

    def put_file(self, local_dir: str, remote_dir: str):
        """Uploads a file from the given local path to the remote location"""
        if not self.ssh:
            self.init_connection()
        sftp = self.ssh.open_sftp()
        sftp.put(localpath=local_dir, remotepath=remote_dir)
        sftp.close()

    def get_file(self, remote_dir: str, local_dir: str):
        """Downloads a file from the given location to the local directory"""
        if not self.ssh:
            self.init_connection()
        sftp = self.ssh.open_sftp()
        sftp.get(remotepath=remote_dir, localpath=local_dir)
        sftp.close()

    def run_command(self, command: str, stdin_input: list[str] = None, remove_trailing_new_lines: bool = True, close_connection:bool = True) -> tuple[list, list]:
        """Runs a bash command on the remote server , returns stdout and stderr"""
        if not self.ssh:
            self.init_connection()
        stdin, stdout, stderr = self.ssh.exec_command(command)
        if stdin_input:
            for i in stdin_input:
                stdin.write(i)

        stdout_ret = [i.replace('\n', '') if remove_trailing_new_lines else i for i in stdout.readlines()]
        stderr_ret = [i.replace('\n', '') if remove_trailing_new_lines else i for i in stderr.readlines()]
        if close_connection:
            self.close_connection()
        return stdout_ret, stderr_ret

    def run_sh_file(self, remote_location: str, logfile: bool = True, copy_log_file: bool = True, auto_close:bool=True) -> dict:
        """runs a remote sh file on the remote_location.Creates a local logfile.The Logfile can be copied to the
        remote_location by setting copy_log_file to true (default).If this flag is false the method returns a dict
        containing the location of the logfile and its supposed location
        """
        if remote_location.split(os.sep)[-1].split(".")[-1] != "sh":
            raise NotImplementedError
        print(self.run_command(f'cat {remote_location}', close_connection=auto_close))
        # parent_folder = remote_location.split(os.sep)[-2]
        os.sep = '/'
        file_name = remote_location.split(os.sep)[-1]
        path_to_file = os.sep.join(remote_location.split(os.sep)[0:-1])
        stdout, stderr = self.run_command(f'cd {path_to_file} && bash {file_name}',
                                          remove_trailing_new_lines=False, close_connection=auto_close)
        if logfile:
            with open(f'{self.local_location}{file_name}.txt', "w+") as f:
                for i in stdout:
                    f.write(i)
                f.write('---')
                for i in stderr:
                    f.write(i)
            print(f'local logfile saved at {self.local_location}{file_name}.txt')
            if copy_log_file:
                self.put_file(f'{self.local_location}{file_name}.txt', path_to_file + os.sep + f"{file_name}_log.txt")
                os.remove(f'{self.local_location}{file_name}.txt')
                print(f'local logfile removed automatically, remote logfile at {path_to_file}{os.sep}{file_name}_log.txt')
                return {'stderr': stderr == []}
            else:
                return {'local': f'{self.local_location}{file_name}.txt',
                        'remote': path_to_file + os.sep + f"{file_name}_log.txt",
                        'delete': True
                        }
        else:
            return {'stderr': stderr == ""}

    def get_all_files_with_extension(self, root_dir: str, extension: str):
        """Generates a list of all files relative to the root_dir that have an specific location"""
        stdout, _ = self.run_command(f'find {tailing_os_sep(root_dir, False)}  -type f -name "*.{extension}"')
        return stdout

    def execute_all_sh_files(self, root_dir: str, instant_copy: bool = False):
        """executes all sh files found in the root_dir (and sub dirs) creates logfiles locally"""
        to_copy = []
        files = self.get_all_files_with_extension(root_dir, 'sh')
        print(f"found {len(files)} files with sh extension , running now")
        for i in files:
            to_copy.append(self.run_sh_file(i, copy_log_file=instant_copy,auto_close=False))
        if not instant_copy:
            self.sync_file_list_to_remote(to_copy)
        self.close_connection()

    def sync_file_list_to_remote(self, file_list: list[dict]):
        """syncs a list of logfile_dicts to their location."""
        for i in file_list:
            self.put_file(i['local'], i['remote'])
            if i["delete"]:
                os.remove(i['local'])

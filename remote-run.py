#!/usr/bin/env python3

import paramiko
import os
import sys
from dotenv import load_dotenv

VERSION = "0.0.1"
DATE = "2024-05-24"

class PermikaClient:
    def __init__(self, hostname, username, password, port=22, ssh_key=""):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.ssh_key = ssh_key
        self.client = self._connect()

    def _connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.ssh_key:
            key_path = os.path.expanduser(self.ssh_key)
            key = paramiko.RSAKey.from_private_key_file(key_path)
            client.connect(self.hostname, username=self.username, pkey=key, port=self.port)
        else:
            client.connect(self.hostname, username=self.username, password=self.password, port=self.port)
        return client

    def upload_file(self, local_path, remote_path):
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        print(f"Uploaded {local_path} to {remote_path}")

    def download_file(self, remote_path, local_path):
        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        print(f"Downloaded {remote_path} to {local_path}")

    def run_remote_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
        return output, error

    def close(self):
        self.client.close()
        print("Connection closed")

def print_help():
    help_text = """
Usage:  remote-run help
        remote-run version
        remote-run upload <local_path> <remote_path>    # Upload a file to the remote server
        remote-run download <remote_path> <local_path>  # Download a file from the remote server
        remote-run run <command> <args>                 # Run a command on the remote server

By default, the script will look for a file named .env in the current directory.
You can specify a different file using the -f flag in front of the command.

Example:
        remote-run -f example.env upload local.txt /remote/path/
"""
    print(help_text)

def get_env_variables(name=".env"):
    if os.path.exists(name):
        load_dotenv(name)
        try:
            hostname = os.getenv("HOSTNAME")
            if not hostname:
                raise KeyError("HOSTNAME is not set")
            env_vars = {
                "hostname": hostname,
                "port": int(os.getenv("PORT", 22)),
                "username": os.getenv("USERNAME", ""),
                "password": os.getenv("PASSWORD", ""),
                "ssh_key": os.path.expanduser(os.getenv("SSH_KEY", ""))
            }
            return env_vars
        except KeyError as e:
            print(f"Missing environment variable: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unknown error occurred: {e}")
            sys.exit(1)
    else:
        raise FileNotFoundError(f"{name} not found")

def main():
    """CLI entrypoint"""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "help":
        print_help()
        sys.exit(0)
    elif cmd == "version":
        print(f"Remote-Run version: {VERSION}")
        print(f"Date: {DATE}")
        sys.exit(0)
    elif cmd not in ["upload", "download", "run"]:
        print("Invalid command")
        sys.exit(1)
    
    myargs = sys.argv[2:] 
    env_file = ".env"
    if "-f" in sys.argv:
        try:
            flag_pos = sys.argv.index("-f")
            env_file = sys.argv[flag_pos + 1]
            myargs = sys.argv[2:flag_pos] + sys.argv[flag_pos + 2:]
        except IndexError:
            print("Missing file name after -f")
            sys.exit(1)

    env = get_env_variables(env_file)
    client = PermikaClient(**env)

    if cmd == "upload":
        if len(myargs) < 2:
            print("Missing arguments")
            sys.exit(1)
        local_path, remote_path = myargs
        client.upload_file(local_path, remote_path)
    elif cmd == "download":
        if len(myargs) < 2:
            print("Missing arguments")
            sys.exit(1)
        remote_path, local_path = myargs
        client.download_file(remote_path, local_path)
    elif cmd == "run":
        if len(myargs) < 1:
            print("Missing command")
            sys.exit(1)
        command = " ".join(myargs)
        client.run_remote_command(command)

    # Close the connection
    client.close()

# Example usage
if __name__ == "__main__":
    is_development = True
    if is_development:
        main()
    else:
        try:
            main()
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

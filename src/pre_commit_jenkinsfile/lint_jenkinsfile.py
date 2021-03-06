import argparse
from enum import IntEnum
from pathlib import Path
from typing import List, Optional, Sequence, Dict

import paramiko
import urllib3
from paramiko import (
    SSHClient,
    SSHException,
    BadHostKeyException,
    AuthenticationException,
    AutoAddPolicy,
)
from urllib3 import HTTPResponse

from src.pre_commit_jenkinsfile.config import Config


class ErrorCodes(IntEnum):
    OK = 0
    FAIL = 1


def get_jenkins_crumb(
    jenkins_url: str, jenkins_login: str, jenkins_api_token: str
) -> Optional[str]:
    crumb: Optional[str]
    http = urllib3.PoolManager()
    request_url: str = f'{jenkins_url}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)'
    header: Dict[str, str] = {}
    if len(jenkins_login) > 0 and len(jenkins_api_token) > 0:
        header = urllib3.make_headers(basic_auth=f"{jenkins_login}:{jenkins_api_token}")
    response: HTTPResponse = http.request("GET", request_url, headers=header)
    if response.status == 200:
        crumb = response.data.decode()
    else:
        response_message: str = response.data.decode()
        if "Authentication required" in response_message:
            print(
                f"Requesting a crumb from the Jenkins server failed due to an authentication failure "
                f"(status {response.status})."
            )
        else:
            print(
                f"Requesting the crumb field from the Jenkins server failed with status {response.status}:"
                f"\n{response_message}."
            )
        crumb = None

    return crumb


def lint_via_http(
    filenames: List[Path],
    jenkins_url: str,
    jenkins_login: str,
    jenkins_api_token: str,
) -> ErrorCodes:

    return_code: ErrorCodes
    return_codes: List[ErrorCodes] = []
    crumb = get_jenkins_crumb(jenkins_url, jenkins_login, jenkins_api_token)
    if crumb:
        http = urllib3.PoolManager()
        request_url: str = f"{jenkins_url}/pipeline-model-converter/validate"
        headers: Dict[str, str] = {}
        if len(jenkins_login) > 0 and len(jenkins_api_token) > 0:
            headers = urllib3.make_headers(
                basic_auth=f"{jenkins_login}:{jenkins_api_token}"
            )

        crumb_parts = crumb.split(":")
        headers[crumb_parts[0]] = crumb_parts[1]
        for filename in filenames:
            return_code = http_validate(filename, headers, http, request_url)
            return_codes.append(return_code)

        return_code = (
            ErrorCodes.OK if ErrorCodes.FAIL not in return_codes else ErrorCodes.FAIL
        )
    else:
        return_code = ErrorCodes.FAIL
        print("No crumb was returned by the Jenkins server and so we cannot lint.")

    return return_code


def http_validate(
    filename: Path, headers: Dict[str, str], http: urllib3.PoolManager, request_url: str
) -> ErrorCodes:
    return_code: ErrorCodes

    jenkinsfile_text: str = filename.read_text()
    response: HTTPResponse = http.request_encode_body(
        "POST",
        request_url,
        fields={"jenkinsfile": jenkinsfile_text},
        headers=headers,
    )
    message: str = response.data.decode()
    if response.status == 200:
        if "Error" in message:
            print(filename)
            print(message)
            return_code = ErrorCodes.FAIL
        else:
            return_code = ErrorCodes.OK
    else:
        print(f"Connection failed: A status code of {response.status} was returned.")
        return_code = ErrorCodes.FAIL

    return return_code


def lint_via_ssh(
    filenames: List[Path], jenkins_hostname: str, jenkins_jenkins_ssh_port: int
) -> ErrorCodes:
    return_code: ErrorCodes = ErrorCodes.FAIL
    return_codes: List[ErrorCodes] = []

    try:
        with SSHClient() as client:
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(jenkins_hostname, port=jenkins_jenkins_ssh_port)
            for filename in filenames:
                return_code = ssh_validate(client, filename)
                return_codes.append(return_code)

    except BadHostKeyException as err:
        print(
            f"Connection to the server failed because the hostkey could not be verified:\n{str(err)}"
        )
    except AuthenticationException as err:
        print(f"Authentication with the server failed:\n{str(err)}")
    except SSHException as err:
        print(f"Error establishing an SSH connection: \n{str(err)}")
    except OSError as err:
        # socket.error is a deprecated alias of OSError
        print(
            f"A socket error occurred during the attempt to connect to the server: \n{str(err)}"
        )
    except Exception as err:
        print(f"An unexpected error occurred:\n{str(err)}")

    if len(return_codes) > 0:
        return_code = (
            ErrorCodes.OK if ErrorCodes.FAIL not in return_codes else ErrorCodes.FAIL
        )

    return return_code


def ssh_validate(client: paramiko.SSHClient, filename: Path) -> ErrorCodes:
    return_code: ErrorCodes = ErrorCodes.FAIL

    if filename.exists():
        try:
            stdin_channel, stdout_channel, stderr_channel = client.exec_command(
                "declarative-linter"
            )

            # Write the file contents to stdin; declarative-linter will wait for stdin input
            stdin_channel.channel.send(filename.read_bytes())
            stdin_channel.channel.shutdown_write()

            # Block until finished
            exit_status: int = stdout_channel.channel.recv_exit_status()
            stdout: str = stdout_channel.read().decode()

            return_code = ErrorCodes.OK if 0 == exit_status else ErrorCodes.FAIL
            if ErrorCodes.FAIL == return_code:
                print(filename)
                print(stdout)

        except SSHException as err:
            print(
                f'Failed to execute the "declarative-linter" command on the Jenkins server:\n{str(err)}'
            )
    else:
        print(f'The file "{str(filename)} does not exist.')

    return return_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--jenkins_url",
        action="store",
        help="The root URL of your Jenkins controller",
        type=str,
        default="",
    )
    parser.add_argument(
        "--jenkins_login",
        action="store",
        help="The user login to the Jenkins controller.",
        type=str,
        default="",
    )
    parser.add_argument(
        "--jenkins_api_token",
        action="store",
        help="The API token for the user account on the Jenkins controller",
        type=str,
        default="",
    )
    parser.add_argument(
        "--jenkins_ssh_port",
        action="store",
        help="The ssh port number for your Jenkins controller",
        type=int,
        default=22,
    )
    parser.add_argument(
        "--jenkins_hostname",
        action="store",
        help="The ssh hostname for your Jenkins controller",
        type=str,
        default="",
    )

    parser.add_argument(
        "--config",
        action="store",
        help="A file path (absolute or relative) to an INI file.",
        type=str,
        default="",
    )
    parser.add_argument("filenames", nargs="*", type=Path)
    args = parser.parse_args(argv)
    return_value: ErrorCodes = ErrorCodes.OK

    filenames: List[Path] = []
    if args.filenames:
        filenames = args.filenames

    config: Config
    if len(args.config) > 0:
        config_file_path: Path = Path(args.config).resolve()
        if config_file_path.exists() and config_file_path.is_file():
            config = Config.load_file(config_file_path)
        else:
            config = Config()
            print(
                f"Could not find the config file {config_file_path} or the path does not point to a file"
            )
    else:
        config = Config(
            args.jenkins_url,
            args.jenkins_login,
            args.jenkins_api_token,
            args.jenkins_hostname,
            args.jenkins_ssh_port,
        )

    if len(filenames) > 0:
        if config.has_http_creds():
            return_value = lint_via_http(
                filenames,
                config.jenkins_url,
                config.jenkins_login,
                config.jenkins_api_token,
            )
        elif config.has_ssh_creds():
            return_value = lint_via_ssh(
                filenames, config.jenkins_hostname, config.jenkins_ssh_port
            )

    return return_value


if __name__ == "__main__":
    SystemExit(main())

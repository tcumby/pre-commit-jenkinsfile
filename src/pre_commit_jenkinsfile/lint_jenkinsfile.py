import argparse
from enum import IntEnum
from pathlib import Path
from socket import socket
from typing import List, Optional, Sequence

import paramiko
import urllib3
from urllib3 import HTTPResponse
from paramiko import (
    SSHClient,
    SSHException,
    BadHostKeyException,
    AuthenticationException,
)


class ErrorCodes(IntEnum):
    OK = 0
    FAIL = 1


def get_jenkins_crumb(jenkins_url: str) -> Optional[str]:
    crumb: Optional[str]
    http = urllib3.PoolManager()
    request_url: str = f'{jenkins_url}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)'
    response: HTTPResponse = http.request("GET", request_url)
    if response.status == 200:
        crumb = response.decode_content()
    else:
        print(
            f"Requesting the crumb field from the Jenkins server failed with status {response.status}."
        )
        crumb = None

    return crumb


def lint_via_http(jenkins_url: str, filenames: List[Path]) -> ErrorCodes:
    return_code: ErrorCodes
    return_codes: List[ErrorCodes] = []
    header = get_jenkins_crumb(jenkins_url)
    if header:
        http = urllib3.PoolManager()
        request_url: str = f"{jenkins_url}/pipeline-model-converter/validate"
        for filename in filenames:
            return_code = http_validate(filename, header, http, request_url)
            return_codes.append(return_code)

        return_code = (
            ErrorCodes.OK if ErrorCodes.FAIL not in return_codes else ErrorCodes.FAIL
        )
    else:
        return_code = ErrorCodes.FAIL
        print("No crumb was returned by the Jenkins server and so we cannot lint.")

    return return_code


def http_validate(
    filename: Path, header: str, http: urllib3.PoolManager, request_url: str
) -> ErrorCodes:
    return_code: ErrorCodes

    jenkinsfile_text: str = filename.read_text()
    response: HTTPResponse = http.request_encode_body(
        "POST",
        request_url,
        fields={"jenkinsfile": jenkinsfile_text},
        headers=header,
    )
    message: str = response.decode_content()
    if response.status == 200:
        if "Error" in message:
            print(message)
            return_code = ErrorCodes.FAIL
        else:
            return_code = ErrorCodes.OK
    else:
        print(f"Connection failed: A status code of {response.status} was returned.")
        return_code = ErrorCodes.FAIL

    return return_code


def lint_via_ssh(
    jenkins_hostname: str, jenkins_sshd_port: int, filenames: List[Path]
) -> ErrorCodes:
    return_code: ErrorCodes = ErrorCodes.FAIL
    return_codes: List[ErrorCodes] = []

    try:
        with SSHClient() as client:
            client.load_system_host_keys()
            client.connect(jenkins_hostname, port=jenkins_sshd_port)
            for filename in filenames:
                return_code = ssh_validate(client, filename)
                return_codes.append(return_code)

    except BadHostKeyException as err:
        print(
            f"Connection to the server failed because the hostkey could not be verified:\n{str(err)}"
        )
    except AuthenticationException as err:
        pass
    except SSHException as err:
        pass
    except OSError as err:
        # socket.error is a deprecated alias of OSError
        pass

    if len(return_codes) > 0:
        return_code = (
            ErrorCodes.OK if ErrorCodes.FAIL not in return_codes else ErrorCodes.FAIL
        )

    return return_code


def ssh_validate(client: paramiko.SSHClient, filename: Path) -> ErrorCodes:
    return_code: ErrorCodes = ErrorCodes.FAIL

    if filename.exists():
        try:
            _, stdout_channel, stderr_channel = client.exec_command(
                f"declarative-linter < {str(filename)}"
            )
            stdout: str = stdout_channel.read().decode()
            stderr: str = stderr_channel.read().decode()
        except SSHException as err:
            print(
                f'Failed to execute the "declarative-linter" command on the Jenkins server:\n{str(err)}'
            )
    else:
        pass

    return return_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", type=Path)
    parser.add_argument(
        "--jenkins_url",
        action="store",
        help="The root URL of your Jenkins controller",
        type=str,
        default="",
    )
    parser.add_argument(
        "--jenkins_sshd_port",
        action="store",
        help="The port number for your Jenkins controller",
        type=str,
        default="",
    )
    parser.add_argument(
        "--jenkins_hostname",
        action="store",
        help="The hostname for your Jenkins controller",
        type=str,
        default="",
    )
    args = parser.parse_args(argv)
    return_value: ErrorCodes = ErrorCodes.OK

    filenames: List[Path] = []
    if args.filenames:
        filenames = args.filenames

    jenkins_url: str = ""
    if args.jenkins_url:
        jenkins_url = args.jenkins_url

    jenkins_sshd_port: str = ""
    if args.jenkins_sshd_port:
        jenkins_sshd_port = args.jenkins_sshd_port

    jenkins_hostname: str = ""
    if args.jenkins_hostname:
        jenkins_hostname = args.jenkins_hostname

    if len(filenames) > 0:
        if len(jenkins_url) > 0:
            return_value = lint_via_http(jenkins_url, filenames)
        elif len(jenkins_sshd_port) > 0 and len(jenkins_hostname) > 0:
            pass

    return return_value


if __name__ == "__main__":
    SystemExit(main())
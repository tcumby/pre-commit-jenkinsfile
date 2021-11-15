import argparse
from enum import IntEnum
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import urllib3
from urllib3 import HTTPResponse


class ErrorCodes(IntEnum):
    OK = (0,)
    NO_JENKINS_CRUMB = 1
    HAD_ERRORS = 2


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


def lint_via_http(jenkins_url: str, filename: Path) -> Tuple[ErrorCodes, str]:
    return_code: ErrorCodes.OK
    error_message: str = ""

    header = get_jenkins_crumb(jenkins_url)
    if header:
        http = urllib3.PoolManager()
        request_url: str = f"{jenkins_url}/pipeline-model-converter/validate"
        jenkinsfile_text: str = filename.read_text()

        response: HTTPResponse = http.request_encode_body(
            "POST",
            request_url,
            fields={"jenkinsfile": jenkinsfile_text},
            headers=header,
        )
    else:
        return_code = ErrorCodes.NO_JENKINS_CRUMB
        error_message = (
            "No crumb was returned by the Jenkins server and so we cannot lint."
        )

    return return_code, error_message


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
    args = parser.parse_args(argv)
    return_value: int = 0

    filenames: List[Path] = []
    if args.filenames:
        filenames = args.filenames

    jenkins_url: str = ""
    if args.jenkins_url:
        jenkins_url = args.jenkins_url

    return return_value


if __name__ == "__main__":
    SystemExit(main())

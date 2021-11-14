import argparse
from pathlib import Path
from typing import Optional, Sequence

import urllib3
from urllib3 import HTTPResponse


def get_jenkins_crumb(jenkins_url: str) -> Optional[str]:
    crumb: Optional[str]
    http = urllib3.PoolManager()
    request_url: str = f'{jenkins_url}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)'
    response: HTTPResponse = http.request("GET", request_url)
    if response:
        data: bytes = response.data
        crumb = data.decode("UTF-8")
    else:
        crumb = None

    return crumb


def lint_via_http(jenkins_url: str, filename: Path):
    header = get_jenkins_crumb(jenkins_url)
    if header:
        http = urllib3.PoolManager()
        request_url: str = f"{jenkins_url}/pipeline-model-converter/validate"
        response: HTTPResponse = http.request("POST", request_url, headers=header)


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

    return return_value


if __name__ == "__main__":
    SystemExit(main())

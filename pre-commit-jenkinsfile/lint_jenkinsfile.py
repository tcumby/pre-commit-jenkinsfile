import argparse
from pathlib import Path
from typing import Optional, Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", type=Path)
    args = parser.parse_args(argv)
    return_value: int = 0

    return return_value


if __name__ == "__main__":
    SystemExit(main())

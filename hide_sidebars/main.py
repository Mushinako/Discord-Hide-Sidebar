#!/usr/bin/env python3
"""Main module. Decides which functions to call"""

import platform


def main() -> None:
    """Main function. Checks OS and runs respective code"""

    if platform.platform == "Windows":
        pass
    else:
        raise NotImplementedError(
            f"Your operating system \"{platform.platform}\" is not yet supported"
        )


if __name__ == "__main__":
    main()

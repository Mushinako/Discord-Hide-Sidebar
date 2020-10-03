#!/usr/bin/env python3
import logging
from pathlib import Path

from hide_sidebars.main import main

LOG_FILE = Path(__file__).resolve().parent / "logs" / "dhs.log"
# Change this to `logging.WARN` and redact all personal information before sharing logs!
LOG_LEVEL = logging.DEBUG

# Main logger
logger = logging.getLogger("hide_sidebars")
logger.setLevel(LOG_LEVEL)
# Main logging file handler
fh = logging.FileHandler(LOG_FILE, "w")
fh.setLevel(LOG_LEVEL)
# Main logging console handler
# ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
# Main logging formatter
fm = logging.Formatter(
    "%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s]: %(message)s",
    r"%Y-%m-%d %H:%M:%S"
)
fh.setFormatter(fm)
# ch.setFormatter(fm)
logger.addHandler(fh)
# logger.addHandler(ch)

if __name__ == "__main__":
    main()

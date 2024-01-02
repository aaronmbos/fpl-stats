import logging
import sys


def init_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(stream=sys.stdout)],
    )

    return logging.getLogger(name)

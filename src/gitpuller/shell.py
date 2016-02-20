#!/usr/bin/env python
import os
import sys
import logging
import argparse
from git import Repo
from git.exc import InvalidGitRepositoryError


def create_argument_parser(logger):
    logger.debug("Parsing Arguments")
    p = argparse.ArgumentParser(description="Git Puller")
    p.add_argument("parent_directory",
                   metavar="parent-directory",
                   nargs=1,
                   help="Parent directory hosting git repositories")
    p.add_argument("--branch", "-b", default="develop", help="The branch to update")
    return p


def initialize_logger():
    _logger = logging.getLogger(__file__)
    _logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    # formatter = logging.Formatter("%(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt=formatter)
    _logger.addHandler(stream_handler)
    return _logger


def update_repositories(parent, branch, logger):
    folders = os.listdir(parent)
    counter = 0
    for folder in folders:
        repository_path = os.path.join(parent, folder)
        if update_repository(repository_path, branch, logger):
            counter += 1
    return counter


def update_repository(path, branch, logger):
    try:
        repository = Repo(path)

        if repository.bare:
            logger.warn("\"%s\" is a bare git repository, skipping", path)
            return False

        branches = repository.branches
        for b in branches:
            if b.name == branch:
                logger.info("Updating \"%s\"", path)
                b.checkout()
                origin = repository.remote()
                origin.pull()
                return True
            else:
                logger.info("\"%s\" does not have a %s branch, skipping", path, branch)
                return False
    except InvalidGitRepositoryError:
        logger.warn("\"%s\" is not a valid git repository, skipping", path)
        return False


def main():
    logger = initialize_logger()
    argument_parser = create_argument_parser(logger)
    arguments = argument_parser.parse_args()

    if not arguments.parent_directory:
        argument_parser.print_help()
        exit(1)

    parent_directory = arguments.parent_directory[0]
    logger.info("Updating git repositories in \"%s\"", parent_directory)
    repository_counter = update_repositories(parent_directory, arguments.branch, logger)
    logger.info("Done, updated %s repositories", repository_counter)
    return 0

if __name__ == "__main__":
    sys.exit(main())


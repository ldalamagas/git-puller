#!/usr/bin/env python
import os
import sys
import logging
import argparse
from Queue import Queue
from threading import Thread
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError


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
    formatter = logging.Formatter("%(levelname)s [%(threadName)s]: %(message)s")
    # formatter = logging.Formatter("%(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt=formatter)
    _logger.addHandler(stream_handler)
    return _logger


def update_worker(work_queue, branch, logger, result_queue):
    while not work_queue.empty():
        repository_path = work_queue.get()
        if update_repository(repository_path, branch, logger):
            result_queue.put(1)
        else:
            result_queue.put(0)
        work_queue.task_done()


def update_repositories(parent, branch, logger):
    queue_boundary = 500
    worker_threads = 5
    folders = os.listdir(parent)
    work_queue = Queue(queue_boundary)
    result_queue = Queue(queue_boundary)

    # Fill the job queue
    for folder in folders:
        work_queue.put(os.path.join(parent, folder))

    # Spawn workers
    for i in range(1, worker_threads):
        thread = Thread(name=i, target=update_worker, args=(work_queue, branch, logger, result_queue))
        thread.daemon = True
        thread.start()

    # Wait for the workers to finish
    work_queue.join()

    # Gather work results
    updated_counter = 0
    total_counter = 0
    while not result_queue.empty():
        result = result_queue.get()
        updated_counter += result
        total_counter += 1
        result_queue.task_done()

    return updated_counter, total_counter


def update_repository(path, branch, logger):
    try:
        repository = Repo(path)

        if repository.bare:
            logger.warn("\"%s\" is a bare git repository, skipping", path)
            return False

        if repository.is_dirty():
            logger.warn("\"%s\" has unsaved changes, skipping", path)
            return False

        branches = repository.branches
        # noinspection PyTypeChecker
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
    except GitCommandError:
        logger.exception("Failed to update \"%s\"", path)
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
    updated_counter, total_counter = update_repositories(parent_directory, arguments.branch, logger)
    logger.info("Done, updated %s of %s repositories", updated_counter, total_counter)
    return 0

if __name__ == "__main__":
    sys.exit(main())

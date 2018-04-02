#!/usr/bin/env python


import os
import sys
import json
import argparse
from antinex_client.log.setup_logging import build_colorized_logger
from antinex_client.utils import ev
from antinex_client.utils import ppj
from antinex_client.ai_client import AIClient
from antinex_client.consts import LOGIN_FAILED
from antinex_client.consts import SUCCESS
from antinex_client.consts import ERROR
from antinex_client.consts import FAILED


name = "ai-client"
log = build_colorized_logger(name=name)


def prepare_new_dataset():
    """prepare_new_dataset

    Prepare a new ``MLPrepare`` record and dataset files on disk.

    """

    parser = argparse.ArgumentParser(
            description=("Python client to Prepare a dataset"))
    parser.add_argument(
            "-u",
            help="username",
            required=False,
            dest="user")
    parser.add_argument(
            "-p",
            help="user password",
            required=False,
            dest="password")
    parser.add_argument(
            "-e",
            help="user email",
            required=False,
            dest="email")
    parser.add_argument(
            "-a",
            help="url endpoint with default http://localhost:8080",
            required=False,
            dest="url")
    parser.add_argument(
            "-f",
            help="file to use default ./examples/test-keras-dnn.json",
            required=False,
            dest="prepare_file")
    parser.add_argument(
            "-s",
            help="silent",
            required=False,
            dest="silent",
            action="store_true")
    parser.add_argument(
            "-d",
            help="debug",
            required=False,
            dest="debug",
            action="store_true")
    args = parser.parse_args()

    user = ev(
        "API_USER",
        "user-not-set")
    password = ev(
        "API_PASSWORD",
        "password-not-set")
    email = ev(
        "API_EMAIL",
        "email-not-set")
    url = ev(
        "API_URL",
        "http://localhost:8080")
    prepare_file = ev(
        "DATAFILE",
        "prepare_file-not-set")
    verbose = bool(str(ev(
        "API_VERBOSE",
        "true")).lower() == "true")
    debug = bool(str(ev(
        "API_DEBUG",
        "false")).lower() == "true")

    if args.user:
        user = args.user
    if args.password:
        password = args.password
    if args.email:
        email = args.email
    if args.url:
        url = args.url
    if args.prepare_file:
        prepare_file = args.prepare_file
    if args.silent:
        verbose = False
    if args.debug:
        debug = True

    usage = ("Please run with -u <username> "
             "-p <password> -e <email> "
             "-a <AntiNex URL http://localhost:8080> "
             "-f <path to prepare file>")

    valid = True
    if not user or user == "user-not-set":
        log.error("missing user")
        valid = False
    if not password or password == "password-not-set":
        log.error("missing password")
        valid = False
    if not prepare_file or prepare_file == "prepare_file-not-set":
        log.error("missing prepare_file")
        valid = False
    else:
        if not os.path.exists(prepare_file):
            log.error(("did not find prepare_file={} on disk")
                      .format(
                        prepare_file))
            valid = False
    if not valid:
        log.error(usage)
        sys.exit(1)

    if verbose:
        log.info(("creating client user={} url={} file={}")
                 .format(
                    user,
                    url,
                    prepare_file))

    client = AIClient(
        user=user,
        email=email,
        password=password,
        url=url,
        verbose=verbose,
        debug=debug)

    if verbose:
        log.info(("loading request in prepare_file={}")
                 .format(
                    prepare_file))

    req_body = None
    with open(prepare_file, "r") as f:
        req_body = json.loads(f.read())

    if verbose:
        log.info("running prepare")

    prepare_was_started = False
    response = client.run_prepare(
        body=req_body)

    if response["status"] == SUCCESS:
        log.info(("prepare started with response={}")
                 .format(
                    response["data"]))
        prepare_was_started = True
    elif response["status"] == FAILED:
        log.error(("prepare failed with error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))
    elif response["status"] == ERROR:
        log.error(("prepare had an error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))
    elif response["status"] == LOGIN_FAILED:
        log.error(("prepare reported user was not able to log in "
                   "with an error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))

    if not prepare_was_started:
        sys.exit(1)

    if debug:
        log.info(("parsing response data={}")
                 .format(
                    response["data"]))
    else:
        if verbose:
            log.info("parsing data")

    prepare_data = response["data"]

    if not prepare_data:
        log.error(("missing prepare dictionary in response data={}")
                  .format(
                    response["data"]))
        sys.exit(1)

    prepare_id = prepare_data.get("id", None)
    prepare_status = prepare_data.get("status", None)

    log.info(("started prepare.id={} prepare.status={}")
             .format(
                prepare_id,
                prepare_status))

    prepare_results = client.wait_for_prepare_to_finish(
        prepare_id=prepare_id)

    if prepare_results["status"] != SUCCESS:
        log.error(("failed waiting for prepare.id={} to finish "
                   "error={} data={}")
                  .format(
                    prepare_id,
                    prepare_results["error"],
                    prepare_results["data"]))
        sys.exit(1)

    final_prepare = prepare_results["data"]

    log.info(("prepare={}")
             .format(
                ppj(final_prepare)))

    log.info(("prepare.id={} is done")
             .format(
                prepare_id))

# end of prepare_new_dataset


if __name__ == "__main__":
    prepare_new_dataset()

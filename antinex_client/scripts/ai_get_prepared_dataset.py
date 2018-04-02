#!/usr/bin/env python


import sys
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


def get_prepared_dataset():
    """get_prepared_dataset

    Get an ``MLPrepare`` by database id.

    """

    parser = argparse.ArgumentParser(
            description=("Python client get Prepared dataset by ID"))
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
            "-i",
            help="User's MLPrepare.id to look up",
            required=False,
            dest="prepare_id")
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
    prepare_id = ev(
        "PREPARE_ID",
        "prepare_id-not-set")
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
    if args.prepare_id:
        prepare_id = args.prepare_id
    if args.silent:
        verbose = False
    if args.debug:
        debug = True

    usage = ("Please run with -u <username> "
             "-p <password> -e <email> "
             "-a <AntiNex URL http://localhost:8080> -i <prepare_id>")

    valid = True
    if not user or user == "user-not-set":
        log.error("missing user")
        valid = False
    if not password or password == "password-not-set":
        log.error("missing password")
        valid = False
    if not prepare_id or prepare_id == "prepare_id-not-set":
        log.error("missing prepare_id")
        valid = False
    else:
        try:
            prepare_id = int(prepare_id)
        except Exception as e:
            log.error("please use -i <prepare_id with an integer>")
            valid = False
    if not valid:
        log.error(usage)
        sys.exit(1)

    if verbose:
        log.info(("creating client user={} url={} file={}")
                 .format(
                    user,
                    url,
                    prepare_id))

    client = AIClient(
        user=user,
        email=email,
        password=password,
        url=url,
        verbose=verbose,
        debug=debug)

    if verbose:
        log.info(("loading request in prepare_id={}")
                 .format(
                    prepare_id))

    response = client.get_prepare_by_id(
        prepare_id=prepare_id)

    if response["status"] == SUCCESS:
        if debug:
            log.info(("got a prepare response={}")
                     .format(
                        response["data"]))
    elif response["status"] == FAILED:
        log.error(("prepare failed with error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))
        sys.exit(1)
    elif response["status"] == ERROR:
        if "missing " in response["error"]:
            log.error(("Did not find a prepare with id={} for user={}")
                      .format(
                        prepare_id,
                        user))
        else:
            log.error(("prepare had an error='{}' with response={}")
                      .format(
                        response["error"],
                        response["data"]))
        sys.exit(1)
    elif response["status"] == LOGIN_FAILED:
        log.error(("prepare reported user was not able to log in "
                   "with an error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))
        sys.exit(1)

    prepare_data = response["data"]

    if len(prepare_data) == 0:
        log.error(("Did not find a prepare with id={} for user={}")
                  .format(
                    prepare_id,
                    user))
        sys.exit(1)

    prepare_id = prepare_data.get("id", None)
    prepare_status = prepare_data.get("status", None)

    log.info(("prepare={}")
             .format(
                ppj(prepare_data)))

    log.info(("done getting prepare.id={} status={}")
             .format(
                prepare_id,
                prepare_status))

# end of get_prepared_dataset


if __name__ == "__main__":
    get_prepared_dataset()

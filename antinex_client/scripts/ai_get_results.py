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


def get_ml_job_results():
    """get_ml_job_results

    Get an ``MLJobResult`` by database id.

    """

    parser = argparse.ArgumentParser(
            description=("Python client get AI Results by ID"))
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
            help="User's MLJobResult.id to look up",
            required=False,
            dest="result_id")
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
    result_id = ev(
        "RESULT_ID",
        "result_id-not-set")
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
    if args.result_id:
        result_id = args.result_id
    if args.silent:
        verbose = False
    if args.debug:
        debug = True

    usage = ("Please run with -u <username> "
             "-p <password> -e <email> "
             "-a <AntiNex URL http://localhost:8080> -i <result_id>")

    valid = True
    if not user or user == "user-not-set":
        log.error("missing user")
        valid = False
    if not password or password == "password-not-set":
        log.error("missing password")
        valid = False
    if not result_id or result_id == "result_id-not-set":
        log.error("missing result_id")
        valid = False
    else:
        try:
            result_id = int(result_id)
        except Exception as e:
            log.error("please use -i <result_id with an integer>")
            valid = False
    if not valid:
        log.error(usage)
        sys.exit(1)

    if verbose:
        log.info(("creating client user={} url={} result_id={}")
                 .format(
                    user,
                    url,
                    result_id))

    client = AIClient(
        user=user,
        email=email,
        password=password,
        url=url,
        verbose=verbose,
        debug=debug)

    if verbose:
        log.info(("loading request in result_id={}")
                 .format(
                    result_id))

    response = client.get_result_by_id(
        result_id=result_id)

    if response["status"] == SUCCESS:
        if debug:
            log.info(("got a result response={}")
                     .format(
                        response["data"]))
    elif response["status"] == FAILED:
        log.error(("result failed with error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))
        sys.exit(1)
    elif response["status"] == ERROR:
        if "missing " in response["error"]:
            log.error(("Did not find a result with id={} for user={}")
                      .format(
                        result_id,
                        user))
        else:
            log.error(("result had an error='{}' with response={}")
                      .format(
                        response["error"],
                        response["data"]))
        sys.exit(1)
    elif response["status"] == LOGIN_FAILED:
        log.error(("result reported user was not able to log in "
                   "with an error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))
        sys.exit(1)

    result_data = response["data"]

    if len(result_data) == 0:
        log.error(("Did not find a result with id={} for user={}")
                  .format(
                    result_id,
                    user))
        sys.exit(1)

    result_id = result_data.get("id", None)
    result_status = result_data.get("status", None)

    if debug:
        log.info(("result={}")
                 .format(
                    ppj(result_data)))
        for k in result_data:
            log.info(("result_data has key={}")
                     .format(
                        k))
        # end of for all result data keys
    # if in debug

    if result_data["status"] == "finished":
        log.info(("accuracy={} num_results={}")
                 .format(
                    result_data["acc_data"]["accuracy"],
                    len(result_data["predictions_json"]["predictions"])))
    else:
        log.info(("job is not done latest results={}")
                 .format(
                    ppj(result_data)))

    log.info(("done getting result.id={} status={}")
             .format(
                result_id,
                result_status))

# end of get_ml_job_results


if __name__ == "__main__":
    get_ml_job_results()

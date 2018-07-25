#!/usr/bin/env python

import os
import sys
import argparse
from spylunking.log.setup_logging import console_logger
from antinex_client.utils import ev
from antinex_client.utils import ppj
from antinex_client.ai_client import AIClient
from antinex_client.consts import LOGIN_FAILED
from antinex_client.consts import SUCCESS
from antinex_client.consts import ERROR
from antinex_client.consts import FAILED


log = console_logger(
    name='get_job')


def get_ml_job():
    """get_ml_job

    Get an ``MLJob`` by database id.

    """

    parser = argparse.ArgumentParser(
            description=("Python client get AI Job by ID"))
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
        help="url endpoint with default http://localhost:8010",
        required=False,
        dest="url")
    parser.add_argument(
        "-i",
        help="User's MLJob.id to look up",
        required=False,
        dest="job_id")
    parser.add_argument(
        "-b",
        help=(
            "optional - path to CA bundle directory for "
            "client encryption over HTTP"),
        required=False,
        dest="ca_dir")
    parser.add_argument(
        "-c",
        help=(
            "optional - path to x509 certificate for "
            "client encryption over HTTP"),
        required=False,
        dest="cert_file")
    parser.add_argument(
        "-k",
        help=(
            "optional - path to x509 key file for "
            "client encryption over HTTP"),
        required=False,
        dest="key_file")
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
        "http://localhost:8010")
    job_id = ev(
        "JOB_ID",
        "job_id-not-set")
    ca_dir = os.getenv(
        "API_CA_BUNDLE_DIR",
        None)
    cert_file = os.getenv(
        "API_CERT_FILE",
        None)
    key_file = os.getenv(
        "API_KEY_FILE",
        None)
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
    if args.job_id:
        job_id = args.job_id
    if args.ca_dir:
        ca_dir = args.ca_dir
    if args.cert_file:
        cert_file = args.cert_file
    if args.key_file:
        key_file = args.key_file
    if args.silent:
        verbose = False
    if args.debug:
        debug = True

    usage = (
        "Please run with "
        "-u <username> "
        "-p <password> "
        "-a <AntiNex URL http://localhost:8010> "
        "-i <job_id> "
        "-b <optional - path to CA bundle directory> "
        "-c <optional - path to x509 ssl certificate file> "
        "-k <optional - path to x509 ssl key file>")

    valid = True
    if not user or user == "user-not-set":
        log.error("missing user")
        valid = False
    if not password or password == "password-not-set":
        log.error("missing password")
        valid = False
    if not job_id or job_id == "job_id-not-set":
        log.error("missing job_id")
        valid = False
    else:
        try:
            job_id = int(job_id)
        except Exception as e:
            log.error("please use -i <job_id with an integer>")
            valid = False
    if not valid:
        log.error(usage)
        sys.exit(1)

    if verbose:
        log.info((
            "creating client user={} url={} job_id={} "
            "ca_dir={} cert_file={} key_file={}").format(
                user,
                url,
                job_id,
                ca_dir,
                cert_file,
                key_file))

    client = AIClient(
        user=user,
        email=email,
        password=password,
        url=url,
        ca_dir=ca_dir,
        cert_file=cert_file,
        key_file=key_file,
        verbose=verbose,
        debug=debug)

    if verbose:
        log.info(("loading request in job_id={}")
                 .format(
                    job_id))

    response = client.get_job_by_id(
        job_id=job_id)

    if response["status"] == SUCCESS:
        if debug:
            log.info(("got a job response={}")
                     .format(
                        response["data"]))
    elif response["status"] == FAILED:
        log.error(("job failed with error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))
        sys.exit(1)
    elif response["status"] == ERROR:
        if "missing " in response["error"]:
            log.error(("Did not find a job with id={} for user={}")
                      .format(
                        job_id,
                        user))
        else:
            log.error(("job had an error='{}' with response={}")
                      .format(
                        response["error"],
                        response["data"]))
        sys.exit(1)
    elif response["status"] == LOGIN_FAILED:
        log.error(("job reported user was not able to log in "
                   "with an error='{}' with response={}")
                  .format(
                    response["error"],
                    response["data"]))
        sys.exit(1)

    job_data = response["data"]

    if len(job_data) == 0:
        log.error(("Did not find a job with id={} for user={}")
                  .format(
                    job_id,
                    user))
        sys.exit(1)

    job_id = job_data.get("id", None)
    job_status = job_data.get("status", None)

    log.info(("job={}")
             .format(
                ppj(job_data)))

    log.info(("done getting job.id={} status={}")
             .format(
                job_id,
                job_status))

# end of get_ml_job


if __name__ == "__main__":
    get_ml_job()

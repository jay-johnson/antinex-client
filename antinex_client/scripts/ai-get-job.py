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
        help="url endpoint with default http://localhost:8080",
        required=False,
        dest="url")
parser.add_argument(
        "-i",
        help="User's MLJob.id to look up",
        required=False,
        dest="job_id")
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
job_id = ev(
    "JOB_ID",
    "job_id-not-set")
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
if args.silent:
    verbose = False
if args.debug:
    debug = True

usage = ("Please run with -u <username> "
         "-p <password> -e <email> "
         "-a <AntiNex URL http://localhost:8080> -i <job_id>")

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
    log.info(("creating client user={} url={} job_id={}")
             .format(
                user,
                url,
                job_id))

client = AIClient(
    user=user,
    email=email,
    password=password,
    url=url,
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
elif response["status"] == ERROR:
    log.error(("job had an error='{}' with response={}")
              .format(
                response["error"],
                response["data"]))
elif response["status"] == LOGIN_FAILED:
    log.error(("job reported user was not able to log in "
               "with an error='{}' with response={}")
              .format(
                response["error"],
                response["data"]))

job_data = response["data"]
job_id = job_data.get("id", None)
job_status = job_data.get("status", None)

log.info(("job={}")
         .format(
            ppj(job_data)))

log.info(("done getting job.id={}")
         .format(
            job_id))

sys.exit(0)

#!/usr/bin/env python


import os
import sys
import json
import argparse
import pandas as pd
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


def train_new_deep_neural_network():
    """train_new_deep_neural_network

    Train a new deep neural network and store the results as a new:
    ``MLJob`` and ``MLJobResult`` database records.

    """

    parser = argparse.ArgumentParser(
            description=("Python client to Train a Deep Neural Network "
                         "with AntiNex Django Rest Framework"))
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
            dest="datafile")
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
    datafile = ev(
        "DATAFILE",
        "datafile-not-set")
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
    if args.datafile:
        datafile = args.datafile
    if args.silent:
        verbose = False
    if args.debug:
        debug = True

    usage = ("Please run with -u <username> "
             "-p <password> -e <email> "
             "-a <AntiNex URL http://localhost:8080> -f <path to json file>")

    valid = True
    if not user or user == "user-not-set":
        log.error("missing user")
        valid = False
    if not password or password == "password-not-set":
        log.error("missing password")
        valid = False
    if not datafile or datafile == "datafile-not-set":
        log.error("missing datafile")
        valid = False
    else:
        if not os.path.exists(datafile):
            log.error(("did not find datafile={} on disk")
                      .format(
                        datafile))
            valid = False
    if not valid:
        log.error(usage)
        sys.exit(1)

    if verbose:
        log.info(("creating client user={} url={} file={}")
                 .format(
                    user,
                    url,
                    datafile))

    client = AIClient(
        user=user,
        email=email,
        password=password,
        url=url,
        verbose=verbose,
        debug=debug)

    if verbose:
        log.info(("loading request in datafile={}")
                 .format(
                    datafile))

    req_body = None
    with open(datafile, "r") as f:
        req_body = json.loads(f.read())

    if verbose:
        log.info("running job")

    job_was_started = False
    response = client.run_job(
        body=req_body)

    if response["status"] == SUCCESS:
        log.info(("job started with response={}")
                 .format(
                    response["data"]))
        job_was_started = True
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

    if not job_was_started:
        sys.exit(1)

    if debug:
        log.info(("parsing response data={}")
                 .format(
                    response["data"]))
    else:
        if verbose:
            log.info("parsing data")

    res_data = response["data"]

    job_data = res_data.get(
        "job",
        None)
    result_data = res_data.get(
        "results",
        None)

    if not job_data:
        log.error(("missing job dictionary in response data={}")
                  .format(
                    response["data"]))
        sys.exit(1)
    if not result_data:
        log.error(("missing results dictionary in response data={}")
                  .format(
                    response["data"]))
        sys.exit(1)

    job_id = job_data.get("id", None)
    job_status = job_data.get("status", None)
    result_id = result_data.get("id", None)
    result_status = result_data.get("status", None)

    log.info(("started job.id={} job.status={} with "
              "result.id={} result.status={}")
             .format(
                job_id,
                job_status,
                result_id,
                result_status))

    job_results = client.wait_for_job_to_finish(
        job_id=job_id)

    if job_results["status"] != SUCCESS:
        log.error(("failed waiting for job.id={} to finish error={} data={}")
                  .format(
                    job_id,
                    job_results["error"],
                    job_results["data"]))
        sys.exit(1)

    final_job = job_results["data"]["job"]
    final_result = job_results["data"]["result"]

    log.info(("job={}")
             .format(
                ppj(final_job)))

    log.info(("result={}")
             .format(
                ppj(final_result)))

    log.info(("job.id={} is done")
             .format(
                job_id))

    predictions = final_result["predictions_json"].get(
        "predictions",
        [])

    log.info(("loading predictions={} into pandas dataframe")
             .format(
                len(predictions)))

    df = pd.DataFrame(predictions)

    log.info(("dataframe={}")
             .format(
                df))

# end of train_new_deep_neural_network


if __name__ == "__main__":
    train_new_deep_neural_network()

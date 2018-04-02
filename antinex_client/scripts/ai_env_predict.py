#!/usr/bin/env python


import sys
import json
import argparse
import pandas as pd
from antinex_client.log.setup_logging import build_colorized_logger
from antinex_client.utils import ev
from antinex_client.utils import ppj
from antinex_client.consts import LOGIN_FAILED
from antinex_client.consts import SUCCESS
from antinex_client.consts import ERROR
from antinex_client.consts import FAILED
from antinex_client.build_ai_client_from_env import build_ai_client_from_env
from antinex_client.generate_ai_request import generate_ai_request


name = "ai-env-client"
log = build_colorized_logger(name=name)


def start_predictions():
    """start_predictions

    Using environment variables, create an AntiNex AI Client.
    You can also use command line args if you want.

    This can train a new deep neural network if it does not
    exist or it can use an existing pre-trained deep neural
    network within the AntiNex Core to make new predictions.

    """

    parser = argparse.ArgumentParser(
            description=("Python client to make Predictions "
                         "using a Pre-trained Deep Neural Network "
                         "with AntiNex Django Rest Framework"))
    parser.add_argument(
            "-f",
            help=("file to use default ./examples/"
                  "predict-rows-scaler-full-django.json"),
            required=False,
            dest="datafile")
    parser.add_argument(
            "-m",
            help="send mock data",
            required=False,
            dest="use_fake_rows",
            action="store_true")
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

    datafile = ev(
        "DATAFILE",
        "./examples/predict-rows-scaler-full-django.json")
    verbose = bool(str(ev(
        "ANTINEX_CLIENT_VERBOSE",
        "1")).lower() == "1")
    debug = bool(str(ev(
        "ANTINEX_CLIENT_DEBUG",
        "0")).lower() == "1")

    use_fake_rows = False

    if args.use_fake_rows:
        use_fake_rows = True
    if args.datafile:
        datafile = args.datafile
    if args.silent:
        verbose = False
    if args.debug:
        debug = True

    if verbose:
        log.info("creating client")

    client = build_ai_client_from_env()

    if verbose:
        log.info(("loading request in datafile={}")
                 .format(
                    datafile))

# pass in full or partial prediction record dictionaries
# the generate_ai_request will fill in gaps with defaults
    fake_rows_for_predicting = [
        {
            "tcp_seq": 1
        },
        {
            "tcp_seq": 2
        },
        {
            "tcp_seq": 3
        },
        {
            "tcp_seq": 4
        }
    ]

    res_gen = None
    if use_fake_rows:
        res_gen = generate_ai_request(
            predict_rows=fake_rows_for_predicting)
    else:
        req_with_org_rows = None
        with open(datafile, "r") as f:
            req_with_org_rows = json.loads(f.read())

        res_gen = generate_ai_request(
            predict_rows=req_with_org_rows["predict_rows"])
# end of sending mock data from this file or a file on disk

    if res_gen["status"] != SUCCESS:
        log.error(("failed generate_ai_request with error={}")
                  .format(
                    res_gen["error"]))
        sys.exit(1)

    req_body = res_gen["data"]

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

# end of start_predictions


if __name__ == "__main__":
    start_predictions()

import os
import json
import copy
from antinex_client.log.setup_logging import build_colorized_logger
from antinex_client.utils import ppj
from antinex_client.consts import FAILED
from antinex_client.consts import SUCCESS
from antinex_client.consts import NOT_SET
from antinex_client.consts import ERROR
from antinex_client.consts import DISABLED
from antinex_client.consts import ANTINEX_PUBLISH_ENABLED
from antinex_client.consts import ANTINEX_PUBLISH_REQUEST_FILE
from antinex_client.consts import ANTINEX_FEATURES_TO_PROCESS
from antinex_client.consts import ANTINEX_IGNORE_FEATURES
from antinex_client.consts import ANTINEX_SORT_VALUES
from antinex_client.consts import ANTINEX_ML_TYPE
from antinex_client.consts import ANTINEX_USE_MODEL_NAME
from antinex_client.consts import ANTINEX_PREDICT_FEATURE
from antinex_client.consts import ANTINEX_SEED
from antinex_client.consts import ANTINEX_TEST_SIZE
from antinex_client.consts import ANTINEX_BATCH_SIZE
from antinex_client.consts import ANTINEX_EPOCHS
from antinex_client.consts import ANTINEX_NUM_SPLITS
from antinex_client.consts import ANTINEX_LOSS
from antinex_client.consts import ANTINEX_OPTIMIZER
from antinex_client.consts import ANTINEX_METRICS
from antinex_client.consts import ANTINEX_HISTORIES
from antinex_client.consts import FILTER_FEATURES_DICT
from antinex_client.consts import FILTER_FEATURES
from antinex_client.consts import ANTINEX_CONVERT_DATA
from antinex_client.consts import ANTINEX_CONVERT_DATA_TYPE
from antinex_client.consts import ANTINEX_INCLUDE_FAILED_CONVERSIONS
from antinex_client.consts import ANTINEX_PUBLISH_TO_CORE
from antinex_client.consts import ANTINEX_CHECK_MISSING_PREDICT
from antinex_client.consts import ANTINEX_MISSING_VALUE
from antinex_client.consts import ANTINEX_VERSION
from antinex_client.consts import ANTINEX_CLIENT_DEBUG


name = "ai-req"
log = build_colorized_logger(name=name)


def generate_ai_request(
        predict_rows,
        req_dict=None,
        req_file=ANTINEX_PUBLISH_REQUEST_FILE,
        features=ANTINEX_FEATURES_TO_PROCESS,
        ignore_features=ANTINEX_IGNORE_FEATURES,
        sort_values=ANTINEX_SORT_VALUES,
        ml_type=ANTINEX_ML_TYPE,
        use_model_name=ANTINEX_USE_MODEL_NAME,
        predict_feature=ANTINEX_PREDICT_FEATURE,
        seed=ANTINEX_SEED,
        test_size=ANTINEX_TEST_SIZE,
        batch_size=ANTINEX_BATCH_SIZE,
        epochs=ANTINEX_EPOCHS,
        num_splits=ANTINEX_NUM_SPLITS,
        loss=ANTINEX_LOSS,
        optimizer=ANTINEX_OPTIMIZER,
        metrics=ANTINEX_METRICS,
        histories=ANTINEX_HISTORIES,
        filter_features_dict=FILTER_FEATURES_DICT,
        filter_features=FILTER_FEATURES,
        convert_enabled=ANTINEX_CONVERT_DATA,
        convert_to_type=ANTINEX_CONVERT_DATA_TYPE,
        include_failed_conversions=ANTINEX_INCLUDE_FAILED_CONVERSIONS,
        value_for_missing=ANTINEX_MISSING_VALUE,
        version=ANTINEX_VERSION,
        publish_to_core=ANTINEX_PUBLISH_TO_CORE,
        check_missing_predict_feature=ANTINEX_CHECK_MISSING_PREDICT,
        debug=ANTINEX_CLIENT_DEBUG):
    """generate_ai_request

    :param predict_rows: list of predict rows to build into the request
    :param req_dict: request dictionary to update - for long-running clients
    :param req_file: file holding a request dict to update - one-off tests
    :param features: features to process in the data
    :param ignore_features: features to ignore in the data (non-numerics)
    :param sort_values: optional - order rows for scaler normalization
    :param ml_type: machine learning type - classification/regression
    :param use_model_name: use a pre-trained model by name
    :param predict_feature: predict the values of this feature
    :param seed: seed for randomness reproducability
    :param test_size: split train/test data
    :param batch_size: batch size for processing
    :param epochs: test epochs
    :param num_splits: test splits for cross validation
    :param loss: loss function
    :param optimizer: optimizer
    :param metrics: metrics to apply
    :param histories: historical values to test
    :param filter_features_dict: dictionary of features to use
    :param filter_features: list of features to use
    :param convert_to_type: convert predict_row values to scaler-ready values
    :param include_failed_conversions: should the predict rows include fails
    :param value_for_missing: set this value to any columns that are missing
    :param version: version of the API request
    :param publish_to_core: want to publish it to the core or the worker
    :param debug: log debug messages
    """

    status = NOT_SET
    err = "not-set"
    data = None

    if not ANTINEX_PUBLISH_ENABLED:
        log.info(("publish disabled ANTINEX_PUBLISH_ENABLED={}")
                 .format(
                    ANTINEX_PUBLISH_ENABLED))
        status = DISABLED
        err = "disabled"
        return {
            "status": status,
            "error": err,
            "data": None}
    # stop if not enabled

    try:

        err = "checking number of predict rows"
        if len(predict_rows) == 0:
            err = "please provide a list of predict_rows"
            log.error(err)
            status = FAILED
            res = {
                "status": status,
                "error": err,
                "data": None}
            return res
        # stop if there's no new rows

        body = None
        if not req_dict:
            if os.path.exists(req_file):
                with open(req_file, "r") as f:
                    body = json.loads(f.read())
        else:
            body = copy.deepcopy(
                req_dict)
        # end of loading body from requested

        if not body:
            err = ("failed to load request body "
                   "req_dict={} req_file={}").format(
                       req_dict,
                       req_file)
            log.error(err)
            status = FAILED

            res = {
                "status": status,
                "error": err,
                "data": None}
            return res
        # if body is empty

        err = ("setting values rows={} body={} features={}").format(
            len(predict_rows),
            body,
            filter_features)

        if debug:
            log.info(err)

        use_predict_rows = []
        for r in predict_rows:
            new_row = {}
            for col in r:
                cur_value = r[col]
                if col in filter_features_dict:
                    if not cur_value:
                        cur_value = value_for_missing
                    if ANTINEX_CONVERT_DATA:
                        try:
                            if convert_to_type == "float":
                                new_row[col] = float(cur_value)
                            elif convert_to_type == "int":
                                new_row[col] = int(cur_value)
                        except Exception as e:
                            if include_failed_conversions:
                                new_row[col] = cur_value
                            else:
                                log.error(("failed converting {}={} type={}")
                                          .format(
                                            col,
                                            cur_value,
                                            convert_to_type))
                        # if conversion failed
                    else:
                        new_row[col] = cur_value
                    # if not converting data
                # if the column is in the filtered features
            # for all columns in the row dictionary

            for col in filter_features:
                if col not in new_row:
                    new_row[col] = value_for_missing
            # make sure to fill in missing columns with a default

            if check_missing_predict_feature:
                if predict_feature not in new_row:
                    new_row[predict_feature] = value_for_missing

            use_predict_rows.append(new_row)
        # for all predict rows to convert and fileter

        err = ("converted rows={} to use_rows={}").format(
            len(predict_rows),
            len(use_predict_rows))

        log.info(err)

        body["label"] = use_model_name
        body["predict_feature"] = predict_feature
        body["predict_rows"] = use_predict_rows
        body["publish_to_core"] = publish_to_core
        body["seed"] = seed
        body["test_size"] = test_size
        body["batch_size"] = batch_size
        body["epochs"] = epochs
        body["num_splits"] = num_splits
        body["loss"] = loss
        body["optimizer"] = optimizer
        body["metrics"] = metrics
        body["histories"] = histories
        body["ml_type"] = ml_type
        if sort_values:
            body["sort_values"] = sort_values
        if filter_features:
            body["features_to_process"] = filter_features
        if ignore_features:
            body["ignore_features"] = ignore_features

        data = body

        if debug:
            log.info(("req={}")
                     .format(
                        ppj(data)))

        status = SUCCESS
        err = ""
    except Exception as e:
        log.error(("failed last_step='{}' with ex={}")
                  .format(
                    err,
                    e))
        status = ERROR
    # end of try/ex

    res = {
        "status": status,
        "error": err,
        "data": data}
    return res
# end of generate_ai_request

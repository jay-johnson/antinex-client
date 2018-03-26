import os
from antinex_client.utils import ev


LOGIN_SUCCESS = 0
LOGIN_NOT_ATTEMPTED = 1
LOGIN_FAILED = 2
SUCCESS = 0
FAILED = 1
ERROR = 2
NOT_SET = 3
DISABLED = 4


# AntiNex REST API flags, endpoint and credentials
# https://github.com/jay-johnson/train-ai-with-django-swagger-jwt
#
# AntiNex is running using compose.yml file:
# noqa https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/master/compose.yml
#
# AntiNex python client:
# https://github.com/jay-johnson/antinex-client
ANTINEX_PUBLISH_ENABLED = bool(ev(
    "ANTINEX_PUBLISH_ENABLED",
    "1") == "1")
ANTINEX_URL = ev(
    "ANTINEX_URL",
    "http://localhost:8080")
ANTINEX_CA_FILE = os.getenv(
    "ANTINEX_CA_FILE",
    None)
ANTINEX_CERT_FILE = os.getenv(
    "ANTINEX_CERT_FILE",
    None)
ANTINEX_KEY_FILE = os.getenv(
    "ANTINEX_KEY_FILE",
    None)
ANTINEX_USER = ev(
    "ANTINEX_USER",
    "root")
ANTINEX_EMAIL = ev(
    "ANTINEX_EMAIL",
    "notreal@test.com")
ANTINEX_PASSWORD = ev(
    "ANTINEX_PASSWORD",
    "123321")
# provide a template request publish file like:
# noqa https://github.com/jay-johnson/antinex-client/blob/master/examples/predict-rows-scaler-full-django.json
ANTINEX_PUBLISH_REQUEST_FILE = ev(
    "ANTINEX_PUBLISH_REQUEST_FILE",
    ("/opt/antinex-client/examples/"
     "predict-rows-scaler-full-django.json"))
# comma-separated list
ANTINEX_FEATURES_TO_PROCESS_STR = os.getenv(
    "ANTINEX_FEATURES_TO_PROCESS",
    None)
# comma-separated list
ANTINEX_IGNORE_FEATURES_STR = os.getenv(
    "ANTINEX_IGNORE_FEATURES",
    None)
# comma-separated list
ANTINEX_SORT_VALUES_STR = os.getenv(
    "ANTINEX_SORT_VALUES",
    None)
# comma-separated list
ANTINEX_METRICS_STR = os.getenv(
    "ANTINEX_METRICS",
    None)
# comma-separated list
ANTINEX_HISTORIES_STR = os.getenv(
    "ANTINEX_HISTORIES",
    None)
ANTINEX_ML_TYPE = ev(
    "ANTINEX_ML_TYPE",
    "classification")
ANTINEX_USE_MODEL_NAME = ev(
    "ANTINEX_USE_MODEL_NAME",
    "Full-Django-AntiNex-Simple-Scaler-DNN")
ANTINEX_PREDICT_FEATURE = ev(
    "ANTINEX_PREDICT_FEATURE",
    "label_value")
ANTINEX_SEED = int(ev(
    "ANTINEX_SEED",
    "42"))
ANTINEX_TEST_SIZE = float(ev(
    "ANTINEX_TEST_SIZE",
    "0.2"))
ANTINEX_BATCH_SIZE = int(ev(
    "ANTINEX_BATCH_SIZE",
    "32"))
ANTINEX_EPOCHS = int(ev(
    "ANTINEX_EPOCHS",
    "15"))
ANTINEX_NUM_SPLITS = int(ev(
    "ANTINEX_NUM_SPLITS",
    "3"))
ANTINEX_LOSS = ev(
    "ANTINEX_LOSS",
    "binary_crossentropy")
ANTINEX_OPTIMIZER = ev(
    "ANTINEX_OPTIMIZER",
    "adam")
ANTINEX_VERSION = ev(
    "ANTINEX_VERSION",
    "1")
ANTINEX_CONVERT_DATA = bool(ev(
    "ANTINEX_CONVERT_DATA",
    "1") == "1")
ANTINEX_CONVERT_DATA_TYPE = ev(
    "ANTINEX_CONVERT_DATA_TYPE",
    "float")
ANTINEX_INCLUDE_FAILED_CONVERSIONS = bool(ev(
    "ANTINEX_INCLUDE_FAILED_CONVERSIONS",
    "0") == "1")
ANTINEX_MISSING_VALUE = ev(
    "ANTINEX_MISSING_VALUE",
    "-1.0")
ANTINEX_PUBLISH_TO_CORE = bool(ev(
    "ANTINEX_PUBLISH_TO_CORE",
    "1") == "1")
ANTINEX_CHECK_MISSING_PREDICT = bool(ev(
    "ANTINEX_CHECK_MISSING_PREDICT",
    "1") == "1")
ANTINEX_CLIENT_VERBOSE = bool(ev(
    "ANTINEX_CLIENT_VERBOSE",
    "1") == "1")
ANTINEX_CLIENT_DEBUG = bool(ev(
    "ANTINEX_CLIENT_DEBUG",
    "0") == "1")

# set empty defaults
ANTINEX_FEATURES_TO_PROCESS = []
ANTINEX_IGNORE_FEATURES = []
ANTINEX_SORT_VALUES = []
ANTINEX_METRICS = []
ANTINEX_HISTORIES = []

if ANTINEX_FEATURES_TO_PROCESS_STR:
    ANTINEX_FEATURES_TO_PROCESS = \
        ANTINEX_FEATURES_TO_PROCESS_STR.split(",")
if ANTINEX_IGNORE_FEATURES_STR:
    ANTINEX_IGNORE_FEATURES = \
        ANTINEX_IGNORE_FEATURES_STR.split(",")
if ANTINEX_SORT_VALUES_STR:
    ANTINEX_SORT_VALUES = \
        ANTINEX_SORT_VALUES_STR.split(",")
if ANTINEX_METRICS_STR:
    ANTINEX_METRICS = \
        ANTINEX_METRICS_STR.split(",")
if ANTINEX_HISTORIES_STR:
    ANTINEX_HISTORIES = \
        ANTINEX_HISTORIES_STR.split(",")

FILTER_FEATURES_DICT = {}
FILTER_FEATURES = []
for idx, f in enumerate(ANTINEX_FEATURES_TO_PROCESS):
    include_feature = True
    if f == ANTINEX_PREDICT_FEATURE:
        include_feature = False
    for i in ANTINEX_IGNORE_FEATURES:
        if f == i:
            include_feature = False
            break
    if include_feature:
        FILTER_FEATURES.append(f)
        FILTER_FEATURES_DICT[f] = idx
# end of for all features not being ignored

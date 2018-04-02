Train a Deep Neural Network and Make Predictions
================================================

This uses environment variables to build, train and make predictions using the AntiNex client.

This python script is available in the pip: ``ai_env_predict.py``

It takes parameters:

::

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

Source Code
-----------

.. automodule:: antinex_client.scripts.ai_env_predict
    :members: start_predictions

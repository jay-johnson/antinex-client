Prepare a New Dataset
=====================

This python script is available in the pip: ``ai_prepare_dataset.py``

It takes parameters:

::

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

Source Code
-----------

.. automodule:: antinex_client.scripts.ai_prepare_dataset
    :members: prepare_new_dataset

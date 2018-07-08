Get an ML Job
=============

This python script is available in the pip: ``ai_get_job.py``

It takes parameters:

::

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

.. automodule:: antinex_client.scripts.ai_get_job
    :members: get_ml_job

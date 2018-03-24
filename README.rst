AntiNex Python Client
=====================

Python API Client for training deep neural networks with the REST API running:

https://github.com/jay-johnson/train-ai-with-django-swagger-jwt

Install
-------

pip install antinex-client

Run Predictions
===============

These examples use the default user ``root`` with password ``123321``. It is advised to change this to your own user in the future.

Train a Deep Neural Network with a JSON List of Records
-------------------------------------------------------

::

    ai-train-dnn.py -u root -p 123321 -f examples/predict-rows-scaler-django-simple.json

Train a Deep Neural Network to Predict Attacks with the AntiNex Datasets
------------------------------------------------------------------------

Please make sure the datasets are available to the REST API, Celery worker, and AntiNex Core worker. The datasets are already included in the docker container ``ai-core`` provided in the default ``compose.yml`` file:

https://github.com/jay-johnson/train-ai-with-django-swagger-jwt/blob/51f731860daf134ea2bd3b68468927c614c83ee5/compose.yml#L53-L104

If you're running outside docker make sure to clone the repo with:

::

    git clone https://github.com/jay-johnson/antinex-datasets.git /opt/antinex-datasets    

Train the Django Defensive Deep Neural Network
----------------------------------------------

Please wait as this will take a few minutes to return and convert the predictions to a pandas DataFrame.

::

    ai-train-dnn.py -u root -p 123321 -f examples/scaler-full-django-antinex-simple.json 

    ...

    [30200 rows x 72 columns]


Development
-----------
::

    virtualenv -p python3 ~/.venvs/antinexclient && source ~/.venvs/antinexcore/bin/activate && pip install -e .

Testing
-------

Run all

::

    python setup.py test

Linting
-------

flake8 .

pycodestyle --exclude=.tox,.eggs

License
-------

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/jay-johnson/antinex-client/blob/master/LICENSE

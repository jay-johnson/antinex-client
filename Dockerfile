FROM jayjohnson/ai-core:latest

RUN echo "creating project directories" \
  && mkdir -p -m 777 /var/log/antinex/client \
  && mkdir -p -m 777 /opt/antinex \
  && chmod 777 //var/log/antinex/client \
  && touch /var/log/antinex/client/client.log \
  && chmod 777 /var/log/antinex/client/client.log \
  && echo "updating repo" \
  && cd /opt/antinex/client \
  && git checkout master \
  && git pull \
  && echo "checking repo in container" \
  && ls -l /opt/antinex/client \
  && echo "activating venv" \
  && . /opt/venv/bin/activate \
  && cd /opt/antinex/client \
  && echo "installing pip upgrades" \
  && pip install --upgrade -e . \
  && echo "building docs" \
  && cd /opt/antinex/client/docs \
  && ls -l \
  && make html

ENV PROJECT_NAME="client" \
    SHARED_LOG_CFG="/opt/antinex/core/antinex_core/log/debug-openshift-logging.json" \
    DEBUG_SHARED_LOG_CFG="0" \
    LOG_LEVEL="DEBUG" \
    LOG_FILE="/var/log/antinex/client/client.log" \
    USE_ENV="drf-dev" \
    USE_VENV="/opt/venv" \
    API_USER="trex" \
    API_PASSWORD="123321" \
    API_EMAIL="bugs@antinex.com" \
    API_FIRSTNAME="Guest" \
    API_LASTNAME="Guest" \
    API_URL="http://api.antinex.com:8010" \
    API_VERBOSE="true" \
    API_DEBUG="false" \
    USE_FILE="false" \
    SILENT="-s"

WORKDIR /opt/antinex/client

# set for anonymous user access in the container
RUN find /opt/antinex/client -type d -exec chmod 777 {} \;
RUN find /var/log/antinex -type d -exec chmod 777 {} \;

ENTRYPOINT . /opt/venv/bin/activate \
  && /opt/antinex/client/antinex_client/ai \
     -u ${API_USER} \
     -p ${API_PASSWORD} \
     -f ${USE_FILE} \
     -a ${API_URL} ${SILENT}

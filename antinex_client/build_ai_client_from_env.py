from antinex_client.log.setup_logging import build_colorized_logger
from antinex_client.ai_client import AIClient
from antinex_client.consts import ANTINEX_PUBLISH_ENABLED
from antinex_client.consts import ANTINEX_URL
from antinex_client.consts import ANTINEX_CA_FILE
from antinex_client.consts import ANTINEX_KEY_FILE
from antinex_client.consts import ANTINEX_CERT_FILE
from antinex_client.consts import ANTINEX_USER
from antinex_client.consts import ANTINEX_EMAIL
from antinex_client.consts import ANTINEX_PASSWORD
from antinex_client.consts import ANTINEX_CLIENT_VERBOSE
from antinex_client.consts import ANTINEX_CLIENT_DEBUG


name = "build-ai-client-from-env"
log = build_colorized_logger(name=name)


def build_ai_client_from_env(
        verbose=ANTINEX_CLIENT_VERBOSE,
        debug=ANTINEX_CLIENT_DEBUG):
    """build_ai_client_from_env
       Use environment variables to build a client
    """

    if not ANTINEX_PUBLISH_ENABLED:
        log.info(("publish disabled ANTINEX_PUBLISH_ENABLED={}")
                 .format(
                    ANTINEX_PUBLISH_ENABLED))
        return None

    if ANTINEX_CA_FILE or ANTINEX_KEY_FILE or ANTINEX_CERT_FILE:
        log.info(("creating secure client user={} url={} ca={} cert={} key={}")
                 .format(
                    ANTINEX_USER,
                    ANTINEX_URL,
                    ANTINEX_CA_FILE,
                    ANTINEX_KEY_FILE,
                    ANTINEX_CERT_FILE))
    else:
        log.info(("creating non-secure client user={} url={}")
                 .format(
                    ANTINEX_USER,
                    ANTINEX_URL))
    # if secure or dev

    return AIClient(
        user=ANTINEX_USER,
        email=ANTINEX_EMAIL,
        password=ANTINEX_PASSWORD,
        url=ANTINEX_URL,
        ca_file=ANTINEX_CA_FILE,
        cert_file=ANTINEX_CERT_FILE,
        key_file=ANTINEX_KEY_FILE,
        verbose=verbose,
        debug=debug)
# end of build_ai_client_from_env

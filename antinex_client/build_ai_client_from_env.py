from spylunking.log.setup_logging import console_logger
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


log = console_logger(
    name='build_ai_client_from_env')


def build_ai_client_from_env(
        verbose=ANTINEX_CLIENT_VERBOSE,
        debug=ANTINEX_CLIENT_DEBUG,
        ca_dir=None,
        cert_file=None,
        key_file=None):
    """build_ai_client_from_env

    Use environment variables to build a client

    :param verbose: verbose logging
    :param debug: debug internal client calls
    :param ca_dir: optional path to CA bundle dir
    :param cert_file: optional path to x509 ssl cert file
    :param key_file: optional path to x509 ssl key file
    """

    if not ANTINEX_PUBLISH_ENABLED:
        log.info((
            "publish disabled ANTINEX_PUBLISH_ENABLED={}").format(
                ANTINEX_PUBLISH_ENABLED))
        return None

    use_ca_dir = ca_dir
    use_cert_file = cert_file
    use_key_file = key_file

    if ANTINEX_CA_FILE or ANTINEX_KEY_FILE or ANTINEX_CERT_FILE:
        use_ca_dir = ANTINEX_CA_FILE
        use_cert_file = ANTINEX_CERT_FILE
        use_key_file = ANTINEX_KEY_FILE
        log.info((
            "creating env client user={} url={} "
            "ca={} cert={} key={}").format(
                ANTINEX_USER,
                ANTINEX_URL,
                ANTINEX_CA_FILE,
                ANTINEX_CERT_FILE,
                ANTINEX_KEY_FILE))
    else:
        log.info((
            "creating client user={} url={} "
            "ca={} cert={} key={}").format(
                ANTINEX_USER,
                ANTINEX_URL,
                use_ca_dir,
                use_cert_file,
                use_key_file))
    # if secure or dev

    return AIClient(
        user=ANTINEX_USER,
        email=ANTINEX_EMAIL,
        password=ANTINEX_PASSWORD,
        url=ANTINEX_URL,
        ca_dir=use_ca_dir,
        cert_file=use_cert_file,
        key_file=use_key_file,
        verbose=verbose,
        debug=debug)
# end of build_ai_client_from_env

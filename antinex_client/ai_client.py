import json
import requests
import logging
import time
from antinex_client.log.setup_logging import build_colorized_logger
from antinex_client.utils import ev


name = "ai-client"
log_level = logging.INFO
log_level_str = ev(
    "AI_CLIENT_LEVEL",
    "info").lower()
if log_level_str == "info":
    log_level = logging.INFO
elif log_level_str == "debug":
    log_level = logging.DEBUG
elif log_level_str == "silent":
    log_level = logging.CRITICAL
elif log_level_str == "critical":
    log_level = logging.CRITICAL
elif log_level_str == "error":
    log_level = logging.ERROR

log = build_colorized_logger(
    name=name,
    log_level=log_level)

LOGIN_SUCCESS = 0
LOGIN_NOT_ATTEMPTED = 1
LOGIN_FAILED = 2
SUCCESS = 0
FAILED = 1
ERROR = 2
NOT_SET = 3


class AIClient:

    def __init__(
            self,
            user=ev(
                "API_USER",
                "user-not-set"),
            password=ev(
                "API_PASSWORD",
                "password-not-set"),
            url=ev(
                "API_URL",
                "http://localhost:8080"),
            email=ev(
                "API_EMAIL",
                "email-not-set"),
            verbose=True,
            debug=False):
        """__init__

        :param name: log name
        :param user: username
        :param email: email address
        :param password: password for the user
        :param url: url running the django rest framework
        :param verbose: turn off setup_logging
        """

        self.user = user
        self.email = email
        self.password = password
        self.url = url
        self.verbose = verbose
        self.debug = debug

        if self.debug:
            self.verbose = True

        self.api_urls = {
            "login": "{}/api-token-auth/".format(self.url),
            "job": "{}/ml/".format(self.url),
            "prepare": "{}/mlprepare/".format(self.url),
            "results": "{}/mlresults/".format(self.url),
            "create_user": "{}/users/".format(self.url)
        }
        self.token = "not-logged-in-no-token"
        self.login_status = LOGIN_NOT_ATTEMPTED
        self.user_id = None
        self.max_retries = 10
        self.login_retry_wait_time = 0.1  # in seconds
        self.all_prepares = {}
        self.all_jobs = {}
        self.all_results = {}
    # end of __init__

    def login(
            self):

        auth_url = self.api_urls["login"]

        if self.verbose:
            log.info(("log in user={} url={}")
                     .format(
                        self.user,
                        auth_url))

        use_headers = {
            "Content-type": "application/json"
        }
        login_data = {
            "username": self.user,
            "password": self.password
        }

        if self.debug:
            log.info(("LOGIN with body={} headers={} url={}")
                     .format(
                        login_data,
                        use_headers,
                        auth_url))

        response = requests.post(
            auth_url,
            data=json.dumps(login_data),
            headers=use_headers)

        if self.debug:
            log.info(("LOGIN response status_code={} text={} reason={}")
                     .format(
                        response.status_code,
                        response.text,
                        response.reason))

        user_token = ""
        if response.status_code == 200:
            user_token = json.loads(response.text)["token"]

        if user_token != "":
            self.token = user_token
            self.login_status = LOGIN_SUCCESS

            if self.verbose:
                log.debug("login success")
        else:
            log.error(("failed to login user={} to url={} text={}")
                      .format(
                        self.user,
                        auth_url,
                        response.text))
            self.login_status = LOGIN_FAILED
        # if the user token exists

        return self.login_status
    # end of login

    def is_logged_in(
            self):
        """is_logged_in"""
        return self.login_status == LOGIN_SUCCESS
    # end of is_logged_in

    def get_token(
            self):
        """get_token"""
        return self.token
    # end of get_token

    def get_auth_header(
            self):
        headers = {
            "Content-type": "application/json",
            "Authorization": "JWT {}".format(self.get_token())
        }
        return headers
    # end of get_auth_header

    def build_response(
            self,
            status=NOT_SET,
            error="",
            data=None):
        """build_response

        :param status: status code
        :param error: error message
        :param data: dictionary to send back
        """

        res_node = {
            "status": status,
            "error": error,
            "data": data
        }
        return res_node
    # end of build_response

    def retry_login(
            self):
        """retry_login"""

        if not self.user or not self.password:
            return self.build_response(
                status=ERROR,
                error="please set the user and password")

        retry = 0
        not_done = True
        while not_done:
            if self.is_logged_in():
                return self.build_response(
                    status=SUCCESS)
            else:
                if self.verbose:
                    log.debug(("login attempt={} max={}")
                              .format(
                                retry,
                                self.max_retries))

                if self.login() == LOGIN_SUCCESS:
                    return self.build_response(
                        status=SUCCESS)
                else:
                    time.sleep(
                        self.login_retry_wait_time)
            # if able to login or not
            retry += 1
            if retry > self.max_retries:
                return self.build_response(
                    status=ERROR,
                    error="failed logging in user={} retries={}".format(
                            self.user,
                            self.max_retries))
        # if login worked or not

        return self.build_response(
            status=FAILED,
            error="user={} not able to login attempts={}".format(
                self.user,
                retry))
    # end of retry_login

    def get_job_by_id(
            self,
            job_id=None):
        """get_job_by_id

        :param job_id: MLJob.id in the database
        """

        if not job_id:
            log.error("missing job_id for get_job_by_id")
            return self.build_response(
                status=ERROR,
                error="missing job_id for get_job_by_id")

        if self.verbose:
            log.info(("user={} getting job={}")
                     .format(
                        self.user,
                        job_id))

        url = "{}{}".format(
                self.api_urls["job"],
                job_id)

        not_done = True
        while not_done:

            if self.debug:
                log.info(("JOB attempting to get={} to url={}")
                         .format(
                            job_id,
                            url))

            response = requests.get(
                url,
                headers=self.get_auth_header())

            if self.debug:
                log.info(("JOB response status_code={} text={} reason={}")
                         .format(
                            response.status_code,
                            response.text,
                            response.reason))

            if response.status_code == 401:
                login_res = self.retry_login()
                if login_res["status"] != SUCCESS:
                    if self.verbose:
                        log.error(
                            "retry login attempts failed")
                    return self.build_response(
                        status=login_res["status"],
                        error=login_res["error"])
                # if able to log back in just retry the call
            elif response.status_code == 200:

                if self.verbose:
                    log.debug("deserializing")

                job_data = json.loads(
                    response.text)

                job_id = job_data.get(
                    "id",
                    None)

                if not job_id:
                    return self.build_response(
                        status=ERROR,
                        error="missing job.id",
                        data="text={} reason={}".format(
                            response.reason,
                            response.text))

                self.all_jobs[str(job_id)] = job_data

                if self.verbose:
                    log.info(("added job={} all_jobs={} ")
                             .format(
                                job_id,
                                len(self.all_jobs)))

                return self.build_response(
                    status=SUCCESS,
                    error="",
                    data=job_data)
            else:
                err_msg = ("failed with "
                           "status_code={} text={} reason={}").format(
                               response.status_code,
                               response.text,
                               response.reason)
                if self.verbose:
                    log.error(err_msg)
                return self.build_response(
                    status=ERROR,
                    error=err_msg)
                # if able to log back in just retry the call
            # end of handling response status codes
        # end of while not_done
    # end of get_job_by_id

    def get_result_by_id(
            self,
            result_id=None):
        """get_result_by_id

        :param result_id: MLJobResult.id in the database
        """

        if not result_id:
            log.error("missing result_id for get_result_by_id")
            return self.build_response(
                status=ERROR,
                error="missing result_id for get_result_by_id")

        if self.verbose:
            log.info(("user={} getting result={}")
                     .format(
                        self.user,
                        result_id))

        url = "{}{}".format(
                self.api_urls["results"],
                result_id)

        not_done = True
        while not_done:

            if self.debug:
                log.info(("RESULT attempting to get={} to url={}")
                         .format(
                            result_id,
                            url))

            response = requests.get(
                url,
                headers=self.get_auth_header())

            if self.debug:
                log.info(("RESULT response status_code={} text={} reason={}")
                         .format(
                            response.status_code,
                            response.text,
                            response.reason))

            if response.status_code == 401:
                login_res = self.retry_login()
                if login_res["status"] != SUCCESS:
                    if self.verbose:
                        log.error(
                            "retry login attempts failed")
                    return self.build_response(
                        status=login_res["status"],
                        error=login_res["error"])
                # if able to log back in just retry the call
            elif response.status_code == 200:

                if self.verbose:
                    log.debug("deserializing")

                result_data = json.loads(
                    response.text)

                result_id = result_data.get(
                    "id",
                    None)

                if not result_id:
                    return self.build_response(
                        status=ERROR,
                        error="missing result.id",
                        data="text={} reason={}".format(
                            response.reason,
                            response.text))

                self.all_results[str(result_id)] = result_data

                if self.verbose:
                    log.info(("added result={} all_results={} ")
                             .format(
                                result_id,
                                len(self.all_results)))

                return self.build_response(
                    status=SUCCESS,
                    error="",
                    data=result_data)
            else:
                err_msg = ("failed with "
                           "status_code={} text={} reason={}").format(
                               response.status_code,
                               response.text,
                               response.reason)
                if self.verbose:
                    log.error(err_msg)
                return self.build_response(
                    status=ERROR,
                    error=err_msg)
                # if able to log back in just retry the call
            # end of handling response status codes
        # end of while not_done
    # end of get_result_by_id

    def run_job(
            self,
            body):
        """run_job

        :param body: dictionary to launch job
        """

        if self.verbose:
            log.info(("user={} starting job={}")
                     .format(
                        self.user,
                        str(body)[0:32]))

        url = "{}".format(
                self.api_urls["job"])

        not_done = True
        while not_done:

            if self.debug:
                log.info(("JOB attempting to post={} to url={}")
                         .format(
                            json.dumps(body),
                            url))

            response = requests.post(
                url,
                data=json.dumps(body),
                headers=self.get_auth_header())

            if self.debug:
                log.info(("JOB response status_code={} text={} reason={}")
                         .format(
                            response.status_code,
                            response.text,
                            response.reason))

            if response.status_code == 401:
                login_res = self.retry_login()
                if login_res["status"] != SUCCESS:
                    if self.verbose:
                        log.error(
                            "retry login attempts failed")
                    return self.build_response(
                        status=login_res["status"],
                        error=login_res["error"])
                # if able to log back in just retry the call
            elif response.status_code == 201:

                if self.verbose:
                    log.debug("deserializing")

                res_dict = json.loads(
                    response.text)

                job_data = res_dict.get(
                    "job",
                    None)
                result_data = res_dict.get(
                    "results",
                    None)
                if not job_data:
                    return self.build_response(
                        status=ERROR,
                        error="job failed",
                        data="text={} reason={}".format(
                            response.reason,
                            response.text))

                job_id = job_data.get(
                    "id",
                    None)
                result_id = result_data.get(
                    "id",
                    None)

                if not job_id:
                    return self.build_response(
                        status=ERROR,
                        error="missing job.id",
                        data="text={} reason={}".format(
                            response.reason,
                            response.text))
                if not result_id:
                    return self.build_response(
                        status=ERROR,
                        error="missing result.id",
                        data="text={} reason={}".format(
                            response.reason,
                            response.text))

                self.all_jobs[str(job_id)] = job_data
                self.all_results[str(result_id)] = result_data

                if self.verbose:
                    log.info(("added job={} result={} "
                              "all_jobs={} all_results={}")
                             .format(
                                job_id,
                                result_id,
                                len(self.all_jobs),
                                len(self.all_results)))

                return self.build_response(
                    status=SUCCESS,
                    error="",
                    data=res_dict)
            else:
                err_msg = ("failed with "
                           "status_code={} text={} reason={}").format(
                               response.status_code,
                               response.text,
                               response.reason)
                if self.verbose:
                    log.error(err_msg)
                return self.build_response(
                    status=ERROR,
                    error=err_msg)
                # if able to log back in just retry the call
            # end of handling response status codes
        # end of while not_done
    # end of run_job

    def wait_for_job_to_finish(
            self,
            job_id,
            sec_to_sleep=0.1,
            max_retries=100000):

        not_done = True
        sec_to_sleep = 0.1
        retry_attempt = 0
        while not_done:

            if self.verbose:
                log.info(("JOBSTATUS getting job.id={} details")
                         .format(
                            job_id))

            response = self.get_job_by_id(job_id)

            if self.verbose:
                log.info(("JOBSTATUS got job.id={} response={}")
                         .format(
                            job_id,
                            response))

            if response["status"] != SUCCESS:
                log.error(("JOBSTATUS failed to get job.id={} with error={}")
                          .format(
                            job_id,
                            response["error"]))
                return self.build_response(
                    status=ERROR,
                    error=response["error"],
                    data=response["data"])
            # stop if this failed getting the job details

            job_data = response.get(
                "data",
                None)

            if not job_data:
                return self.build_response(
                    status=ERROR,
                    error="failed to find job dictionary in response",
                    data=response["data"])

            job_status = job_data["status"]

            if job_status == "finished" \
               or job_status == "completed" \
               or job_status == "launched":

                log.info(("job.id={} is done with status={}")
                         .format(
                            job_id,
                            job_status))

                result_id = job_data["predict_manifest"]["result_id"]

                if self.verbose:
                    log.info(("JOBRESULT getting result.id={} details")
                             .format(
                                result_id))

                response = self.get_result_by_id(result_id)

                if self.verbose:
                    log.info(("JOBRESULT got result.id={} response={}")
                             .format(
                                result_id,
                                response))

                if response["status"] != SUCCESS:
                    log.error(("JOBRESULT failed to get "
                               "result.id={} with error={}")
                              .format(
                                result_id,
                                response["error"]))
                    return self.build_response(
                        status=ERROR,
                        error=response["error"],
                        data=response["data"])
                # stop if this failed getting the result details

                result_data = response.get(
                    "data",
                    None)

                full_response = {
                    "job": job_data,
                    "result": result_data
                }

                not_done = False
                return self.build_response(
                    status=SUCCESS,
                    error="",
                    data=full_response)
            else:

                retry_attempt += 1
                if retry_attempt > max_retries:
                    err_msg = ("failed waiting "
                               "for job.id={} to finish").format(
                                   job_id)
                    log.error(err_msg)
                    return self.build_response(
                        status=ERROR,
                        error=err_msg)
                else:
                    if self.verbose:
                        if retry_attempt % 100 == 0:
                            log.info(("waiting on job.id={} retry={}")
                                     .format(
                                        job_id,
                                        retry_attempt))
                    # if logging just to show this is running
                    time.sleep(sec_to_sleep)
        # end of while waiting for the job to finish

    # end of wait_for_job_to_finish


# end of AIClient

import os
import sys
import json
import getpass
import requests
import datetime
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Optional
from keycloak import (
    KeycloakOpenID,
    KeycloakConnectionError,
    KeycloakAuthenticationError,
)


class ServiceClient(ABC):
    def __init__(self, debug):
        properties_filename = os.environ.get("PYCLI_PROPERTIES")
        if not properties_filename:
            properties_filename = "properties.json"

        try:
            self.debug = debug
            self.access_token = None
            self.refresh_token = None
            self.token_expires = None
            self.refresh_token_expires = None
            f = open(properties_filename)
            self.properties = json.load(f)
            f.close()
            return
        except FileNotFoundError:
            ServiceClient.print_error(
                "PyCli properties not found at " + properties_filename + "."
            )
            exit(2)
        except JSONDecodeError as f:
            ServiceClient.print_error(
                "Invalid PyCli properties file format in file "
                + properties_filename
                + ". Message: "
                + f.msg
            )
            exit(2)

    @abstractmethod
    def create(
        self,
        identifier: str,
        metadata: str,
        content: Optional[str],
        path: Optional[str],
        auth: bool = False,
    ):
        pass

    @abstractmethod
    def update(
        self,
        resource_id: str,
        metadata: Optional[str],
        content: Optional[str],
        path: Optional[str],
        auth: bool = False,
    ):
        pass

    @abstractmethod
    def patch(
        self,
        resource_id: str,
        metadata: Optional[str],
        path: Optional[str],
        auth: bool = False,
    ):
        pass

    @abstractmethod
    def get(
        self,
        resource_id: Optional[str],
        path: str,
        query_params: Optional[dict],
        auth: bool = False,
    ) -> list:
        pass

    @abstractmethod
    def delete(
        self,
        resource_id: Optional[str],
        path: Optional[str],
        soft: bool = True,
        auth: bool = False,
    ):
        pass

    @abstractmethod
    def download(
        self,
        resource_id: str,
        path: Optional[str],
        version: Optional[int],
        auth: bool = False,
    ):
        pass

    @abstractmethod
    def render_response(self, content: list, render_as: str):
        pass

    def login(self, do_auth, headers) -> bool:
        if not do_auth:
            # skip login
            self.print_debug("Skipping KeyCloak login.")
            return True

        keycloak_openid = KeycloakOpenID(
            server_url=self.properties["keycloak"]["server_url"],
            client_id=self.properties["keycloak"]["client_id"],
            realm_name=self.properties["keycloak"]["realm_name"],
        )
        try:
            # first check for possibility to refresh
            self.print_debug("Starting KeyCloak login.")
            in_thirty_seconds = datetime.datetime.now() + datetime.timedelta(seconds=30)
            if (
                self.token_expires
                and in_thirty_seconds > self.token_expires
                and self.refresh_token
                and self.refresh_token_expires
                and datetime.datetime.now() < self.refresh_token_expires
            ):
                # token lifetime smaller 30 seconds, refresh token available and still usable -> do refresh
                self.print_debug("Refreshing existing JSON Web Token via KeyCloak.")
                token = keycloak_openid.refresh_token(self.refresh_token, "password")
            else:
                # no refresh possible, either due to initial receive or refresh token expired
                self.print_debug(
                    "No refresh token found. Performing initial login to KeyCloak."
                )
                username = self.properties["keycloak"]["username"]
                if not username:
                    username = input("Username: ")
                password = self.properties["keycloak"]["password"]
                if not password:
                    password = getpass.getpass("Password: ")
                self.print_debug("Performing KeyCloak login.")
                token = keycloak_openid.token(username, password, "password")
            if "access_token" in token:
                self.print_debug("Extracting access token from response.")
                self.access_token = token["access_token"]
                # obtain expiration times for tokens
                self.print_debug("Extracting token expiration times from response.")
                self.token_expires = datetime.datetime.now() + datetime.timedelta(
                    seconds=token["expires_in"]
                )
                self.refresh_token_expires = (
                    datetime.datetime.now()
                    + datetime.timedelta(seconds=token["refresh_expires_in"])
                )
                if "refresh_token" in token:
                    # obtain refresh token for renewal
                    self.print_debug("Extracting refresh token from response.")
                    self.refresh_token = token["refresh_token"]

                self.print_debug("Adding access token to request header.")
                headers["Authorization"] = "Bearer " + self.access_token
                if self.debug:
                    self.print_debug("Obtaining user information from KeyCloak.")
                    userinfo = keycloak_openid.userinfo(token["access_token"])
                    self.print_debug(
                        "Successfully logged in as username: "
                        + userinfo["preferred_username"]
                        + ", email: "
                        + userinfo["email"]
                        + ", groups "
                        + str(userinfo["groups"])
                        + "."
                    )
                return True
            else:
                self.print_error("No access_token found in KeyCloak response.")
        except KeycloakConnectionError as e:
            self.print_error(
                "Failed to connect to KeyCloak instance. Message: "
                + str(e.error_message)
            )
        except KeycloakAuthenticationError as f:
            self.print_error(
                "Failed to authenticate at KeyCloak instance. Message: "
                + str(f.error_message)
            )

        # if we did not return, yet, login has failed
        return False

    @classmethod
    def check_file_exists(cls, file_path: str) -> bool:
        return os.path.exists(file_path)

    def print_debug(self, message: str):
        if self.debug:
            print(message)

    @classmethod
    def print_error(cls, message: str):
        print(message, file=sys.stderr)

    def do_get(self, base_url: str, path: str, headers):
        url = base_url + path
        self.print_debug("Performing GET " + url)
        try:
            response = requests.request("GET", url, headers=headers)

            if response.status_code == 200:
                # render result
                self.print_debug("Successfully received HTTP 200. Returning response.")
                return response.content
            else:
                self.print_error(
                    "Server returned status "
                    + str(response.status_code)
                    + ". Body: "
                    + str(response.content)
                )
                exit(2)
        except requests.exceptions.RequestException as e:
            self.print_error("Failed to connect to " + base_url + ".")
            raise SystemExit(e)

    def do_get_etag(self, base_url: str, path: str, headers) -> str:
        url = base_url + path
        self.print_debug("Performing GET " + url)
        try:
            response = requests.request("GET", url, headers=headers)

            if response.status_code == 200:
                # render result
                self.print_debug("Successfully received HTTP 200. Extracting ETag.")
                return response.headers.get("etag")
            else:
                self.print_error(
                    "Server returned status "
                    + str(response.status_code)
                    + ". Body: "
                    + str(response.content)
                )
                exit(2)
        except requests.exceptions.RequestException as e:
            self.print_error("Failed to connect to " + base_url + ".")
            raise SystemExit(e)

    def do_post(self, base_url: str, path: str, headers, payload):
        url = base_url + path
        self.print_debug("Performing POST " + url)
        try:
            if isinstance(payload, str):
                self.print_debug("Posting payload in body.")
                response = requests.request("POST", url, headers=headers, data=payload)
            else:
                self.print_debug("Posting payload as files.")
                response = requests.request("POST", url, headers=headers, files=payload)

            if response.status_code == 201:
                # render result
                self.print_debug("Successfully received HTTP 201. Returning response.")
                return response.content
            else:
                self.print_error(
                    "Server returned status "
                    + str(response.status_code)
                    + ". Body: "
                    + str(response.content)
                )
                exit(2)
        except requests.exceptions.RequestException as e:
            self.print_error("Failed to connect to " + base_url + ".")
            raise SystemExit(e)

    def do_put(self, base_url: str, path: str, headers, payload):
        url = base_url + path
        self.print_debug("Performing PUT " + url)
        try:
            if isinstance(payload, str):
                self.print_debug("Putting payload in body.")
                response = requests.request("PUT", url, headers=headers, data=payload)
            else:
                self.print_debug("Putting payload as files.")
                response = requests.request("PUT", url, headers=headers, files=payload)

            if response.status_code == 200:
                # render result
                self.print_debug("Successfully received HTTP 200. Returning response.")
                return response.content
            else:
                self.print_error(
                    "Server returned status "
                    + str(response.status_code)
                    + ". Body: "
                    + str(response.content)
                )
                exit(2)
        except requests.exceptions.RequestException as e:
            self.print_error("Failed to connect to " + base_url + ".")
            raise SystemExit(e)

    def do_delete(self, base_url: str, path: str, headers):
        url = base_url + path
        self.print_debug("Performing DELETE " + url)
        try:
            response = requests.request("DELETE", url, headers=headers)

            if response.status_code == 204:
                # render result
                self.print_debug("Successfully received HTTP 204. Returning True.")
                return True
            else:
                self.print_error(
                    "Server returned status "
                    + str(response.status_code)
                    + ". Body: "
                    + str(response.content)
                )
                exit(2)
        except requests.exceptions.RequestException as e:
            self.print_error("Failed to connect to " + base_url + ".")
            raise SystemExit(e)

    def do_patch(self, base_url: str, path: str, headers, payload: str):
        url = base_url + path
        self.print_debug("Performing PATCH " + url)
        try:
            response = requests.request("PATCH", url, headers=headers, data=payload)

            if response.status_code == 204:
                # render result
                self.print_debug("Successfully received HTTP 204. Returning True.")
                return True
            else:
                self.print_error(
                    "Server returned status "
                    + str(response.status_code)
                    + ". Body: "
                    + str(response.content)
                )
                exit(2)
        except requests.exceptions.RequestException as e:
            self.print_error("Failed to connect to " + base_url + ".")
            raise SystemExit(e)

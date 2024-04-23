import json
from typing import Optional
from kitdm_pycli.helpers.service_helper import ServiceClient
from kitdm_pycli.helpers.render_utils import render_as_table, render_as_list
from kitdm_pycli.helpers.file_utils import check_json_file
from kitdm_pycli.helpers.url_utils import add_query_parameters


def id_for_element(elem):
    return elem["pid"]


class TypedPidMakerClient(ServiceClient):
    """
    Client implementation for accessing a Typed PID Maker service instance.
    """

    def __init__(self, debug=False):
        ServiceClient.__init__(self, debug)
        self.server_url = self.properties["type_pid_maker"]["server_url"]
        self.tableItemsRecord = self.properties["type_pid_maker"]["tableItemsRecord"]
        self.tableItemsPid = self.properties["type_pid_maker"]["tableItemsPid"]

    def create(
        self,
        identifier: str,
        metadata: str,
        payload: Optional[str],
        path: Optional[str],
        auth: bool = False,
    ):
        """
        Create operation for Typed PID Maker records.

        :param identifier: (Not required)
        :param metadata: The PID record as JSON document.
        :param payload: (Not required)
        :param path: Used to switch between dryrun (value = dry) and real creation (value = anything else).
        :param auth: True|False Either perform or skip authorization.
        :return: A single PID Record in a list.
        """

        headers = {"Content-Type": "application/json"}
        # Check which metadata format.
        # If it contains "entries", use default content type
        # If it contains "record", use simple content type
        metadata_content = check_json_file(metadata, ["entries"])
        if not metadata_content:
            # not default format, check for simple format
            metadata_content = check_json_file(metadata, ["record"])
            if not metadata_content:
                # no supported format
                ServiceClient.print_error("Provided metadata seems to be invalid.")
                return
            else:
                headers = {
                    "Content-Type": "application/vnd.datamanager.pid.simple+json"
                }

        endpoint = "api/v1/pit/pid/"
        if path == "dry":
            endpoint += "?dryrun=true"

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        # create pid record
        resource_response = self.do_post(
            self.server_url, endpoint, headers, metadata_content
        )
        resource_response_json = json.loads(resource_response)

        # ensure a list to be returned
        if isinstance(resource_response_json, dict):
            resource_response_json = [resource_response_json]

        return resource_response_json

    def update(
        self,
        identifier: str,
        metadata: Optional[str],
        content: Optional[str],
        path: Optional[str],
        auth: bool = False,
    ):
        """
        Update a PID record replacing its contents by the provided metadata in the file provided by the metadata
        argument.

        :param identifier: The PID pointing to the record to update.
        :param metadata: The PID record as JSON document.
        :param content: The content (ignored).
        :param path: The resource path (ignored).
        :param auth: True|False Either perform or skip authorization.
        :return: A single PID Record in a list.
        """
        headers = {"Content-Type": "application/json"}
        # Check which metadata format.
        # If it contains "entries", use default content type
        # If it contains "record", use simple content type
        metadata_content = check_json_file(metadata, ["entries"])
        if not metadata_content:
            # not default format, check for simple format
            metadata_content = check_json_file(metadata, ["record"])
            if not metadata_content:
                # no supported format
                ServiceClient.print_error("Provided metadata seems to be invalid.")
                return
            else:
                headers = {
                    "Content-Type": "application/vnd.datamanager.pid.simple+json"
                }

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        # obtain etag from resource
        etag = self.do_get_etag(
            self.server_url, "api/v1/pit/pid/" + identifier, headers
        )
        headers["If-Match"] = etag
        # do put with metadata_content
        resource_response = self.do_put(
            self.server_url, "api/v1/pit/pid/" + identifier, headers, metadata_content
        )

        resource_response_json = json.loads(resource_response)

        # ensure a list to be returned
        if isinstance(resource_response_json, dict):
            resource_response_json = [resource_response_json]

        return resource_response_json

    def get(
        self,
        identifier: Optional[str],
        path: Optional[str],
        query_params: Optional[dict],
        auth: bool = False,
    ) -> list:
        """
        Get PIDs or PID records. Depending on the parameters, either a single PID including its create/modification
        information is returned, or a PID record.

        :param identifier: The PID pointing to the record to obtain.
        :param path: Used to switch between obtaining PID record (value = pid) or check for known PIDs (value = known),
        where only the PID and create/modification information are returned.
        :param query_params: All query parameters in a dictionary.
        :param auth: True|False Either perform or skip authorization.
        :return: PID Record or PID basic information elements in a list.
        """

        headers = {"Accept": "application/json"}

        resource_path = "api/v1/pit/"
        if path == "pid":
            resource_path += path + "/" + identifier
        elif path == "known":
            resource_path += "known-pid"
            if identifier:
                resource_path += "/" + identifier

        resource_path = add_query_parameters(resource_path, query_params)

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return None

        resource_response = self.do_get(self.server_url, resource_path, headers)
        response_json = json.loads(resource_response)

        # ensure a list to be returned
        if isinstance(response_json, dict):
            response_json = [response_json]

        return response_json

    def patch(
        self,
        resource_id: str,
        metadata: Optional[str],
        path: Optional[str],
        auth: bool = False,
    ):
        print("Not supported")

    def delete(
        self,
        resource_id: Optional[str],
        path: Optional[str],
        soft: bool = True,
        auth: bool = False,
    ):
        print("Not supported")

    def download(
        self,
        resource_id: str,
        path: Optional[str],
        version: Optional[int],
        auth: bool = False,
    ):
        print("Not supported")

    def render_response(self, content, render_as):
        """
        Render the response of a certain operation. This function must only be used with structured information, i.e.,
        a JSON list in its Python representation. Depending on the render_as parameter, the result is rendered either
        as table, list, or returned in its raw form.

        :param content: The content to render.
        :param render_as: Can be either TABLE, LIST, or RAW.
        :return: The rendered or raw output.
        """
        # check render type
        if render_as == "TABLE":
            if content and len(content) > 0:
                return render_as_table(content, self.table_items_for_element)
        elif render_as == "LIST":
            return render_as_list(content, id_for_element)
        elif render_as == "RAW":
            return content

    def table_items_for_element(self, elem):
        if "created" not in elem:
            return self.tableItemsRecord
        else:
            return self.tableItemsPid

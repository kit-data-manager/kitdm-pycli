import json
from typing import Optional
from kitdm_pycli.helpers.service_helper import ServiceClient
from kitdm_pycli.helpers.render_utils import render_as_table, render_as_list
from kitdm_pycli.helpers.file_utils import check_json_file
from kitdm_pycli.helpers.url_utils import get_query_param_entry, add_query_parameters


def id_for_element(elem):
    if 'label' not in elem:
        return elem['id']
    else:
        return elem['schemaId']


class MetaStoreClient(ServiceClient):
    """
    Client implementation for accessing a MetaStore service instance.
    """

    def __init__(self, debug=False):
        ServiceClient.__init__(self, debug)
        self.server_url = self.properties['metastore']['server_url']
        self.tableItemsSchema = self.properties['metastore']['tableItemsSchema']
        self.tableItemsDocument = self.properties['metastore']['tableItemsDocument']

    def create(self, metadata: str, payload: Optional[str], path: Optional[str], auth: bool = False):
        """
        Create operation for schemas and documents. Depending on the arguments, either a
        schema or document is created. What is created is determined by the content of metadata.

        :param metadata: The metadata for the created element, i.e., schema or metadata record.
        :param payload: The payload, i.e., a local file path, which either contains a metadata schema or document.
        :param path: The path identifier that allows to switch between accessing schemas and documents, i.e., 'schema'
        or 'document'.
        :param auth: True|False Either perform or skip authorization.
        :return: A single data resource or content information metadata element in a list.
        """

        if path == "schema":
            endpoint = "schemas"
            # read metadata for validation
            check_json_file(metadata, ["type", "schemaId"])
            files = [
                ('schema', ('schema.json', open(payload, 'rb'), 'application/json')),
                ('record', ('schema_record.json', open(metadata, 'rb'), 'application/json'))
            ]
        elif path == "document":
            endpoint = "metadata"
            # read metadata for validation
            check_json_file(metadata, ["relatedResource", "schema"])
            files = [
                ('document', ('document.json', open(payload, 'rb'), 'application/json')),
                ('record', ('metadata_record.json', open(metadata, 'rb'), 'application/json'))
            ]
        else:
            # bad path
            self.print_error("Bad resource type " + path + " provided. Only 'schema' or 'document' are supported.")
            return

        # start with creating data resource
        headers = {}

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        # create schema or document
        resource_response = self.do_post(self.server_url, "api/v1/" + endpoint, headers, files)
        resource_response_json = json.loads(resource_response)

        # ensure a list to be returned
        if type(resource_response_json) == dict:
            resource_response_json = [resource_response_json]

        return resource_response_json

    def update(self, identifier: str, metadata: str, payload: Optional[str], path: Optional[str], auth: bool = False):
        """
        Update a metadata schema or document. The content of metadata must have been obtained from the server before
        as only in that case it will contain all references to existing elements. Providing a metadata document only
        containing manually created entries may lead to removing parts of the metadata which where not meant to be
        removed.

        :param identifier: The identifier of the schema/metadata record.
        :param metadata: The new metadata record.
        :param payload: The new metadata schema/document.
        :param path: The path identifier that allows to switch between accessing schemas and documents, i.e., 'schema'
        or 'document'.
        :param auth: True|False Either perform or skip authorization.
        :return: A single schema/document metadata element in a list.
        """

        headers = {}
        if path == "schema":
            endpoint = "schemas"
            headers['Accept'] = "application/vnd.datamanager.schema-record+json";
            files = []
            # add record metadata if provided
            if metadata:
                # read metadata for validation
                check_json_file(metadata, ["type", "schemaId"])
                files.append(('record', ('schema_record.json', open(metadata, 'rb'), 'application/json')))
            # add schema document if provided
            if payload:
                files.append(('schema', ('schema.json', open(payload, 'rb'), 'application/json')))
        elif path == "document":
            endpoint = "metadata"
            headers['Accept'] = "application/vnd.datamanager.metadata-record+json";
            files = []
            # add record metadata if provided
            if metadata:
                # read metadata for validation
                check_json_file(metadata, ["relatedResource", "schema"])
                files.append(('record', ('metadata_record.json', open(metadata, 'rb'), 'application/json')))
            # add metadata document if provided
            if payload:
                files.append(('document', ('document.json', open(payload, 'rb'), 'application/json')))
        else:
            # bad path
            self.print_error("Bad resource type " + path + " provided. Only 'schema' or 'document' are supported.")
            return

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        # obtain etag and add to header
        etag = self.do_get_etag(self.server_url, "api/v1/" + endpoint + "/" + identifier, headers)
        headers['If-Match'] = etag
        # Remove accept header for PUT operation
        headers['Accept'] = None
        # create schema or document
        resource_response = self.do_put(self.server_url, "api/v1/" + endpoint + "/" + identifier, headers, files)
        resource_response_json = json.loads(resource_response)

        # ensure a list to be returned
        if type(resource_response_json) == dict:
            resource_response_json = [resource_response_json]

        return resource_response_json

    def get(self, resource_id: Optional[str], path: Optional[str], query_params: Optional[dict], auth: bool = False) -> list:

        """
        Get schema or document metadata. Depending on the parameters, either a single element
        is obtained or an (optionally) filtered list will be returned. See the argument descriptions for more details.

        :param resource_id: The schema or document identifier, which is mandatory for obtaining a single resource.
        only used if a single resource is obtained, i.e., only if resource_id is provided.
        :param path: The path identifier that allows to switch between accessing schemas and documents, i.e., 'schema'
        or 'document'.
        :param query_params: Query parameters in a dictionary.
        :param auth: True|False Either perform or skip authorization.
        :return: Data resource or content information elements in a list.
        """
        headers = {}
        if path == "schema":
            endpoint = "schemas"
            headers['Accept'] = 'application/vnd.datamanager.schema-record+json'
        elif path == "document":
            endpoint = "metadata"
            headers['Accept'] = 'application/vnd.datamanager.metadata-record+json'
        else:
            # bad path
            self.print_error("Bad resource type " + path + " provided. Only 'schema' or 'document' are supported.")
            return

        resource_path = "api/v1/" + endpoint

        if resource_id:
            resource_path += "/" + resource_id

        resource_path = add_query_parameters(resource_path, query_params)

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        resource_response = self.do_get(self.server_url, resource_path, headers)
        response_json = json.loads(resource_response)

        # ensure a list to be returned
        if type(response_json) == dict:
            response_json = [response_json]

        return response_json

    def delete(self, identifier: str, path: Optional[str], soft: bool = True, auth: bool = False):
        """
        Delete a schema or document from the server. By default, both are revoked at the
        first call (which can be reverted) and will be removed if one deletes a revoked schema or document.
        If the parameter soft is set to False, also schemas/documents are removed in a single call!

        :param identifier: The identifier of the schema/document.
        :param path: The path identifier that allows to switch between accessing schemas and documents, i.e., 'schema'
        or 'document'.
        :param soft: If True, data resources are revoked first, before they are removed during a second delete
        operation.
        :param auth: True|False Either perform or skip authorization.
        :return: True or False, depending on the result of the delete operation.
        """

        headers = {"Accept": "application/json"}
        if path == "schema":
            endpoint = "schemas"
            headers["Accept"] = "application/vnd.datamanager.schema-record+json"
        elif path == "document":
            endpoint = "metadata"
            headers["Accept"] = "application/vnd.datamanager.metadata-record+json"
        else:
            # bad path
            self.print_error("Bad resource type " + path + " provided. Only 'schema' or 'document' are supported.")
            return

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        etag = self.do_get_etag(self.server_url, "api/v1/" + endpoint + "/" + identifier, headers)
        headers['If-Match'] = etag
        # remove accept header for deletion
        headers['Accept'] = None
        result = self.do_delete(self.server_url, "api/v1/" + endpoint + "/" + identifier, headers)
        if result and not soft:
            # repeat recursively but set 'soft' True to stop recursion after one iteration
            result = self.delete(identifier, path, True, auth)

        return result

    def download(self, resource_id: str, path: str, version: Optional[int], auth: bool = False):
        """
        Download the schema or document, optionally in a specific version. Which kind of resource is downloaded is
        determined by the path argument, which can be either 'schema' or 'document'.

        :param resource_id: The identifier of the schema or document.
        :param path: The path identifier that allows to switch between accessing schemas and documents, i.e., 'schemas'
         or 'metadata'.
        :param version: The version of schema or document if versioning is enabled on the
        server.
        :param auth: True|False Either perform or skip authorization.
        :return: The downloaded bitstream, which can be further processed or stored in a local file.
        """
        headers = {}
        resource_path = "api/v1/"
        if path == "schema":
            resource_path += "schemas/" + resource_id
        elif path == "document":
            resource_path += "metadata/" + resource_id
        else:
            # bad path
            self.print_error("Bad resource type " + path + " provided. Only 'schema' or 'document' are supported.")
            return

        if version:
            # only append version if a single file is downloaded
            resource_path += "?version=" + str(version)

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        return self.do_get(self.server_url, resource_path, headers)

    def patch(self, resource_id: str, payload: Optional[str], path: Optional[str], auth: bool = False):
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
            return render_as_table(content, self.table_items_for_element)
        elif render_as == "LIST":
            return render_as_list(content, id_for_element)
        elif render_as == "RAW":
            return content

    def table_items_for_element(self, elem):
        if 'label' not in elem:
            return self.tableItemsDocument
        else:
            return self.tableItemsSchema

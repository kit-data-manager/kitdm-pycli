import json
import ntpath
from kitdm_pycli.helpers.service_helper import ServiceClient
from typing import Optional
from kitdm_pycli.helpers.render_utils import render_as_table, render_as_list
from kitdm_pycli.helpers.file_utils import check_json_file, check_file_exists
from kitdm_pycli.helpers.url_utils import get_query_param_entry, add_query_parameters


def id_for_element(elem):
    if 'parentResource' not in elem:
        return elem['id']
    else:
        return elem['parentResource']['id'] + '/data/' + elem['relativePath']


class BaseRepoClient(ServiceClient):
    """
    Client implementation for accessing a base-repo service instance.
    """

    def __init__(self, debug=False):
        ServiceClient.__init__(self, debug)
        self.server_url = self.properties['base_repo']['server_url']
        self.tableItemsResource = self.properties['base_repo']['tableItemsResource']
        self.tableItemsContent = self.properties['base_repo']['tableItemsContent']

    def create(self, identifier: str, metadata: str, payload: Optional[str], path: Optional[str], auth: bool = False):
        """
        Create operation for base-repo resources and content information. Depending on the arguments, either a
        resource of a content element is created. If an identifier is provided, metadata is expected to refer to
        data resource metadata and a data resource will be created. If an identifier is provided, metadata is
        expected to optionally refer to content information metadata, whereas path optionally refers to a local
        file which will be uploaded (if not references in metadata), and a new content element is created for an
        existing data resource.

        :param identifier: The identifier of an existing resource. Required for content upload.
        :param metadata: The metadata for the created element, i.e., data resource or content information metadata.
        :param payload: The payload, i.e., a local file path, which will be uploaded during content creation.
        :param path: The relative path where the file will be remotely accessible, e.g., file.txt or folder/file.txt.
        :param auth: True|False Either perform or skip authorization.
        :return: A single data resource or content information metadata element in a list.
        """
        metadata_content = None
        if not identifier:
            # create data resource
            metadata_content = check_json_file(metadata, ["resourceType"])
            if not metadata_content:
                # data resource metadata not found or not in proper format
                ServiceClient.print_error("Provided metadata seems to be invalid.")
                return
        else:
            # identifier available, content creation envisioned -> check content argument
            if payload and not check_file_exists(payload):
                # content argument provided, but file not found
                ServiceClient.print_error("Content path seems to be invalid.")
                return

        # start with creating data resource
        headers = {"Content-Type": "application/json"}

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        if not identifier:
            # create resource if no identifier is provided
            resource_response = self.do_post(self.server_url, "api/v1/dataresources/", headers, metadata_content)
            resource_response_json = json.loads(resource_response)
        else:
            # Create new content
            resource_id = identifier
            # upload content
            headers['Content-Type'] = None
            content_path = "api/v1/dataresources/" + resource_id + "/data/"
            if path:
                content_path += path.lstrip('/')
            else:
                path = ""
            if path.endswith("/"):
                # file part still missing, add content filename
                if payload:
                    content_path += ntpath.basename(payload)
                else:
                    self.print_error("If no content is provided, relative path must not end with slash.")
                    return

            files = None
            if metadata and payload:
                # content information and file provided
                files = {
                    "metadata": open(metadata, 'rb'),
                    "file": open(payload, 'rb')
                }
            elif not metadata and payload:
                # only file provided
                files = {
                    "file": open(payload, 'rb')
                }
            elif metadata and not payload:
                # only content information provided (file references inside)
                files = {
                    "metadata": open(metadata, 'rb')
                }

            # do create new content
            self.do_post(self.server_url, content_path, headers, files)
            # as post does not return the result, we do an additional GET now to obtain the content information
            headers['Accept'] = "application/vnd.datamanager.content-information+json"
            resource_response = self.do_get(self.server_url, content_path, headers);
            resource_response_json = json.loads(resource_response)

        # ensure a list to be returned
        if type(resource_response_json) == dict:
            resource_response_json = [resource_response_json]

        return resource_response_json

    def update(self, identifier: str, metadata: Optional[str], auth: bool = False):
        """
        Update a data resource replacing its metadata by the provided metadata in the file provided by the metadata
        argument. The content of metadata must have been obtained from the server before as only in that case
        it will contain all references to existing elements. Providing a metadata document only containing manually
        created entries may lead to removing parts of the data resource which where not meant to be removed.

        :param identifier: The identifier of the data resource.
        :param metadata: The new data resource metadata document.
        :param auth: True|False Either perform or skip authorization.
        :return: A single data resource element in a list.
        """
        # read provided data resource metadata
        metadata_content = check_json_file(metadata, ["resourceType"])

        if not metadata_content:
            # data resource metadata not found or not in proper format
            ServiceClient.print_error("Provided metadata seems to be invalid.")
            return

        headers = {"Content-Type": "application/json"}

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        # obtain etag from resource
        etag = self.do_get_etag(self.server_url, "api/v1/dataresources/" + identifier, headers)
        headers['If-Match'] = etag
        # do put with metadata_content
        resource_response = self.do_put(self.server_url, "api/v1/dataresources/" + identifier, headers,
                                        metadata_content)

        resource_response_json = json.loads(resource_response)

        # ensure a list to be returned
        if type(resource_response_json) == dict:
            resource_response_json = [resource_response_json]

        return resource_response_json

    def patch(self, identifier: str, payload: str, path: Optional[str], auth: bool = False):
        """
        Path data resource or content information element. Compared to a full update, a patch operation only
        changes parts of the resource. Patching instructions must be provided in the standardized format specified in
        RFC 6902 (see https://jsonpatch.com/).

        :param identifier: The identifier of the data resource.
        :param payload: The patch instructions.
        :param path: The relative path of the content information element to patch, e.g., file.txt or folder/file.txt.
        :param auth: True|False Either perform or skip authorization.
        :return: A single data resource or content information element in a list.
        """
        metadata_patch = check_json_file(payload)

        headers = {"Content-Type": "application/json-patch+json"}

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        if not path:
            # no path, patch data resource
            # obtain etag from resource
            resource_path = "api/v1/dataresources/" + identifier
            headers["Accept"] = "application/json"
            etag = self.do_get_etag(self.server_url, resource_path, headers)

            headers['If-Match'] = etag
            # do patch with metadata_patch
            if self.do_patch(self.server_url, resource_path, headers, metadata_patch):
                # obtain patched resource
                resource_response = self.do_get(self.server_url, resource_path, headers)
                response_json = json.loads(resource_response)
        else:
            # with path, patch content information
            # obtain etag for content information
            resource_path = "api/v1/dataresources/" + identifier + "/data/" + path.lstrip("/");
            headers["Accept"] = "application/vnd.datamanager.content-information+json"
            etag = self.do_get_etag(self.server_url, resource_path, headers)
            headers['If-Match'] = etag
            # do patch with metadata_patch
            if self.do_patch(self.server_url, resource_path, headers, metadata_patch):
                # obtain patched resource
                resource_response = self.do_get(self.server_url, resource_path, headers)
                response_json = json.loads(resource_response)

        # ensure a list to be returned
        if type(response_json) == dict:
            response_json = [response_json]
        return response_json

    def get(self, resource_id: Optional[str], path: Optional[str], query_params: Optional[dict], auth: bool = False) -> list:
        """
        Get data resource or content information elements. Depending on the parameters, either a single element
        is obtained or an (optionally) filtered list will be returned. See the argument descriptions for more details.

        :param resource_id: The data resource identifier, which is mandatory for obtaining a single resource or for
        obtaining content information for a parent resource.
        :param path: The relative path of the content information element to obtain, e.g., file.txt, folder/ or
        folder/file.txt.
        :param query_params: All query parameters in a dictionary.
        :param auth: True|False Either perform or skip authorization.
        :return: Data resource or content information elements in a list.
        """

        headers = {"Accept": "application/json"}

        resource_path = "api/v1/dataresources/"
        if resource_id:
            # append resource id to base path
            resource_path += resource_id
            if path:
                # append data sub-path and set proper content type
                headers['Accept'] = 'application/vnd.datamanager.content-information+json'
                resource_path += "/data/" + path.lstrip("/")

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

    def download(self, resource_id: str, path: str, version: Optional[int], auth: bool = False):
        """
        Download the file referred by a specific content information element, optionally in a specific version.

        :param resource_id: The identifier of the parent data resource.
        :param path: The path of the content to downloads, e.g., file.txt, folder/, or folder/file.txt. If providing a
        folder, all contained files are downloaded as ZIP file.
        :param version: The file version used to obtain a specific version of a file if versioning is enabled on the
        server. The version argument is only used while accessing single content information elements and will be
        ignored when accessing a relative path.
        :param auth: True|False Either perform or skip authorization.
        :return: The downloaded bitstream, which can be further processed or stored in a local file.
        """
        headers = {}
        if path.endswith("/"):
            # to download folders, the proper accept header must be provided
            headers['Accept'] = 'application/zip'

        # authentication not required or done, now do the real stuff
        resource_path = "api/v1/dataresources/" + resource_id + "/data/" + path.lstrip("/")

        if version and not resource_path.endswith("/"):
            # only append version if a single file is downloaded
            resource_path += "?version=" + str(version)

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        return self.do_get(self.server_url, resource_path, headers)

    def delete(self, identifier: str, path: Optional[str], soft: bool = True, auth: bool = False):
        """
        Delete data resource or content information elements from the server. For content information elements, this
        happens immediately but has to be for each element separately. Data resources are by default revoked at the
        first call (which can be reverted) and will be removed if one deletes a revoked data resource.
        If the parameter soft is set to False, also data resources are removed in a single call!

        :param identifier: The identifier of the data resource.
        :param path: The path of the content information element to remove, e.g., file.txt or folder/file.txt. It is
        not possible to remove entire folders, e.g., by providing folder/.
        :param soft: If True, data resources are revoked first, before they are removed during a second delete
        operation.
        :param auth: True|False Either perform or skip authorization.
        :return: True or False, depending on the result of the delete operation.
        """

        headers = {"Accept": "application/json"}

        # authenticate if required, stop if login fails
        if not self.login(auth, headers):
            return

        if not path:
            # obtain etag for resource
            etag = self.do_get_etag(self.server_url, "api/v1/dataresources/" + identifier, headers)
            headers['If-Match'] = etag
            # perform delete operation
            result = self.do_delete(self.server_url, "api/v1/dataresources/" + identifier, headers)
            # if delete operation successful and hard delete enter here
            if result and not soft:
                # repeat recursively but set 'soft' True to stop recursion after one iteration
                result = self.delete(identifier, path, True, auth)
        else:
            # obtain etag for content
            headers["Accept"] = "application/vnd.datamanager.content-information+json"
            etag = self.do_get_etag(self.server_url, "api/v1/dataresources/" + identifier + "/data/" + path.lstrip("/"),
                                    headers)
            headers['If-Match'] = etag
            # perform delete operation
            result = self.do_delete(self.server_url, "api/v1/dataresources/" + identifier + "/data/" + path.lstrip("/"),
                                    headers)

        return result

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
        if 'parentResource' not in elem:
            return self.tableItemsResource
        else:
            return self.tableItemsContent

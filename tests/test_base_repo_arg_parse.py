from kitdm_pycli.clients.base_repo_client import parse_arguments


def test_create_resource():
    # createResource [-m data_resource.json]
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "createResource", "-m", "metadata.json"]
    result = parse_arguments(args)
    assert result.operation == "createResource"
    assert result.metadata == "metadata.json"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_create_content():
    # createContent -id 123 [-m content_information.json] [-pl file.txt] [-rp folder/file.txt]
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "createContent", "-id", "123", "-m", "metadata.json",
            "-pl", "data.txt", "-rp", "files/datafile.txt"]
    result = parse_arguments(args)
    assert result.operation == "createContent"
    assert result.metadata == "metadata.json"
    assert result.payload == "data.txt"
    assert result.relativePath == "files/datafile.txt"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_get_resource():
    # getResource -id 123 456 [-v 2]
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "getResource", "-id", "123", "456", "-v", "1"]
    result = parse_arguments(args)
    assert result.operation == "getResource"
    assert len(result.identifier) == 2
    assert result.identifier[0] == "123"
    assert result.identifier[1] == "456"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_get_resources():
    # getResources [-f 'yesterday'] [-u 'now'] [-p 1] [-s 30]
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "getResources", "-f", "yesterday", "-u", "now",
            "-p", "1", "-s", "30"]
    result = parse_arguments(args)
    assert result.operation == "getResources"
    assert result.fromDate == "yesterday"
    assert result.untilDate == "now"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.page == 1
    assert result.pageSize == 30
    assert result.render_as == "LIST"


def test_get_content():
    # getContent -id 123 [-rp folder/] [-v 2] [-t thumb]
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "getContent", "-id", "123", "456", "-rp",
            "files/file.txt", "-v", "1"]
    result = parse_arguments(args)
    assert result.operation == "getContent"
    assert len(result.identifier) == 2
    assert result.identifier[0] == "123"
    assert result.identifier[1] == "456"
    assert result.relativePath == "files/file.txt"
    assert result.version == 1
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"

def test_download_content():
    # downloadContent -id 123 [-rp /] [-v 1]
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "downloadContent", "-id", "123", "-rp", "files/file.txt",
            "-v", "1"]
    result = parse_arguments(args)
    assert result.operation == "downloadContent"
    assert result.identifier == "123"
    assert result.relativePath == "files/file.txt"
    assert result.version == 1
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_update_resource():
    # updateResource -id 123 -m data_resource.json
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "updateResource", "-id", "123", "-m", "metadata.json"]
    result = parse_arguments(args)
    assert result.operation == "updateResource"
    assert result.identifier == "123"
    assert result.metadata == "metadata.json"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_patch_resource():
    # patchResource -id 123 ... -m patch.json
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "patchResource", "-id", "123", "456", "-pl", "patch.json"]
    result = parse_arguments(args)
    assert result.operation == "patchResource"
    assert len(result.identifier) == 2
    assert result.identifier[0] == "123"
    assert result.identifier[1] == "456"
    assert result.payload == "patch.json"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_delete_resource():
    # deleteResource -id 123 [-soft]
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "deleteResource", "-id", "123", "456", "--soft"]
    result = parse_arguments(args)
    assert result.operation == "deleteResource"
    assert len(result.identifier) == 2
    assert result.identifier[0] == "123"
    assert result.identifier[1] == "456"
    assert result.soft is True
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_delete_content():
    # deleteContent -id 123 -rp /folder/
    args = ["-a", "-r", "LIST", "-o", "file.json", "--debug", "deleteContent", "-id", "123", "-rp", "files/file.txt"]
    result = parse_arguments(args)
    assert result.operation == "deleteContent"
    assert result.identifier == "123"
    assert result.relativePath == "files/file.txt"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"

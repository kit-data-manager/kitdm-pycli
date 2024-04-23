from kitdm_pycli.clients.metastore_client import parse_arguments


def test_create_schema():
    # createSchema -m schema_record.json -s schema.json
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "createSchema",
        "-m",
        "metadata.json",
        "-pl",
        "schema.json",
    ]
    result = parse_arguments(args)
    assert result.operation == "createSchema"
    assert result.metadata == "metadata.json"
    assert result.payload == "schema.json"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_create_document():
    # createDocument -m metadata_record.json -pl document.json
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "createDocument",
        "-m",
        "metadata.json",
        "-pl",
        "document.json",
    ]
    result = parse_arguments(args)
    assert result.operation == "createDocument"
    assert result.metadata == "metadata.json"
    assert result.payload == "document.json"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_get_schema():
    # getSchema -id 123 456 -v 1
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "getSchema",
        "-id",
        "123",
        "456",
        "-v",
        "1",
    ]
    result = parse_arguments(args)
    assert result.operation == "getSchema"
    assert len(result.identifier) == 2
    assert result.identifier[0] == "123"
    assert result.identifier[1] == "456"
    assert result.version == 1
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_get_schemas():
    # getSchemas [-f 'yesterday'] [-u 'now'] [-p 1] [-s 30]
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "getSchemas",
        "-f",
        "yesterday",
        "-u",
        "now",
        "-p",
        "1",
        "-s",
        "30",
    ]
    result = parse_arguments(args)
    assert result.operation == "getSchemas"
    assert result.fromDate == "yesterday"
    assert result.untilDate == "now"
    assert result.page == 1
    assert result.pageSize == 30
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_get_document():
    # getDocument -i 123 [-v 1]
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "getDocument",
        "-id",
        "123",
        "456",
        "-v",
        "1",
    ]
    result = parse_arguments(args)
    assert result.operation == "getDocument"
    assert len(result.identifier) == 2
    assert result.identifier[0] == "123"
    assert result.identifier[1] == "456"
    assert result.version == 1
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_get_documents():
    # getDocuments [-f 'yesterday'] [-u 'now'] [-p 1] [-s 30]
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "getDocuments",
        "-f",
        "yesterday",
        "-u",
        "now",
        "-p",
        "1",
        "-s",
        "30",
    ]
    result = parse_arguments(args)
    assert result.operation == "getDocuments"
    assert result.fromDate == "yesterday"
    assert result.untilDate == "now"
    assert result.page == 1
    assert result.pageSize == 30
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_download_schema():
    # downloadSchema -id 123 [-v 1]
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "downloadSchema",
        "-id",
        "123",
        "-v",
        "1",
    ]
    result = parse_arguments(args)
    assert result.operation == "downloadSchema"
    assert result.identifier == "123"
    assert result.version == 1
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_download_document():
    # downloadDocument -id 123 [-v 1]
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "downloadDocument",
        "-id",
        "123",
        "-v",
        "1",
    ]
    result = parse_arguments(args)
    assert result.operation == "downloadDocument"
    assert result.identifier == "123"
    assert result.version == 1
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_update_schema():
    # updateSchema -id 123 -m schema_record.json -pl schema.json
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "updateSchema",
        "-id",
        "123",
        "-m",
        "schema_record.json",
        "-pl",
        "schema.json",
    ]
    result = parse_arguments(args)
    assert result.operation == "updateSchema"
    assert result.identifier == "123"
    assert result.metadata == "schema_record.json"
    assert result.payload == "schema.json"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_update_document():
    # updateDocument -id 123 -m schema_record.json -pl schema.json
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "updateDocument",
        "-id",
        "123",
        "-m",
        "document_record.json",
        "-pl",
        "document.json",
    ]
    result = parse_arguments(args)
    assert result.operation == "updateDocument"
    assert result.identifier == "123"
    assert result.metadata == "document_record.json"
    assert result.payload == "document.json"
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_delete_schema():
    # deleteSchema -id 123 [-soft]
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "deleteSchema",
        "-id",
        "123",
        "456",
        "--soft",
    ]
    result = parse_arguments(args)
    assert result.operation == "deleteSchema"
    assert len(result.identifier) == 2
    assert result.identifier[0] == "123"
    assert result.identifier[1] == "456"
    assert result.soft is True
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"


def test_delete_document():
    # deleteDocument -id 123 [-soft]
    args = [
        "-a",
        "-r",
        "LIST",
        "-o",
        "file.json",
        "--debug",
        "deleteDocument",
        "-id",
        "123",
        "456",
        "--soft",
    ]
    result = parse_arguments(args)
    assert result.operation == "deleteDocument"
    assert len(result.identifier) == 2
    assert result.identifier[0] == "123"
    assert result.identifier[1] == "456"
    assert result.soft is True
    assert result.debug is True
    assert result.output == "file.json"
    assert result.auth is True
    assert result.render_as == "LIST"

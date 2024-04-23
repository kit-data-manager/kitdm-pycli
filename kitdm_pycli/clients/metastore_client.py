import argparse
import sys
from kitdm_pycli.helpers.metastore_helper import MetaStoreClient
from kitdm_pycli.helpers.url_utils import get_query_param_entry
from kitdm_pycli.helpers.command_line_utils import add_global_arguments
from kitdm_pycli.helpers.command_line_utils import add_single_identifier_argument
from kitdm_pycli.helpers.command_line_utils import add_range_filter_arguments
from kitdm_pycli.helpers.command_line_utils import add_payload_argument
from kitdm_pycli.helpers.command_line_utils import parse_query_params
from kitdm_pycli.helpers.command_line_utils import add_multiple_identifier_argument
from kitdm_pycli.helpers.command_line_utils import add_version_argument
from kitdm_pycli.helpers.command_line_utils import add_pagination_arguments
from kitdm_pycli.helpers.command_line_utils import add_metadata_argument
from kitdm_pycli.helpers.render_utils import render_to_file


def parse_arguments(args):
    parser = argparse.ArgumentParser(
        description="Command line client interface for the MetaStore service."
    )

    operation_subparser = parser.add_subparsers(
        dest="operation", help="Operation selection"
    )

    # createSchema -m schema_record.json -pl schema.json
    create_schema_parser = operation_subparser.add_parser(
        "createSchema", help="Create a new metadata schema."
    )
    add_metadata_argument(create_schema_parser)
    add_payload_argument(create_schema_parser)

    # createDocument -m metadata_record.json -d metadata.json
    create_document_parser = operation_subparser.add_parser(
        "createDocument", help="Create a new metadata document."
    )
    add_metadata_argument(create_document_parser)
    add_payload_argument(create_document_parser)

    # getSchema [-id 123] [-v 2]
    get_schema_parser = operation_subparser.add_parser(
        "getSchema", help="List metadata for single or multiple " "registered schemas."
    )
    add_multiple_identifier_argument(get_schema_parser)
    add_version_argument(get_schema_parser)

    # getSchemas [-f 'two days ago'] [-u Now] [-p 1] [-s 20]
    get_schemas_parser = operation_subparser.add_parser(
        "getSchemas", help="List metadata for multiple " "registered schemas."
    )
    add_range_filter_arguments(get_schemas_parser)
    add_pagination_arguments(get_schemas_parser)

    # getDocument [-id 123] [-v 2]
    get_document_parser = operation_subparser.add_parser(
        "getDocument",
        help="List metadata for single or multiple " "registered documents by id",
    )
    add_multiple_identifier_argument(get_document_parser)
    add_version_argument(get_document_parser)

    # getDocuments [-f 'two days ago'] [-u Now] [-p 1] [-s 20]
    get_documents_parser = operation_subparser.add_parser(
        "getDocuments", help="List metadata for multiple " "registered documents."
    )
    get_documents_parser.add_argument(
        "-sid",
        "--schemaIds",
        type=str,
        nargs="+",
        help="This argument allows to provide one or more schema ids, which are "
        "used to filter the list of received metadata records.",
    )
    get_documents_parser.add_argument(
        "-rr",
        "--relatedResources",
        type=str,
        nargs="+",
        help="This argument allows to provide one or more related resources, which are "
        "used to filter the list of received metadata records.",
    )

    add_range_filter_arguments(get_documents_parser)
    add_pagination_arguments(get_documents_parser)

    # downloadSchema -id 123 [-v 2]
    download_schema_parser = operation_subparser.add_parser(
        "downloadSchema", help="Download a metadata schema."
    )
    add_single_identifier_argument(download_schema_parser)
    add_version_argument(download_schema_parser)

    # downloadDocument -id 123 [-v 2]
    download_document_parser = operation_subparser.add_parser(
        "downloadDocument", help="Download a metadata document."
    )
    add_single_identifier_argument(download_document_parser)
    add_version_argument(download_document_parser)

    # updateSchema -id 123 [-m schema_record.json] [-s schema.json]
    update_schema_parser = operation_subparser.add_parser(
        "updateSchema", help="Update a metadata schema."
    )
    add_single_identifier_argument(update_schema_parser)
    add_metadata_argument(update_schema_parser)
    add_payload_argument(update_schema_parser)

    # updateDocument -id 123 [-m metadata_record.json] [-d metadata.json]
    update_document_parser = operation_subparser.add_parser(
        "updateDocument", help="Update a metadata document."
    )
    add_single_identifier_argument(update_document_parser)
    add_metadata_argument(update_document_parser)
    add_payload_argument(update_document_parser)

    # deleteSchema -id 123 [-soft]
    delete_schema_parser = operation_subparser.add_parser(
        "deleteSchema", help="Delete one or more schemas."
    )
    add_multiple_identifier_argument(delete_schema_parser)
    delete_schema_parser.add_argument(
        "-s",
        "--soft",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="This switch allows to perform a soft-delete for schemas and is "
        "always enabled by default. This means, that a schema is only revoked "
        "and will be permanently removed if deleting it a second time.",
    )

    # deleteDocument -id 123 [-soft]
    delete_document_parser = operation_subparser.add_parser(
        "deleteDocument", help="Delete one or more documents."
    )
    add_multiple_identifier_argument(delete_document_parser)
    delete_document_parser.add_argument(
        "-s",
        "--soft",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="This switch allows to perform a soft-delete for documents and is "
        "always enabled by default. This means, that a document is only revoked "
        "and will be permanently removed if deleting it a second time.",
    )

    add_global_arguments(parser)

    return parser.parse_args(args)


def main():
    args = parse_arguments(sys.argv[1:])

    # Determine client to use
    service_client = MetaStoreClient(args.debug)

    # Determine and call operation to apply
    response = None

    if args.operation == "createSchema":
        # createSchema -m schema_record.json -pl schema.json
        response = service_client.create(
            args.metadata, args.payload, "schema", args.auth
        )
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "createDocument":
        # createDocument -m metadata_record.json -pl document.json
        response = service_client.create(
            args.metadata, args.payload, "document", args.auth
        )
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "getSchema":
        if len(args.identifier) > 1:
            # multiple ids provided
            all_results = []
            for identifier in args.identifier:
                response = service_client.get(identifier, "schema", None, args.auth)
                all_results += response
            response = all_results
        else:
            query_params = [get_query_param_entry("version", str(args.version))]
            response = service_client.get(
                args.identifier[0], "schema", query_params, args.auth
            )

        response = service_client.render_response(response, args.render_as)
    elif args.operation == "getSchemas":
        # getSchemas [-f 'yesterday'] [-u 'now'] [-p 1] [-s 30]
        query_params = parse_query_params(args)
        response = service_client.get(None, "schema", query_params, args.auth)
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "getDocument":
        # getDocument -i 123 [-v 1]
        if len(args.identifier) > 1:
            # multiple ids provided
            all_results = []

            for identifier in args.identifier:
                response = service_client.get(identifier, "document", None, args.auth)
                all_results += response
            response = all_results
        else:
            query_params = [get_query_param_entry("version", str(args.version))]
            response = service_client.get(
                args.identifier[0], "document", query_params, args.auth
            )

        response = service_client.render_response(response, args.render_as)
    elif args.operation == "getDocuments":
        # getDocuments [-f 'yesterday'] [-u 'now'] [-p 1] [-s 30]
        query_params = parse_query_params(args)

        if args.relatedResources:
            query_params.append(
                get_query_param_entry("resourceId", ",".join(args.relatedResources))
            )

        if args.schemaIds:
            query_params.append(
                get_query_param_entry("schemaId", ",".join(args.schemaIds))
            )

        response = service_client.get(None, "document", query_params, args.auth)
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "downloadSchema":
        # downloadSchema -id 123 [-v 1]
        response = service_client.download(
            args.identifier, "schema", args.version, args.auth
        )
    elif args.operation == "downloadDocument":
        # downloadDocument -id 123 [-v 1]
        response = service_client.download(
            args.identifier, "document", args.version, args.auth
        )
    elif args.operation == "updateSchema":
        # updateSchema -id 123 -m schema_record.json -pl schema.json
        response = service_client.update(
            args.identifier, args.metadata, args.payload, "schema", args.auth
        )
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "updateDocument":
        # updateDocument -id 123 -m metadata_record.json -pl metadata.json
        response = service_client.update(
            args.identifier, args.metadata, args.payload, "document", args.auth
        )
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "deleteSchema":
        # deleteSchema -id 123 [-soft]
        if len(args.identifier) > 1:
            # multiple ids provided
            all_results = []
            for identifier in args.identifier:
                response = service_client.delete(
                    identifier, "schema", args.soft, args.auth
                )
                if not response:
                    service_client.print_error(
                        "Schema " + identifier + " could not be deleted."
                    )
        else:
            response = service_client.delete(
                args.identifier[0], "schema", args.soft, args.auth
            )
            if not response:
                service_client.print_error(
                    "Schema " + args.identifier[0] + " could not be deleted."
                )
    elif args.operation == "deleteDocument":
        # deleteDocument -id 123 [-soft]
        if len(args.identifier) > 1:
            # multiple ids provided
            all_results = []
            for identifier in args.identifier:
                response = service_client.delete(
                    identifier, "document", args.soft, args.auth
                )
                if not response:
                    service_client.print_error(
                        "Document " + identifier + " could not be deleted."
                    )
        else:
            response = service_client.delete(
                args.identifier[0], "document", args.soft, args.auth
            )
            if not response:
                service_client.print_error(
                    "Document " + args.identifier[0] + " could not be deleted."
                )

    if args.output:
        # write to file
        render_to_file(response, args)
    else:
        # print response to stdout
        print(response)


if __name__ == "__main__":
    main()

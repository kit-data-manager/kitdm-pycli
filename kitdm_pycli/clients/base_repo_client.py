from kitdm_pycli.helpers.base_repo_helper import BaseRepoClient
import argparse
import dateparser
import sys
from prettytable import PrettyTable
from kitdm_pycli.helpers.url_utils import get_query_param_entry
from kitdm_pycli.helpers.command_line_utils import *
from kitdm_pycli.helpers.render_utils import *


def parse_arguments(args):
    parser = argparse.ArgumentParser(description='Command line client interface for the base-repo service.')

    operation_subparser = parser.add_subparsers(dest="operation", help='Operation selection')

    # createResource [-m data_resource.json]
    create_resource_parser = operation_subparser.add_parser('createResource', help='Create a new data resource.')
    add_metadata_argument(create_resource_parser)

    # createContent -id 123 [-m content_information.json] [-pl file.txt] [-rp folder/file.txt]
    create_content_parser = operation_subparser.add_parser('createContent', help='Create a new content element.')
    add_single_identifier_argument(create_content_parser)
    add_metadata_argument(create_content_parser)
    add_payload_argument(create_content_parser)
    create_content_parser.add_argument('-rp', '--relativePath', type=str, default="/",
                                       help='The relative path where the content is stored. If the relative path '
                                            ' ends with a slash, the local filename is appended. Otherwise, the '
                                            'provided filename will be used. If the relative path is omitted, '
                                            'the file is uploaded to the root of the resource and will keep its '
                                            'name.')

    # getResource -id 123 ... [-v 2]
    get_resource_parser = operation_subparser.add_parser('getResource', help='List metadata for one or more single '
                                                                             'resources.')
    add_multiple_identifier_argument(get_resource_parser)
    add_version_argument(get_resource_parser)

    # getResources [-f 'yesterday'] [-u 'now'] [-p 1] [-s 30]
    get_resources_parser = operation_subparser.add_parser('getResources', help='List metadata for all resources,'
                                                                               'optionally filtered by creation time.')
    add_range_filter_arguments(get_resources_parser)
    add_pagination_arguments(get_resources_parser)

    # getContent -id 123 [-rp folder/] [-v 2] [-t thumb]
    get_content_parser = operation_subparser.add_parser('getContent',
                                                        help='List metadata for one or more resource\'s '
                                                             'content elements.')
    add_multiple_identifier_argument(get_content_parser)
    get_content_parser.add_argument('-rp', '--relativePath', type=str, default="/",
                                    help='The relative path of the content. If omitted, '
                                         'the root of the resource is used and all its contents are listed.')
    add_version_argument(get_content_parser)
    # get_content_parser.add_argument('-t', '--tag', type=int,
    #                                help='The tag of contents to obtain metadata for.')
    add_pagination_arguments(get_content_parser)

    # downloadContent -id 123 [-rp /] [-v 1]
    download_content_parser = operation_subparser.add_parser('downloadContent', help='Download content from a '
                                                                                     'resource.')
    add_single_identifier_argument(download_content_parser)
    download_content_parser.add_argument('-rp', '--relativePath', type=str, default="/",
                                         help='The relative path of the content. If omitted, '
                                              'the root of the resource is used and all contents are downloaded '
                                              'in a single zip file.')
    add_version_argument(download_content_parser)

    # updateResource -id 123 -m data_resource.json
    update_resource_parser = operation_subparser.add_parser('updateResource', help='Update a resource\'s metadata '
                                                                                   'providing a complete resource '
                                                                                   'metadata document that will '
                                                                                   'replace the existing version.')
    add_single_identifier_argument(update_resource_parser)
    add_metadata_argument(update_resource_parser, required=True)

    # patchResource -id 123 ... -pl patch.json
    patch_resource_parser = operation_subparser.add_parser('patchResource', help='Patch a resource\'s metadata. '
                                                                                 'In comparison the the update, '
                                                                                 'the patch operation accepts an '
                                                                                 'RFC 6902 JSON Patch document '
                                                                                 'instead of all resource metadata.')
    add_multiple_identifier_argument(patch_resource_parser)
    add_payload_argument(patch_resource_parser, required=True)

    # patchContent -id 123 -rp /folder/file.txt -m patch.json
    patch_content_parser = operation_subparser.add_parser('patchContent', help='Patch content metadata.')
    add_single_identifier_argument(patch_content_parser)
    patch_content_parser.add_argument('-rp', '--relativePath', type=str, default="/",
                                      help='The relative path of the content. The path must point to a single '
                                           'content element. Patching content folders is not supported.')
    add_payload_argument(patch_content_parser, required=True)
    # deleteResource -id 123 [-soft]
    delete_resource_parser = operation_subparser.add_parser('deleteResource',
                                                            help='Delete one or more single resource(s) and '
                                                                 ' all its contents.')
    add_multiple_identifier_argument(delete_resource_parser)
    delete_resource_parser.add_argument('-s', '--soft', action=argparse.BooleanOptionalAction, default=True,
                                        help='This switch allows to perform a soft-delete for resources and is '
                                             'always enabled by default. This means, that a resource is only revoked '
                                             'and will be permanently removed if deleting it a second time. '
                                             'To revoke a delete operation, only patching the \'state\' attribute\'s '
                                             'value from REVOKED to VOLATILE is sufficient. To turn off soft-delete, '
                                             'the option --no-soft must be appended.')

    # deleteContent -id 123 -rp /folder/
    delete_content_parser = operation_subparser.add_parser('deleteContent', help='Delete content.')
    add_single_identifier_argument(delete_content_parser)
    delete_content_parser.add_argument('-rp', '--relativePath', type=str, default="/",
                                       help='The relative path of the content. If omitted, '
                                            'the root of the resource is used.')

    add_global_arguments(parser)

    return parser.parse_args(args)


def main():
    args = parse_arguments(sys.argv[1:])

    # Determine client to use
    service_client = BaseRepoClient(args.debug)

    # Determine and call operation to apply
    response = None

    if args.operation == "createResource":
        # createResource [-m data_resource.json]
        response = service_client.create(None, args.metadata, None, None, args.auth)
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "createContent":
        # createContent -id 123 [-m content_information.json] [-pl file.txt] [-rp folder/file.txt]
        response = service_client.create(args.identifier, args.metadata, args.payload, args.relativePath, args.auth)
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "getResources":
        # getResources [-f 'yesterday'] [-u 'now'] [-p 1] [-s 30]
        query_params = parse_query_params(args)
        response = service_client.get(None, None, query_params, args.auth)
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "getResource":
        # getResource -id 123 [-v 2]
        if len(args.identifier) > 1:
            # multiple ids provided
            all_results = []
            for identifier in args.identifier:
                # Get single resource omitting the version argument to avoid errors if a resource does not have
                # a particular version
                response = service_client.get(identifier, None, None, args.auth)
                all_results += response
            response = all_results
        else:
            # single id provided, also include version attribute
            query_params = [get_query_param_entry("version", str(args.version))]
            response = service_client.get(args.identifier[0], None, query_params, args.auth)
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "getContent":
        # getContent -id 123 [-rp folder/] [-v 2] [-t thumb] [-p 1] [-s 30]
        if len(args.identifier) > 1:
            all_results = []
            for identifier in args.identifier:
                query_params = [get_query_param_entry("page", str(args.page)),
                                get_query_param_entry("size", str(args.pageSize))]
                response = service_client.get(identifier, args.relativePath, query_params, args.auth)
                all_results += response
            response = all_results
        else:
            query_params = None
            if args.relativePath and not args.relativePath.endswith("/"):
                query_params = [get_query_param_entry("version", str(args.version))]

            response = service_client.get(args.identifier[0], args.relativePath, query_params, args.auth)

        response = service_client.render_response(response, args.render_as)
    elif args.operation == "downloadContent":
        # downloadContent -id 123 [-rp /] [-v 1]
        response = service_client.download(args.identifier, args.relativePath, args.version, args.auth)
    elif args.operation == "updateResource":
        # updateResource -id 123 -m data_resource.json
        response = service_client.update(args.identifier, args.metadata, args.auth)
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "patchContent":
        # patchContent -id 123 -rp /folder/file.txt -m patch.json
        response = service_client.patch(args.identifier, args.payload, args.relativePath, args.auth)
        response = service_client.render_response(response, args.render_as)
    elif args.operation == "patchResource":
        # patchResource -id 123 -pl patch.json
        if len(args.identifier) > 1:
            # multiple ids provided
            all_results = []
            for identifier in args.identifier:
                response = service_client.patch(identifier, args.payload, None, args.auth)
                all_results += response
            response = all_results
        else:
            response = service_client.patch(args.identifier[0], args.payload, None, args.auth)

        response = service_client.render_response(response, args.render_as)
    elif args.operation == "deleteResource":
        # deleteResource -id 123 [-soft]
        if len(args.identifier) > 1:
            # multiple ids provided
            for identifier in args.identifier:
                response = service_client.delete(identifier, None, args.soft, args.auth)
                if not response:
                    service_client.print_error("Resource " + identifier + " could not be deleted.")
        else:
            response = service_client.delete(args.identifier[0], None, args.soft, args.auth)
            if not response:
                service_client.print_error("Resource " + args.identifier[0] + " could not be deleted.")
    elif args.operation == "deleteContent":
        # deleteContent -id 123 -rp /folder/
        response = service_client.delete(args.identifier, args.relativePath, None, args.auth)

    if args.output:
        render_to_file(response, args)
    else:
        # print response to stdout
        print(response)


if __name__ == '__main__':
    main()

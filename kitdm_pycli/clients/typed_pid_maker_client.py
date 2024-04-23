import dateparser
import sys
from prettytable import PrettyTable
from kitdm_pycli.helpers.typed_pid_maker_helper import TypedPidMakerClient
from helpers.URLUtils import get_query_param_entry
from kitdm_pycli.helpers.command_line_utils import *
from kitdm_pycli.helpers.render_utils import *

def parse_arguments(args):
    parser = argparse.ArgumentParser(description='Command line client interface for the Typed PID Maker service.')

    operation_subparser = parser.add_subparsers(dest="operation", help='Operation selection')

    # createRecord [-m pid-record.json] [--dry]
    create_resource_parser = operation_subparser.add_parser('createRecord', help='Create a new typed PID record.')
    add_metadata_argument(create_resource_parser)
    create_resource_parser.add_argument('-dry', '--dryRun', action=argparse.BooleanOptionalAction, default=False,
                                        help='This switch allows to perform a dryrun which allows to check if '
                                             'a PID record can be created using the provided metadata, or if '
                                             'validation fails. If dryrun is enabled, no changes are made to the '
                                             'server.')

    # getKnownPid -id 123 ...
    get_pid_parser = operation_subparser.add_parser('getPid', help='List PIDs and their create/modification '
                                                                   'details for one or more PIDs.')
    add_multiple_identifier_argument(get_pid_parser)
    get_pid_parser.add_argument('-v', '--validate', action=argparse.BooleanOptionalAction, default=False,
                                help='This switch allows to perform a validation before the actual PID record '
                                     'is returned. This can be relevant while resolving an unknown PID to '
                                     'ensure, that it points to a valid PID record, even if it was not created '
                                     'by another Typed PID Maker instance.')

    # getKnownPid -id 123 ...
    get_known_pid_parser = operation_subparser.add_parser('getKnownPid', help='Get one or more known PIDs and their '
                                                                              'create/modification details.')
    add_multiple_identifier_argument(get_known_pid_parser)

    # getKnownPids [-f 'yesterday'] [-u 'now'] [-mf 'last year] [-mu yesterday] [-p 1] [-s 30]
    get_known_pids_parser = operation_subparser.add_parser('getKnownPids', help='List all known PIDs and their '
                                                                                'create/modification details, '
                                                                                'optionally filtered by creation time.')
    add_range_filter_arguments(get_known_pids_parser)
    get_known_pids_parser.add_argument('-mf', '--modifiedFromDate', type=str,
                                       help='This parameter allows to filter PIDs based on their '
                                            'modification date. Only PIDs modified after the provided '
                                            'date are returned. The date can be provided in many different '
                                            'ways, e.g., in a short form like 2023-11-02, '
                                            'in ISO format like 2023-11-02T08:33:00Z, or in a semantic '
                                            'form like \'two days ago\'.')
    get_known_pids_parser.add_argument('-mu', '--modifiedUntilDate', type=str,
                                       help='This parameter allows to filter PIDs based on their '
                                            'modification date. Only PIDs modified before the provided '
                                            'date are returned. The date can be provided in many different '
                                            'ways, e.g., in a short form like 2023-11-02, '
                                            'in ISO format like 2023-11-02T08:33:00Z, or in a semantic '
                                            'form like \'two days ago\'.')
    add_pagination_arguments(get_known_pids_parser)

    # updateRecord -id 123 -m pid-record.json
    update_record_parser = operation_subparser.add_parser('updateRecord', help='Update a PID Record\'s metadata '
                                                                               'providing a complete PID record '
                                                                               'document that will '
                                                                               'replace the existing version.')
    add_single_identifier_argument(update_record_parser)
    add_metadata_argument(update_record_parser, required=True)

    add_global_arguments(parser)

    return parser.parse_args(args)


def main():
    args = parse_arguments(sys.argv[1:])

    # Determine client to use
    serviceClient = TypedPidMakerClient(args.debug)

    # Determine and call operation to apply
    response = None

    if args.operation == "createRecord":
        # createRecord [-m pid-record.json] [-dry]
        path = None
        if args.dryRun:
            path = "dry"
        response = serviceClient.create(None, args.metadata, None, path, args.auth)
        response = serviceClient.render_response(response, args.render_as)
    elif args.operation == "getPid":
        # getPid -id 123 [-v]
        query_params = []
        if args.validate:
            query_params.append(get_query_param_entry("validation", "true"))

        if len(args.identifier) > 1:
            allResults = []
            for identifier in args.identifier:
                response = serviceClient.get(identifier, "pid", query_params, args.auth)
                allResults += response
            response = allResults
        else:
            response = serviceClient.get(args.identifier[0], "pid", query_params, args.auth)

        response = serviceClient.render_response(response, args.render_as)

    elif args.operation == "getKnownPid":
        # getKnownPid -id 123
        if len(args.identifier) > 1:
            allResults = []
            for identifier in args.identifier:
                response = serviceClient.get(identifier, "known", None, args.auth)
                allResults += response
            response = allResults
        else:
            response = serviceClient.get(args.identifier[0], "known", None, args.auth)

        response = serviceClient.render_response(response, args.render_as)
    elif args.operation == "getKnownPids":
        # getKnownPids [-f 'yesterday'] [-u 'now'] [-mf 'last year] [-mu yesterday] [-p 1] [-s 30]
        query_params = []

        if args.fromDate:
            fromDate = dateparser.parse(args.fromDate)
            fromDate = fromDate.strftime("%Y-%m-%dT%H:%M:%SZ")
            query_params.append(get_query_param_entry("created_after", fromDate))
        if args.untilDate:
            untilDate = dateparser.parse(args.untilDate)
            untilDate = untilDate.strftime("%Y-%m-%dT%H:%M:%SZ")
            query_params.append(get_query_param_entry("created_before", untilDate))
        if args.modifiedFromDate:
            modifiedFromDate = dateparser.parse(args.modifiedFromDate)
            modifiedFromDate = modifiedFromDate.strftime("%Y-%m-%dT%H:%M:%SZ")
            query_params.append(get_query_param_entry("modified_after", modifiedFromDate))
        if args.modifiedUntilDate:
            modifiedUntilDate = dateparser.parse(args.modifiedUntilDate)
            modifiedUntilDate = modifiedUntilDate.strftime("%Y-%m-%dT%H:%M:%SZ")
            query_params.append(get_query_param_entry("modified_until", modifiedUntilDate))

        query_params.append(get_query_param_entry("page", str(args.page)))
        query_params.append(get_query_param_entry("size", str(args.pageSize)))

        response = serviceClient.get(None, "known", query_params, args.auth)
        response = serviceClient.render_response(response, args.render_as)
    elif args.operation == "updateRecord":
        # updateRecord -id 123 -m pid-record.json
        response = serviceClient.update(args.identifier, args.metadata, args.auth)
        response = serviceClient.render_response(response, args.render_as)

    if args.output:
        render_to_file(response, args)
    else:
        # print response to stdout
        print(response)


if __name__ == '__main__':
    main()

import argparse
from kitdm_pycli.helpers.url_utils import get_query_param_entry


def add_single_identifier_argument(command_parser):
    command_parser.add_argument('-id', '--identifier', type=str, required=True,
                                help='A single resource identifier.')


def add_multiple_identifier_argument(command_parser):
    command_parser.add_argument('-id', '--identifier', type=str, nargs='+', required=True,
                                help='One or more space-separated resource identifiers.')


def add_version_argument(command_parser):
    command_parser.add_argument('-v', '--version', type=int,
                                help='The version of a resource to obtain. Under some circumstances, this argument '
                                     'will be ignored, e.g., if multiple resources are addressed by an operation, '
                                     'as not all resources might be available in the provided version.')


def add_metadata_argument(command_parser, required=False):
    command_parser.add_argument('-m', '--metadata', type=str, required=required,
                                help='The absolute or relative path to a JSON document containing administrative '
                                     'metadata used for creating or updating a resource.')


def add_payload_argument(command_parser, required=False):
    command_parser.add_argument('-pl', '--payload', type=str, required=required,
                                help='The absolute or relative path to a payload file used for uploading contents '
                                     'like data, metadata, or patch instructions.')


def add_range_filter_arguments(command_parser):
    command_parser.add_argument('-f', '--fromDate', type=str,
                                help='This parameter allows to filter resources based on their '
                                     'creation date. Only resources created after the provided '
                                     'date are returned. The date can be provided in many different '
                                     'ways, e.g., in a short form like 2023-11-02, '
                                     'in ISO format like 2023-11-02T08:33:00Z, or in a semantic '
                                     'form like \'two days ago\'.')
    command_parser.add_argument('-u', '--untilDate', type=str,
                                help='This parameter allows to filter resources based on their '
                                     'creation date. Only resources created before the provided '
                                     'date are returned. The date can be provided in many different '
                                     'ways, e.g., in a short form like 2023-11-02, '
                                     'in ISO format like 2023-11-02T08:33:00Z, or in a semantic '
                                     'form like \'two days ago\'.')


def add_pagination_arguments(command_parser):
    command_parser.add_argument('-p', '--page', type=int, default=0,
                                help='The page of a listing that should be returned. Page numbering '
                                     'starts with 0 (default).')
    command_parser.add_argument('-s', '--pageSize', type=int, default=20,
                                help='The size of a listing page, where the default is 20 '
                                     'and the maximum is 100.')


def add_global_arguments(command_parser):
    command_parser.add_argument('-a', '--auth', action=argparse.BooleanOptionalAction,
                                help='Switch for enabling/disabling authentication before the actual service request. '
                                     'If enabled, the KeyCloak instance configured in properties.json is used. '
                                     'By default, the user is asked for username and password. However, both can '
                                     'also be configured in properties.json such that only missing information is '
                                     'requested, e.g., if the password is not stored in properties.json, which is '
                                     'anyway only recommended in a protected environment.')
    command_parser.add_argument('-r', '--render_as', choices=['TABLE', 'LIST', 'RAW'], default="TABLE",
                                help='This parameter allows to configure the way results are rendered. By default, a '
                                     'user-friendly representation as table is printed where results are returned. '
                                     'The visible columns of the table can be configured in properties.json.'
                                     'Alternatively, only the resource ids can be printed for further processing '
                                     'or the raw result can be returned.')
    command_parser.add_argument('-o', '--output', type=str,
                                help='The absolute or relative path of an output file used to store the output of the '
                                     'performed operation, e.g., a file download or the rendered result. If used in '
                                     'combination with --render_as TABLE or LIST outputs that can rendered as such '
                                     'are re-formatted depending on the output file extension. '
                                     'Supported extensions are .csv (comma separated), .json (structured table), '
                                     'and .html (web table). If not provided, all outputs are printed to stdout.')

    command_parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction, default=False,
                                help='Enable verbose output for debugging. Disabled by default.')


def parse_query_params(args):
    query_params = []

    if args.fromDate:
        from_date = dateparser.parse(args.fromDate)
        from_date = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        query_params.append(get_query_param_entry("from", from_date))
    if args.untilDate:
        until_date = dateparser.parse(args.untilDate)
        until_date = until_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        query_params.append(get_query_param_entry("until", until_date))

    query_params.append(get_query_param_entry("page", str(args.page)))
    query_params.append(get_query_param_entry("size", str(args.pageSize)))

    return query_params

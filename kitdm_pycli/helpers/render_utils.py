from prettytable import PrettyTable
import flatdict


def render_as_table(content, table_items_callback):
    """
    Render the provided content as table. The table structure is obtained from the caller using the provided
    callback function.

    :param content: The content to render.
    :param table_items_callback A callback returning the table structure depending on the provided content.
    :return: The rendered output as PrettyTable object.
    """
    if not content or len(content) == 0:
        return None

    table_items = table_items_callback(content[0])
    result_table = PrettyTable(table_items.keys())
    result_table.max_width = 60

    for elem in content:
        flat = flatdict.FlatterDict(elem, delimiter=".")
        row = []
        for key in table_items.keys():
            row.append(flat.get(table_items.get(key)))
        result_table.add_row(row)

    return result_table


def render_as_list(content, id_callback):
    """
    Render the provided content as list of ids. The id for each content element is obtained from the caller by using
    the provided callback function.
    :param content: A list of content element.
    :param id_callback: A callback function returning the id value for a given element.
    :return: The rendered output as PrettyTable object.
    """
    if len(content) == 0:
        return None

    result_table = PrettyTable(["Id"])
    for elem in content:
        result_table.add_row([id_callback(elem)])

    return result_table


def render_to_file(response, args):
    # write to file
    file_content = None
    if type(response) == PrettyTable:
        # PrettyTable can be written depending on output extension
        if args.output.endswith(".csv"):
            file_content = response.get_csv_string()
        elif args.output.endswith(".json"):
            file_content = response.get_json_string()
        elif args.output.endswith(".html"):
            file_content = response.get_html_string()
        else:
            file_content = response.get_string()
    else:
        # If not PrettyTable, just use the result as file
        file_content = str(response)

    open(args.output, "wb").write(bytes(file_content, "UTF-8"))
    print("Output written to " + args.output)

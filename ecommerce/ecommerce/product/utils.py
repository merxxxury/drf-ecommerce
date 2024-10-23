from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.sql import SqlLexer
from sqlparse import format


def remove_empty_fields(data_dict: dict, fields_list: list) -> dict:
    """
    Remove empty fields from a dictionary.

    This function is typically used within a serializer's `to_representation`
    method to remove fields with empty values from the serialized JSON representation.

    Args:
        data_dict (dict): The dictionary containing serialized data.
        fields_list (list): A list of field names (strings) to check and potentially remove.

    Returns:
        dict: The modified dictionary with empty fields removed.
    """
    for field in fields_list:
        # Remove the field if its value is empty or evaluates to False
        if not data_dict[field]:
            data_dict.pop(field, None)

    return data_dict


def inspect_queries(list_of_connection_queries: list) -> str:
    """
    Tool for inspecting SQL queries executed during a request.

    This function is useful for development and debugging purposes.
    It takes a list of queries executed by the database connection,
    formats them and highlights them using syntax highlighting.
    It also returns the total number of queries.


    Need to import:
        from django.db import connection
    Args:
        list_of_connection_queries (list): A list of SQL queries from `connection.queries`.

    Returns:
        str: A formatted string containing the highlighted SQL queries
             and the total number of queries.
    """

    data = ''
    for query in list_of_connection_queries:
        sql_formatted = format(str(query['sql']), reindent=True)
        data += highlight(sql_formatted, SqlLexer(), TerminalFormatter())

    data += f'Number of queries: {len(list_of_connection_queries)}'
    return data

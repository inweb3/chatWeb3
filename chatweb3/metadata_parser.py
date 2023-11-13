# %%
import json
import logging
import re
from collections import defaultdict
from typing import Dict, List, Optional

from chatweb3.utils import parse_table_long_name, parse_table_long_name_to_json_list
from config.logging_config import get_logger

# logger = get_logger(
#     __name__, log_level=logging.INFO, log_to_console=True, log_to_file=True
# )
logger = get_logger(__name__)


def nested_dict_to_dict(d):
    return {
        key: nested_dict_to_dict(value) if isinstance(value, defaultdict) else value
        for key, value in d.items()
    }


def dict_to_nested_dict(d):
    nested = nested_dict()
    for key, value in d.items():
        if isinstance(value, dict):
            nested[key] = dict_to_nested_dict(value)
        else:
            nested[key] = value
    return nested


def len_nested_dict(nested_dict):
    count = 0
    for value in nested_dict.values():
        if isinstance(value, dict):
            count += len_nested_dict(value)
        else:
            count += 1
    return count


def nested_dict():
    return defaultdict(nested_dict)


class Column:
    def __init__(
        self,
        name,
        table_name=None,
        schema_name=None,
        database_name=None,
        data_type=None,
        comment=None,
        verbose=False,
    ):
        self.name = name.lower()
        self.table_name = table_name.lower() if table_name else None
        self.schema_name = schema_name.lower() if schema_name else None
        self.database_name = database_name.lower() if database_name else None
        self.data_type = data_type
        self.comment = comment
        self.sample_values_list = []
        self.verbose = verbose

    def __repr__(self) -> str:
        return f"Column('{self.database_name}, {self.schema_name}, {self.table_name}, {self.name}, {self.data_type}, {self.comment}')"

    def __eq__(self, other):
        if isinstance(other, Column):
            return (
                self.name == other.name
                and self.table_name == other.table_name
                and self.schema_name == other.schema_name
                and self.database_name == other.database_name
                and self.data_type == other.data_type
                and self.comment == other.comment
            )
        return False

    # property for verbose
    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value

    def _parse_data_type_from_create_table_stmt(self, create_table_stmt):
        pattern = rf"{self.name}\s+(?P<data_type>.+?(\([^\)]+\))?(?=\s*(,|\n\s*\))))"

        match = re.search(pattern, create_table_stmt, re.IGNORECASE)

        if match:
            data_type = match.group("data_type")
        else:
            if self.verbose:
                logger.warning(
                    f"{self.database_name}.{self.schema_name}.{self.table_name}: {self.name} data type not parsed from create table statement."
                )
            data_type = None
        return data_type

    def _parse_comment_from_ddl(self, get_ddl_create_table):
        pattern = rf"{self.name}\s+([\w\(\),]*)?\s*COMMENT\s+'(?P<comment>.*?)'"
        match = re.search(pattern, get_ddl_create_table, re.IGNORECASE | re.DOTALL)

        if match:
            comment = match.group("comment")
        else:
            if self.verbose:
                logger.warning(
                    f"{self.database_name}.{self.schema_name}.{self.table_name}: {self.name} comment not parsed from get_ddl_create_table."
                )
            comment = None
        return comment

    def _parse_value_from_sample_rows(self, sample_row_column_names, sample_rows):
        if self.name in sample_row_column_names:
            index = sample_row_column_names.index(self.name)
            values = [row[index] for row in sample_rows]
            sample_values_list = list(values)
        else:
            if self.verbose:
                logger.warning(
                    f"{self.database_name}.{self.schema_name}.{self.table_name}: {self.name} value not parsed from sample rows."
                )
            sample_values_list = None
        return sample_values_list

    def to_dict(self):
        return {
            "name": self.name,
            "table_name": self.table_name,
            "schema_name": self.schema_name,
            "database_name": self.database_name,
            "data_type": self.data_type,
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("name"),
            data.get("table_name"),
            data.get("schema_name"),
            data.get("database_name"),
            data.get("data_type"),
            data.get("comment"),
        )


class Table:
    def __init__(self, table_name, schema_name, database_name, verbose=False):
        self.name = table_name.lower()
        self.schema_name = schema_name.lower()
        self.database_name = database_name.lower()
        self.long_name = f"{database_name}.{schema_name}.{table_name}".lower()
        self.comment = ""
        self.summary = ""
        self.column_names = []
        self.columns = {}
        self.create_table_stmt = None
        self.select_sample_rows_stmt = None
        self.sample_row_column_names = None
        self.sample_rows = None
        self.select_get_ddl_table_stmt = None
        self.get_ddl_create_table = None
        self.select_information_schema_columns_stmt = None
        self.information_schema_columns_names = None
        self.information_schema_columns_values = None
        self.verbose = verbose

    def __repr__(self) -> str:
        return f"Table(name='{self.name}', long_name='{self.long_name}', database_name='{self.database_name}', schema_name='{self.schema_name}', column_names={self.column_names}), summary='{self.summary}', comment='{self.comment}')"

    def __eq__(self, other):
        if isinstance(other, Table):
            return (
                self.name == other.name
                and self.database_name == other.database_name
                and self.schema_name == other.schema_name
                and self.long_name == other.long_name
                and self.comment == other.comment
                and self.summary == other.summary
                and self.column_names == other.column_names
                and self.create_table_stmt == other.create_table_stmt
                and self.select_sample_rows_stmt == other.select_sample_rows_stmt
                and self.sample_row_column_names == other.sample_row_column_names
                and self.sample_rows == other.sample_rows
                and self.select_get_ddl_table_stmt == other.select_get_ddl_table_stmt
                and self.get_ddl_create_table == other.get_ddl_create_table
                and self.select_information_schema_columns_stmt
                == other.select_information_schema_columns_stmt
                and self.information_schema_columns_names
                == other.information_schema_columns_names
                and self.information_schema_columns_values
                == other.information_schema_columns_values
                and self.columns == other.columns
            )
        return False

    # create a property for summary
    @property
    def summary(self):
        return self._summary

    # setter for summary for the table and its columns
    @summary.setter
    def summary(self, summary):
        self._summary = summary
        # for column in self.columns.values():
        #     column.summary = summary

    # create a property for verbose
    @property
    def verbose(self):
        return self._verbose

    # setter for verbose for the table and its columns
    @verbose.setter
    def verbose(self, verbose):
        self._verbose = verbose
        for column in self.columns.values():
            column.verbose = verbose

    def _parse_comment_from_ddl(self, get_ddl_create_table):
        comment_pattern = re.compile(
            r"COMMENT='{1,3}(.*?)'{1,3}(?:[\s\\n]*as[\s\\n]*\((?:.|[\r\n])*?SELECT|[\s\\n]*;)",
            re.IGNORECASE,
        )
        match = comment_pattern.search(get_ddl_create_table)
        if match:
            comment = match.group(1).strip().replace("\\n", "\n")
        else:
            if self.verbose:
                logger.warning(
                    f"Could not parse comment for table {self.database_name}.{self.schema_name}.{self.name}"
                )
            comment = ""
        return comment

    def _create_columns(self):
        """Create Column objects for each column in the table if they do not already exist."""
        for column_name in self.column_names:
            if column_name not in self.columns:
                self.columns[column_name] = Column(
                    name=column_name,
                    table_name=self.name,
                    schema_name=self.schema_name,
                    database_name=self.database_name,
                )

    @staticmethod
    def _format_value(value):
        if isinstance(value, str):
            replaced_value = value.replace("\n", " ")
            # return f"'{replaced_value}'"
            return replaced_value
        return value

    def _get_metadata(
        self,
        include_table_name: bool = True,
        include_table_summary: bool = True,
        include_column_names: bool = False,
        include_column_info: bool = True,
        column_info_format: Optional[List[str]] = None,
    ) -> str:
        """
        By default, this method returns a string with the table name, summary.
        Optionally it can return column names, or more detailed column information.
        """
        output = ""
        if include_table_name:
            output += f"'{self.database_name}.{self.schema_name}.{self.name}': the '{self.name}' table in '{self.schema_name}' schema of '{self.database_name}' database. "
        if include_table_summary and not include_column_info:
            # if include_column_info if True, then we will use the table comment as the summary and not the table summary
            output += f"{self.summary}"

        if include_column_names and not include_column_info:
            column_names = ", ".join(self.column_names)
            output += f"This table has the following columns: '{column_names}'\n"

        if include_column_info:
            if column_info_format is None:
                column_info_format = [
                    "name",
                    "comment",
                    "data_type",
                    "sample_values_list",
                ]
            column_info = {
                "name": "Name",
                "comment": "Comment",
                "data_type": "Data type",
                "sample_values_list": "List of sample values",
            }

            output += f"\nComment: {self.comment}\n"

            if len(column_info_format) > 0:
                output += "Columns in this table:\n"

                headers = [column_info[col] for col in column_info_format]
                output += "\t" + " | ".join(headers) + "\n"
                output += "\t" + "--- | " * (len(column_info_format) - 1) + "---\n"

                for column in self.columns.values():
                    column_values = [getattr(column, col) for col in column_info_format]

                    formatted_values = [
                        ", ".join(str(self._format_value(v)) for v in value)
                        if isinstance(value, list)
                        else self._format_value(value)
                        for value in column_values
                    ]

                    output += (
                        "\t" + " | ".join([str(val) for val in formatted_values]) + "\n"
                    )

        return output.strip()

    def to_dict(self):
        return {
            key: value
            for key, value in {
                "name": self.name,
                "database_name": self.database_name,
                "schema_name": self.schema_name,
                "long_name": self.long_name,
                "comment": self.comment,
                "summary": self.summary,
                "column_names": self.column_names,
                "columns": {
                    name: column.to_dict() for name, column in self.columns.items()
                },
                "create_table_stmt": self.create_table_stmt,
                "select_sample_rows_stmt": self.select_sample_rows_stmt,
                "sample_row_column_names": self.sample_row_column_names,
                "sample_rows": self.sample_rows,
                "select_get_ddl_table_stmt": self.select_get_ddl_table_stmt,
                "get_ddl_create_table": self.get_ddl_create_table,
                "select_information_schema_columns_stmt": self.select_information_schema_columns_stmt,
                "information_schema_columns_names": self.information_schema_columns_names,
                "information_schema_columns_values": self.information_schema_columns_values,
            }.items()
            if value
        }

    @classmethod
    def from_dict(cls, data):
        table = cls(
            data.get("name"), data.get("schema_name"), data.get("database_name")
        )
        # data["name"], data["schema_name"], data["database_name"])
        table.long_name = data.get("long_name").lower()
        table.comment = data.get("comment")
        table.summary = data.get("summary")
        table.column_names = [x.lower() for x in data.get("column_names")]
        table.columns = {
            name.lower(): Column.from_dict(col_data)
            for name, col_data in data.get("columns", {}).items()
        }
        table.create_table_stmt = data.get("create_table_stmt")
        table.select_sample_rows_stmt = data.get("select_sample_rows_stmt")
        table.sample_row_column_names = data.get("sample_row_column_names")
        table.sample_rows = data.get("sample_rows")
        table.select_get_ddl_table_stmt = data.get("select_get_ddl_table_stmt")
        table.get_ddl_create_table = data.get("get_ddl_create_table")
        table.select_information_schema_columns_stmt = data.get(
            "select_information_schema_columns_stmt"
        )
        table.information_schema_columns_names = data.get(
            "information_schema_columns_names"
        )
        table.information_schema_columns_values = data.get(
            "information_schema_columns_values"
        )
        # adjust for columns
        return table


class Schema:
    def __init__(self, schema_name, database_name, verbose=False):
        self.name = schema_name
        self.database_name = database_name.lower()
        self.long_name = f"{database_name}.{schema_name}".lower()
        self.tables = {}
        self.verbose = verbose

    def __repr__(self) -> str:
        return f"Schema(name='{self.name}', long_name='{self.long_name}', database_name='{self.database_name}', tables={self.tables})"

    def __eq__(self, other):
        if isinstance(other, Schema):
            return (
                self.name == other.name
                and self.database_name == other.database_name
                and self.long_name == other.long_name
                and self.tables == other.tables
            )
        return False

    # property for verbose
    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value
        for table in self.tables.values():
            table.verbose = value

    def to_dict(self):
        return {
            "name": self.name,
            "database_name": self.database_name,
            "tables": {name: table.to_dict() for name, table in self.tables.items()},
        }

    @classmethod
    def from_dict(cls, data):
        schema = cls(data["name"], data["database_name"])
        schema.tables = {
            name.lower(): Table.from_dict(table_data)
            for name, table_data in data["tables"].items()
        }
        return schema


class Database:
    def __init__(self, database_name, verbose=False):
        self.name = database_name
        self.schemas = {}
        self.verbose = verbose

    def __repr__(self) -> str:
        return f"Database(name='{self.name}', schemas={self.schemas})"

    def __eq__(self, other):
        if isinstance(other, Database):
            return self.name == other.name and self.schemas == other.schemas
        return False

    # property for verbose
    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value
        for schema in self.schemas.values():
            schema.verbose = value

    def to_dict(self):
        return {
            "name": self.name,
            "schemas": {
                name: schema.to_dict() for name, schema in self.schemas.items()
            },
        }

    @classmethod
    def from_dict(cls, data):
        database = cls(data.get("name"))
        # ["name"])
        database.schemas = {
            name.lower(): Schema.from_dict(schema_data)
            for name, schema_data in data["schemas"].items()
        }
        return database


class RootSchema:
    def __init__(self):
        self.databases = {}  # dictionary of databases
        self.verbose = False

    def __repr__(self) -> str:
        return f"RootSchema(databases={self.databases})"

    def __eq__(self, other):
        if isinstance(other, RootSchema):
            return self.databases == other.databases
        return False

    # property for verbose
    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value
        for database in self.databases.values():
            database.verbose = value

    def to_dict(self):
        return {
            "databases": {
                name: database.to_dict() for name, database in self.databases.items()
            },
        }

    @classmethod
    def from_dict(cls, data):
        root_schema = cls()
        root_schema.databases = {
            name.lower(): Database.from_dict(cat_data)
            for name, cat_data in data["databases"].items()
        }
        return root_schema


class MetadataParser:
    def __init__(
        self,
        file_path: Optional[str] = None,
        annotation_file_path: Optional[str] = None,
        verbose: bool = False,
    ):
        """
        Note: the verbose flag is only effective when the file_path is provided. Otherwise, we have to manually set it after the contents of the root_schema_obj is set.
        The verbose flag is useful when we want to print out the processing warning messages, e.g., parsing issues for comments and other fields of metadata.
        """
        self.file_path = file_path
        self._verbose = verbose

        self._initialize_nested_dicts()

        if file_path is not None:
            # If a file_path is provided, load metadata from the file
            data = self.load_metadata_from_json()
            # then deserialize the metadata into the RootSchema object
            self.from_dict(data, verbose=verbose)

            if annotation_file_path is not None:
                # If an annotation_file_path is provided, load the annotation file and add the summary to the RootSchema object
                self.add_table_summary(file_path_json=annotation_file_path)

            # set the verbose flag for the RootSchema object
            # self.verbose = verbose
        else:
            # If no file_path is provided, create an empty RootSchema object
            self.root_schema_obj = RootSchema()

    def from_dict(self, data, verbose: bool = False):
        """Takes in the metadata dictionary loaded from the JSON file and deserializes it into the RootSchema object"""
        self.root_schema_obj = RootSchema.from_dict(data=data["root_schema_obj"])
        self._unify_names_to_lower_cases()
        # Create the column objects for each table
        self._create_table_columns()
        if verbose:
            self.root_schema_obj.verbose = verbose

        # Populate the comment for each table
        self._populate_table_comment()
        # Populate various column attributes
        self._populate_column_table_schema_database_names()
        self._populate_column_data_type()
        self._populate_column_comment()
        self._populate_column_sample_values_list()

        # NOTE: the use of nested dicts will be removed in the future
        # Initialize the nested dictionaries
        self._initialize_nested_dicts()
        # Populate the nested dictionaries
        self._populate_nested_dicts()

    def to_dict(self):
        self._unify_names_to_lower_cases()
        data = {
            "root_schema_obj": self.root_schema_obj.to_dict(),
        }
        return data

    def _initialize_nested_dicts(self):
        self.create_table_stmt = nested_dict()
        self.select_sample_rows_stmt = nested_dict()
        self.table_sample_rows = nested_dict()
        self.table_sample_row_column_names = nested_dict()
        self.select_get_ddl_table_stmt = nested_dict()
        self.get_ddl_create_table = nested_dict()
        self.select_information_schema_columns_stmt = nested_dict()
        self.information_schema_columns_names = nested_dict()
        self.information_schema_columns_values = nested_dict()

    def _populate_nested_dicts(self):
        for database_name, database in self.root_schema_obj.databases.items():
            for schema_name, schema in database.schemas.items():
                for table_name, table in schema.tables.items():
                    self.create_table_stmt[database_name][schema_name][table_name] = (
                        table.create_table_stmt or None
                    )

                    self.select_sample_rows_stmt[database_name][schema_name][
                        table_name
                    ] = (table.select_sample_rows_stmt or None)

                    self.table_sample_row_column_names[database_name][schema_name][
                        table_name
                    ] = (table.sample_row_column_names or None)

                    self.table_sample_rows[database_name][schema_name][table_name] = (
                        table.sample_rows or None
                    )

                    self.select_get_ddl_table_stmt[database_name][schema_name][
                        table_name
                    ] = (table.select_get_ddl_table_stmt or None)

                    self.get_ddl_create_table[database_name][schema_name][
                        table_name
                    ] = (table.get_ddl_create_table or None)

                    self.select_information_schema_columns_stmt[database_name][
                        schema_name
                    ][table_name] = (
                        table.select_information_schema_columns_stmt or None
                    )

                    self.information_schema_columns_names[database_name][schema_name][
                        table_name
                    ] = (table.information_schema_columns_names or None)

                    self.information_schema_columns_values[database_name][schema_name][
                        table_name
                    ] = (table.information_schema_columns_values or None)

    def _populate_column_table_schema_database_names(self):
        for database_name, database in self.root_schema_obj.databases.items():
            for schema_name, schema in database.schemas.items():
                for table_name, table in schema.tables.items():
                    for column in table.columns.values():
                        column.table_name = table_name
                        column.schema_name = schema_name
                        column.database_name = database_name

    def _create_table_columns(self):
        """Create Column objects for each column in each table in each schema in each database, if they do not already exists."""
        for database_name, database in self.root_schema_obj.databases.items():
            for schema_name, schema in database.schemas.items():
                for table_name, table in schema.tables.items():
                    table._create_columns()

    def _populate_column_comment(self):
        for database_name, database in self.root_schema_obj.databases.items():
            for schema_name, schema in database.schemas.items():
                for table_name, table in schema.tables.items():
                    ddl_create_table = table.get_ddl_create_table
                    for column in table.columns.values():
                        column.comment = (
                            column._parse_comment_from_ddl(ddl_create_table)
                            if ddl_create_table
                            else None
                        )

    #                    ddl_create_table = self.get_ddl_create_table[database_name][ schema_name ][table_name]

    def _populate_column_data_type(self):
        for database_name, database in self.root_schema_obj.databases.items():
            for schema_name, schema in database.schemas.items():
                for table_name, table in schema.tables.items():
                    create_table_stmt = table.create_table_stmt
                    for column in table.columns.values():
                        column.data_type = (
                            (
                                column._parse_data_type_from_create_table_stmt(
                                    create_table_stmt
                                )
                            )
                            if create_table_stmt
                            else None
                        )

                    # create_table_stmt = self.create_table_stmt[database_name][ schema_name ][table_name]

    def _populate_column_sample_values_list(self):
        for database in self.root_schema_obj.databases.values():
            for schema in database.schemas.values():
                for table in schema.tables.values():
                    for column in table.columns.values():
                        column.sample_values_list = (
                            column._parse_value_from_sample_rows(
                                table.sample_row_column_names,
                                table.sample_rows,
                            )
                            if table.sample_rows
                            else None
                        )

    def _populate_table_comment(self):
        for db in self.root_schema_obj.databases.values():
            for schema in db.schemas.values():
                for table in schema.tables.values():
                    table.comment = (
                        table._parse_comment_from_ddl(table.get_ddl_create_table)
                        if table.get_ddl_create_table
                        else None
                    )

    def _unify_names_to_lower_cases(self):
        for database in self.root_schema_obj.databases.values():
            database.name = database.name.lower()
            for schema in database.schemas.values():
                schema.name = schema.name.lower()
                for table in schema.tables.values():
                    table.name = table.name.lower()
                    for column in table.columns.values():
                        column.name = column.name.lower()

    def add_table_summary(
        self,
        table_summary_json: Optional[Dict] = None,
        file_path_json: Optional[str] = None,
    ):
        """Add a table summary to the metadata.
        Input file must be a JSON file with the following structure:
        {
            "table_summary": {
            "table_long_name": "table_summary",
            "table_long_name": "table_summary",
            ...
            }
        }
        """
        if table_summary_json is None and file_path_json is None:
            raise ValueError(
                "Either table_summary_json or file_path_json must be provided."
            )

        if table_summary_json and file_path_json:
            logging.warning(
                "Both table_summary_json and file_path_json are provided, use file_path_json only."
            )

        print(f"{file_path_json=}")
        if file_path_json:
            try:
                with open(file_path_json, "r") as f:
                    data = json.load(f)
                    print(f"{data=}")
                    table_summary = data.get("table_summary", None)
                    print(f"{table_summary=}")
            except FileNotFoundError:
                print(f"File not found: {file_path_json}")
        elif table_summary_json:
            # table_summary = json.loads(table_summary_json)
            table_summary = table_summary_json
        else:
            raise ValueError(
                f"Unable to load table summary from {file_path_json} or {table_summary_json}."
            )

        for table_long_name, summary in table_summary.items():
            # parse the table long name
            database_name, schema_name, table_name = parse_table_long_name(
                table_long_name
            )
            # add the summary to the table
            self.root_schema_obj.databases[database_name].schemas[schema_name].tables[
                table_name
            ].summary = summary

    # create a property to access the verbose attribute
    @property
    def verbose(self):
        return self._verbose

    # create a setter for the verbose attribute
    @verbose.setter
    def verbose(self, value: bool):
        self._verbose = value
        self.root_schema_obj.verbose = value

    def save_metadata_to_json(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f)

    def load_metadata_from_json(self, file_path=None):
        """Load metadata from a JSON file and returns it."""
        if file_path is None:
            file_path = self.file_path

        with open(file_path, "r") as f:
            metadata = json.load(f)
        return metadata

    def get_tables_from_database_schema_table_names(
        self, database_name=None, schema_name=None, table_name=None
    ):
        """return a table or a list of tables
        filtered by database_name, schema_name, and table_name if provided return all table names if database_name or schema_name is None
        """
        # check for error conditions in database_name
        if database_name is not None and not isinstance(database_name, str):
            raise ValueError("database_name must be a string")
        if schema_name is not None and not isinstance(schema_name, str):
            raise ValueError("schema_name must be a string")
        if table_name is not None and not isinstance(schema_name, str):
            raise ValueError("schema_name must be a string")

        tables = []

        if table_name:
            # if table_name is provided, then we only return one table
            if database_name is None or schema_name is None:
                raise ValueError(
                    "database_name and schema_name must be provided if table_name is provided"
                )
            table = (
                self.root_schema_obj.databases[database_name]
                .schemas[schema_name]
                .tables[table_name]
            )
            tables.append(table)
        else:
            for (
                cat_name,
                database,
            ) in (
                self.root_schema_obj.databases.items()
            ):  # database could be e.g., "ethereum"
                if database_name is None or cat_name == database_name:
                    for sch_name, schema in database.schemas.items():
                        if schema_name is None or sch_name == schema_name:
                            for table in schema.tables.values():
                                tables.append(table)
        return tables

    def get_table_metadata(
        self,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        tables: Optional[List] = None,
        include_table_name: Optional[bool] = True,
        include_table_summary: Optional[bool] = True,
        include_column_names: Optional[bool] = False,
        include_column_info: Optional[bool] = True,
        column_info_format: Optional[List] = None,
    ):
        """
        Process and return metadata information given database, schema and table.

        Args:
            database (str, optional): The database of the table.
            schema (str, optional): The schema of the table.
            tables (list of str, optional): The names of the tables.

        Returns:
            str: The concatenated table information.

        """
        target_tables = self._find_target_tables(database, schema, tables)

        output = ""
        for table in target_tables:
            output += table._get_metadata(
                include_table_name=include_table_name,
                include_table_summary=include_table_summary,
                include_column_names=include_column_names,
                include_column_info=include_column_info,
                column_info_format=column_info_format,
            )

            output += "\n\n"

        return output.strip()

    def _find_target_tables(self, database=None, schema=None, tables=None):
        matched_tables = []

        if database is not None and database not in self.root_schema_obj.databases:
            logger.warning(f"Database '{database}' does not exist.")

        for db_name, db in self.root_schema_obj.databases.items():
            if database is None or db_name == database:
                for sch_name, sch in db.schemas.items():
                    if schema is None or sch_name == schema:
                        if tables is None:
                            matched_tables.extend(list(sch.tables.values()))
                        else:
                            for table_name in tables:
                                if table_name in sch.tables:
                                    matched_tables.append(sch.tables[table_name])

        return matched_tables

    def get_metadata_by_table_long_names(
        self,
        table_long_names: str,
        include_table_name: Optional[bool] = True,
        include_table_summary: Optional[bool] = True,
        include_column_names: Optional[bool] = False,
        include_column_info: Optional[bool] = True,
        column_info_format: Optional[List] = None,
    ) -> str:
        """
        Process and return metadata information given a list of table long names in the form of
        database_name.schema_name.table_name.

        Args:
            table_long_names (str): The list of table long names.

        Returns:
            str: The concatenated table information.
        """

        parsed_table_info = parse_table_long_name_to_json_list(table_long_names)

        output = ""
        for info in parsed_table_info:
            database = info["database"]
            schema = info["schema"]
            tables = info["tables"]
            output += self.get_table_metadata(
                database,
                schema,
                tables,
                include_table_name=include_table_name,
                include_table_summary=include_table_summary,
                include_column_names=include_column_names,
                include_column_info=include_column_info,
                column_info_format=column_info_format,
            )
            output += "\n\n"

        return output.strip()

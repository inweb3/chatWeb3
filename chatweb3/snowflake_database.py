# %%
import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from flipside import Flipside
from langchain.sql_database import SQLDatabase
from shroomdk import ShroomDK
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine

# from sqlalchemy.engine.cursor import LegacyCursorResult
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.row import Row
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import CreateTable

from config.logging_config import get_logger

logger = get_logger(
    __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
)


class SnowflakeDatabase(SQLDatabase):
    def __init__(
        self,
        engine: Engine,
        # schema: Optional[str] = None,
        schema: str,
        metadata: Optional[MetaData] = None,
        ignore_tables: Optional[List[str]] = None,
        include_tables: Optional[List[str]] = None,
        sample_rows_in_table_info: int = 3,
        indexes_in_table_info: bool = False,
        custom_table_info: Optional[dict] = None,
        view_support: bool = True,
    ):
        """
        We make schema a required parameter for SnowflakeDatabase, because we know it is needed for our databases.
        We also make view_support required and default to True, because we know it is needed for our databases.
        """

        super().__init__(
            engine=engine,
            schema=schema,
            metadata=metadata,
            ignore_tables=ignore_tables,
            include_tables=include_tables,
            sample_rows_in_table_info=sample_rows_in_table_info,
            indexes_in_table_info=indexes_in_table_info,
            custom_table_info=custom_table_info,
            view_support=view_support,
        )

    def run(  # type: ignore
        self, command: str, fetch: str = "all", return_string: bool = True
    ) -> Union[str, CursorResult]:
        """Execute a SQL command and return a string representing the results.

        If the statement returns rows, a string of the results is returned.
        If the statement returns no rows, an empty string is returned.
        """
        # logger.debug(f"Entering run with command: {command}")

        with self._engine.begin() as connection:
            if self._schema is not None:
                # Set the session-level default schema

                if self.dialect == "snowflake":
                    set_schema_command = f"USE SCHEMA {self._schema}"
                    connection.execute(text(set_schema_command))
                else:
                    connection.exec_driver_sql(f"SET search_path TO {self._schema}")

            cursor: CursorResult = connection.execute(text(command))

            if cursor.returns_rows:
                if return_string:
                    if fetch == "all":
                        # result_all: List[Row] = cursor.fetchall()
                        result_all: Sequence[Row[Any]] = cursor.fetchall()
                        return str(result_all)
                    elif fetch == "one":
                        fetched = cursor.fetchone()
                        result_one: Optional[Tuple[Any, ...]] = (
                            fetched[0] if fetched else None
                        )
                        return str(result_one)
                    else:
                        raise ValueError(
                            "Fetch parameter must be either 'one' or 'all'"
                        )
                else:
                    return cursor
        return "" if return_string else cursor

    def run_no_throw(  # type: ignore
        self, command: str, fetch: str = "all", return_string: bool = True
    ) -> Union[str, CursorResult]:
        """Execute a SQL command and return a string representing the results.

        If the statement returns rows, a string of the results is returned.
        If the statement returns no rows, an empty string is returned.

        If the statement throws an error, the error message is returned.
        """
        try:
            return self.run(command, fetch, return_string)
        except SQLAlchemyError as e:
            """Format the error message"""
            return f"Error: {e}"

    def get_table_info_no_throw(  # type: ignore
        self, table_names: Optional[List[str]] = None, as_dict: bool = False
    ) -> Union[str, Dict[str, str]]:
        """
        Get the table info for the given table names.
        This is a temperary hack to get around the fact that the parent method returns a string, but we want to return a dictionary of table names to table info strings
        We duplicate the parent method here to avoid having to modify the parent method.
        """
        try:
            all_table_names = self.get_usable_table_names()
            if table_names is not None:
                missing_tables = set(table_names).difference(all_table_names)
                if missing_tables:
                    raise ValueError(
                        f"table_names {missing_tables} not found in database"
                    )
                all_table_names = table_names

            meta_tables = [
                tbl
                for tbl in self._metadata.sorted_tables
                if tbl.name in set(all_table_names)
                and not (self.dialect == "sqlite" and tbl.name.startswith("sqlite_"))
            ]

            tables = []
            for table in meta_tables:
                if self._custom_table_info and table.name in self._custom_table_info:
                    tables.append(self._custom_table_info[table.name])
                    continue

                # add create table command
                create_table = str(CreateTable(table).compile(self._engine))
                table_info = f"{create_table.rstrip()}"
                has_extra_info = (
                    self._indexes_in_table_info or self._sample_rows_in_table_info
                )
                if has_extra_info:
                    table_info += "\n\n/*"
                if self._indexes_in_table_info:
                    table_info += f"\n{self._get_table_indexes(table)}\n"
                if self._sample_rows_in_table_info:
                    table_info += f"\n{self._get_sample_rows(table)}\n"
                if has_extra_info:
                    table_info += "*/"
                tables.append(table_info)
            if as_dict:
                return {
                    table.name: table_info
                    for table, table_info in zip(meta_tables, tables)
                }
            else:
                final_str = "\n\n".join(tables)
                return final_str

        except ValueError as e:
            if table_names is not None and as_dict:
                return {table_name: str(e) for table_name in table_names}
            else:
                return f"Error: {e}"


class SnowflakeContainer:
    def __init__(
        self,
        flipside_api_key: str,
        user: str,
        password: str,
        account_identifier: str,
        shroomdk_api_key: Optional[str] = None,
        local_index_file_path: Optional[str] = None,
        index_annotation_file_path: Optional[str] = None,
        verbose: bool = False,
    ):
        """Create a Snowflake container.
        It stores the user, password, and account identifier for a Snowflake account.
        It has a _databases attribute that stores SQLDatabase objects, which are created on demand.
        These databases can be accessed via the (database, schema) key pair
        It can later append the database and schema to the URL to create a Snowflake db engine.
        """
        # delay import to avoid circular import
        from chatweb3.metadata_parser import MetadataParser

        self._user = user
        self._password = password
        self._account_identifier = account_identifier
        # Store SQLDatabase objects with (database, schema) as the key
        self._databases: Dict[str, SnowflakeDatabase] = {}
        # Keep the dialect attribute for compatibility with SQLDatabase object
        self.dialect = "snowflake"
        self.metadata_parser = MetadataParser(
            file_path=local_index_file_path,
            annotation_file_path=index_annotation_file_path,
            verbose=verbose,
        )
        self._flipside = (
            Flipside(flipside_api_key) if flipside_api_key is not None else None
        )
        self._shroomdk = (
            ShroomDK(shroomdk_api_key) if shroomdk_api_key is not None else None
        )

    @property
    def flipside(self):
        if self._flipside is None:
            raise AttributeError(
                "Flipside attribute is not found in the SnowflakeContainer; please double check whether your FLIPSIDE_API_KEY is set correctly in the .env file"
            )
        return self._flipside

    @property
    def shroomdk(self):
        if self._shroomdk is None:
            raise AttributeError(
                "Shroomdk attribute is not found in the SnowflakeContainer; please double check whether your SHROOMDK_API_KEY is set correctly in the .env file"
            )
        return self._shroomdk

    def _create_engine(self, database: str) -> Engine:
        """Create a Snowflake engine with the given database
        We do not need to specify the schema here, since we can specify it when we create the SQLDatabase object
        """
        # create the base Snowflake URL
        logger.debug(f"Creating Snowflake engine for {database=}")
        engine_url = (
            f"snowflake://{self._user}:{self._password}@{self._account_identifier}/"
        )
        engine_url += f"{database}/"
        engine = create_engine(
            engine_url,
            connect_args={
                "client_session_keep_alive": True,
            },
            # echo=True,
        )
        logger.debug(f"to return {engine=}")
        return engine

    def get_database(self, database: str, schema: str) -> SnowflakeDatabase:
        key = f"{database}.{schema}"

        if key in self._databases:
            return self._databases[key]
        else:
            try:
                engine = self._create_engine(database)
                snowflake_database = SnowflakeDatabase(engine=engine, schema=schema)
                logger.debug(f"Created {snowflake_database=}")
                # sql_database = SQLDatabase(engine=engine, schema=schema)
                self._databases[key] = snowflake_database
                return snowflake_database
            except Exception as e:
                raise ValueError(
                    f"Error getting snowflake database for {key}: {str(e)}"
                )

    def run_no_throw(
        self,
        command: str,
        database: str,
        schema: str,
        fetch: str = "all",
        return_string: bool = True,
    ) -> Union[str, CursorResult]:
        """
        submit a query to Snowflake by providing a database and a schema
        """
        try:
            return self.get_database(database=database, schema=schema).run_no_throw(
                command=command, fetch=fetch, return_string=return_string
            )
        except Exception as e:
            return f"Error snowflake container running {command=} on {database}.{schema}: {str(e)}"

from agents import FunctionTool, function_tool
import psycopg2
from typing_extensions import TypedDict, Any
import os


@function_tool
def execute_query(query: str) -> str:
    """Execute a query on a PostgreSQL database using psycopg2.

    Args:
        query: The SQL query to execute.
    """
    try:
        # Connect to PostgreSQL database
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        
        ## don't allow delete- if the query is a delete, raise an error
        if query.strip().lower().startswith('delete'):
            raise ValueError("Delete operations are not allowed.")
        
        ## don't allow drop- if the query is a drop, raise an error
        if query.strip().lower().startswith('drop'):
            raise ValueError("Drop operations are not allowed.")
        
        # Execute the query
        cursor.execute(query)
        connection.commit()
        
        # Log and return results if SELECT query
        if query.strip().lower().startswith('select'):
            results = cursor.fetchall()
            return str(results)
        return "Query executed successfully."
        
    except (Exception, psycopg2.Error) as error:
        return f"Error: {str(error)}"
        
    finally:
        if connection:
            cursor.close()
            connection.close()



def execute_query_non_agent(query: str, values: str) -> str:
    """Execute a query on a PostgreSQL database using psycopg2.

    Args:
        query: The SQL query to execute.
    """
    try:
        # Connect to PostgreSQL database
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        
        ## don't allow delete- if the query is a delete, raise an error
        if query.strip().lower().startswith('delete'):
            raise ValueError("Delete operations are not allowed.")
        
        ## don't allow drop- if the query is a drop, raise an error
        if query.strip().lower().startswith('drop'):
            raise ValueError("Drop operations are not allowed.")
        
        # Execute the query
        print(query, values)
        cursor.execute(query, values)
        connection.commit()
        
        # Log and return results if SELECT query
        if query.strip().lower().startswith('select'):
            results = cursor.fetchall()
            return str(results)
        return "Query executed successfully."
        
    except (Exception, psycopg2.Error) as error:
        return f"Error: {str(error)}"
        
    finally:
        if connection:
            cursor.close()
            connection.close()

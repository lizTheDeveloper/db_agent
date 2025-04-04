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

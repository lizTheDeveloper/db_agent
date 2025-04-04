from agents import Agent, Runner
import asyncio
import random
import os

from db import execute_query

# agent = Agent(
#     name="Customer Service Bot",
#     instructions="""
# Your role is to handle a few specific email triage tasks:
 
# - When students email me asking where the link to class is, you'll respond with the most up-to-date Gather Town link
# - When students ask about the curriculum you'll respond with the most up-to-date curriculum link
# - If they ask when class is, look up their email, find out what class they're in and then send them a class schedule for the next classes that they're in 
# - If they ask what class they should start with, ask them a follow-up question about their background to see if they need to go through the beginning classes or if they can jump straight in
#     """,
# )

import json

from typing_extensions import TypedDict, Any

from agents import Agent, FunctionTool, RunContextWrapper, function_tool


class Location(TypedDict):
    lat: float
    long: float

@function_tool  
async def fetch_weather(location: Location) -> str:
    
    """Fetch the weather for a given location.

    Args:
        location: The location to fetch the weather for.
    """
    # In real life, we'd fetch the weather from a weather API
    return random.choice(["sunny", "rainy", "cloudy"])


@function_tool(name_override="fetch_data")  
def read_file(ctx: RunContextWrapper[Any], path: str, directory: str | None = None) -> str:
    """Read the contents of a file.

    Args:
        path: The path to the file to read.
        directory: The directory to read the file from.
    """
    with open(path, "r") as file:
        return file.read()
    
@function_tool
def list_files(directory: str) -> list[str]:
    """List the files in a
    directory.
    """

    return os.listdir(directory)

@function_tool
def write_file(path: str, content: str) -> None:
    with open(path, "w") as file:
        file.write(content)


agent = Agent(
    name="Assistant",
    tools=[read_file, list_files, write_file, execute_query],
    instructions="""
You are a helpful assistant. You can read files, list files, and write files, and connect to a database.
If asked to respond to an email, check the database's links table for details you might need.
"""
)

async def main():
    # result = await Runner.run(agent, "Can you write python file with a function that will allow me to connect to a postgres database using psycopg2 and issue any query i send, then save the file as db.py? Please look at main.py first, and create the function as a tool, similar to the other examples in main.py")
    # result = await Runner.run(agent, "Can you connect to the database, there is a table called links with the columns id, name, and url, please insert a row with the name 'gather town' and the url 'https://gather.town/app/xyz123'. Please execute this as at least two separate queries. If you encounter troubles, you can read the db.py file to see how the connection is made, and potentially debug and rewrite the tool so that it works.")
    # result = await Runner.run(agent, "Can you add a description field to the links table for additional context?")
    # result = await Runner.run(agent, "Can you add 'this is the link to class if students ask' for the gather town link in the links table?")
    result = await Runner.run(agent, "Can you respond to this user's email: 'Hi, I was wondering if you could send me the link to class? Thanks!'")
    print(result.final_output)
    


if __name__ == "__main__":
    asyncio.run(main())
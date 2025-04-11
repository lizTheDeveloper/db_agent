from agents import Agent, Runner, WebSearchTool
from agents.mcp import MCPServerStdio
import asyncio
import random
import os
from openai import OpenAI
client = OpenAI()

from db import execute_query, execute_query_non_agent

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
        
        
@function_tool
def save_document(title: str, content: str, metadata: str) -> str:
    response = client.embeddings.create(
        input=content,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    embedding = json.dumps(embedding)
    ## save it to the database
    query = f"INSERT INTO documents (title, content, embeddings, metadata) VALUES (%s, %s, %s, %s)"
    
    execute_query_non_agent(query,values=(title, content, embedding, metadata))
    return "Document saved successfully."

@function_tool
def embeddings_query_database(query: str) -> str:
    print(query)
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    embedding = json.dumps(embedding)
    
    ## query the database using the embeddings
    sql_query = f"SELECT *, (embeddings <-> %s) as distance FROM documents ORDER BY embeddings <-> %s LIMIT 1"
    results = execute_query_non_agent(sql_query, embedding)
    print(results)
    return results
    


agent = Agent(
    name="Assistant",
    tools=[execute_query, save_document, embeddings_query_database, WebSearchTool()],
    instructions="""
You are a helpful assistant. You can read files, list files, and write files, and connect to a database.
You can save documents to the database, which will be stored in a table called documents, along with the embeddings of the document.
If asked to respond to an email, check the database's links table for details you might need.
"""
)


async def main():
    async with MCPServerStdio(
    params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", '/Users/annhoward/intro_to_agents_spr_2025/meshtastic'],
        }
    ) as server:

            agent.mcp_servers.append(server)

    # result = await Runner.run(agent, "Can you write python file with a function that will allow me to connect to a postgres database using psycopg2 and issue any query i send, then save the file as db.py? Please look at main.py first, and create the function as a tool, similar to the other examples in main.py")
    # result = await Runner.run(agent, "Can you connect to the database, there is a table called links with the columns id, name, and url, please insert a row with the name 'gather town' and the url 'https://gather.town/app/xyz123'. Please execute this as at least two separate queries. If you encounter troubles, you can read the db.py file to see how the connection is made, and potentially debug and rewrite the tool so that it works.")
    # result = await Runner.run(agent, "Can you add a description field to the links table for additional context?")
    # result = await Runner.run(agent, "Can you add 'this is the link to class if students ask' for the gather town link in the links table?")
    # result = await Runner.run(agent, "Can you respond to this user's email: 'Hi, I was wondering if you could send me the link to class? Thanks!'")
    # result = await Runner.run(agent, "Please create a table called documents, with columns id, title, content, embeddings, and metadata. The embeddings column should be a vector(1536), and the metadata column should be a jsonb object.")
    # result = await Runner.run(agent, "Please save the /Users/annhoward/intro_to_agents_spr_2025/doc2.txt and doc3.txt files to the documents table, with an appropriate title and set metadata to null.")
        # result = await Runner.run(agent, "how many text files are in /Users/annhoward/intro_to_agents_spr_2025/")
            result = await Runner.run(agent, "Please use your mcp server tools to create an index.html, with embeded html and css, that helps people set up meshtastic nodes at gardens in their communuties. Search the web using your web search tool for information on meshtastic, and use your best judgement to create a simple, but effective landing page. Iterate on the landing page a few times (at least 5 times), until it's really non-trivial, and contains all the information someone might need to buy, build, set up, and configure a meshtastic node to help their community be resilient against natrual disasters and communication interruptions. At the end, please reply with the full file path of the index.html file.")
            
            while True:
                print(result.final_output)
                user_input = input("Please provide any additional information you'd like injected into the prompt.")
                result = await Runner.run(agent, f"""
                                          Please act as an expert educational website critic. 
                                          Find any unfinished elements, or things that could be clarified or expanded, and address them by fixing them. 
                                          Please iterate on the {result.final_output} file again. 
                                          Always include the file path in your final result so the next iteration knows where the file is.
                                          When you are absolutely sure that there is no more helpful information you can provide (including community resources, and other open-source projects that integrate with Meshtastic) please reply only with 'No changes made.' 
                                          Never ask for confirmation to make the changes to a file, always just make the changes. The user will not be able to see your inputs.
                                          Never reply with 'No changes made.' if you have not yet performed a web search.
                                          {user_input}
                                          """
                )
                if "No changes made." in result.final_output:
                    break
                asyncio.sleep(60 * 20)
    print(result.final_output)
    


if __name__ == "__main__":
    asyncio.run(main())
    
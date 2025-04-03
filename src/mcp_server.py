from mcp.server.fastmcp import FastMCP

mcp = FastMCP("advertisements")


@mcp.tool()
async def list_advertisements() -> str:
    """
    List all advertisements in the database.

    This asynchronous function retrieves all advertisement records from the database and returns them as a JSON-formatted string.
    
    Returns:
        str: A JSON-formatted string representing a list of advertisements. 
             If no advertisements are found, the function returns an empty JSON array "[]".
    """
    return "[]"


@mcp.tool()
async def add_advertisements(name: str, title: str) -> str:
    """
    Add an advertisement to the database.

    Args:
        name (str): The name of the advertisement.
        title (str): The title of the advertisement.

    Returns:
        str: A confirmation message indicating that the advertisement was added successfully.
    """
    return f"Added advertisement {name} with title {title}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")

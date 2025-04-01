from mcp.server.fastmcp import FastMCP


mcp = FastMCP("advertisements")


@mcp.tool()
async def list_advertisements() -> str:
    """
    List all advertisements in the database.
    """

    return "[]"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")

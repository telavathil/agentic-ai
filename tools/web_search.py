from typing import Dict, Any
import json
from googleapiclient.discovery import build

from config.settings import settings

from .base import Tool

class WebSearch(Tool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Performs web searches using Google Custom Search API"
        )
        self.api_key = settings.GOOGLE_API_KEY
        self.search_engine_id = settings.SEARCH_ENGINE_ID

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to execute"
                }
            },
            "required": ["query"]
        }

    def get_example(self) -> str:
        return json.dumps({"query": "latest developments in AI"})

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute a web search using Google Custom Search API."""
        try:

            # Get the search query from parameters
            query = parameters.get("query")
            if not query:
                return {"error": "No search query provided"}

            # Create a service object for the Custom Search API
            service = build(
                "customsearch", "v1",
                developerKey=self.api_key
            )

            # Execute the search
            result = service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=5  # Number of results to return
            ).execute()

            # Format the results
            formatted_results = []
            for item in result.get("items", []):
                formatted_results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })

            return {
                "results": formatted_results
            }

        except (AttributeError, TypeError) as e:
            return {"error": f"Search failed: {str(e)}"}

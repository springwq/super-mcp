from mcp.server.fastmcp import FastMCP, Context
from datetime import datetime, timedelta
import httpx
import os
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants and configuration
JAMPP_AUTH_URL = "https://auth.jampp.com/v1/oauth/token"
JAMPP_API_URL = "https://reporting-api.jampp.com/v1/graphql"

class JamppClient:
    """Client for interacting with the Jampp Reporting API."""

    def __init__(self):
        self.client_id = os.getenv("JAMPP_CLIENT_ID")
        self.client_secret = os.getenv("JAMPP_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError("Jampp API credentials not found in environment variables")

        self.auth_url = JAMPP_AUTH_URL
        self.api_url = JAMPP_API_URL
        self.access_token = None
        self.token_expiry = None

    async def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        # Check if we have a valid token
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        # Request a new token
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.auth_url, data=data)
            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data["access_token"]
            # Set expiry time with a small buffer
            self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"] - 60)

            return self.access_token

    async def execute_graphql(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL query against the Jampp API."""
        token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "variables": variables
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

# Initialize the MCP server
mcp = FastMCP("jampp-api", dependencies=["httpx", "python-dotenv"])

# Initialize Jampp client as a global variable
jampp_client = JamppClient()

# Tool to get campaign spend data
@mcp.tool()
async def get_campaign_spend(
    ctx: Context,
    from_date: str,
    to_date: str,
    campaign_id: Optional[int] = None
) -> str:
    """
    Get spend per campaign for a specific date range.

    Args:
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        campaign_id: Optional ID of the campaign to query

    Returns:
        JSON string with campaign spend data
    """
    global jampp_client

    # Define the GraphQL query
    query = """
    query spendPerCampaign($from: DateTime!, $to: DateTime!, $campaignId: Int) {
      spendPerCampaign: pivot(
        from: $from,
        to: $to,
        filter: {campaignId: {equals: $campaignId}}
      ) @include(if: $campaignId != null) {
        results {
          campaignId
          campaign
          spend
        }
      }
    }
    """

    # 如果没有指定campaign_id，使用不带过滤器的查询
    if campaign_id is None:
        query = """
        query spendPerCampaign($from: DateTime!, $to: DateTime!) {
          spendPerCampaign: pivot(
            from: $from,
            to: $to
          ) {
            results {
              campaignId
              campaign
              spend
            }
          }
        }
        """

    variables = {
        "from": from_date,
        "to": to_date,
        "campaignId": campaign_id
    }

    try:
        result = await jampp_client.execute_graphql(query, variables)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching campaign spend: {str(e)}"

# Tool to get daily spend for a specific campaign
@mcp.tool()
async def get_campaign_daily_spend(
    ctx: Context,
    from_date: str,
    to_date: str,
    campaign_id: int,
    timezone: str = "UTC"
) -> str:
    """
    Get daily spend for a specific campaign.

    Args:
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        campaign_id: ID of the campaign to query
        timezone: Timezone for the report (default: UTC)

    Returns:
        JSON string with daily spend data
    """
    global jampp_client

    # Define the GraphQL query
    query = """
    query spendPerDay($from: DateTime!, $to: DateTime!, $campaignId: Int!, $timezone: String) {
      spendPerDay: pivot(
        from: $from,
        to: $to,
        filter: {
          campaignId: {
            equals: $campaignId
          }
        },
        context: {
          sqlTimeZone: $timezone
        }
      ) {
        results {
          date(granularity: DAILY)
          spend
        }
      }
    }
    """

    variables = {
        "from": from_date,
        "to": to_date,
        "campaignId": campaign_id,
        "timezone": timezone
    }

    try:
        result = await jampp_client.execute_graphql(query, variables)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching daily spend: {str(e)}"

# Tool to get comprehensive performance metrics
@mcp.tool()
async def get_campaign_performance(
    ctx: Context,
    from_date: str,
    to_date: str,
    campaign_id: Optional[int] = None,
    timezone: str = "UTC"
) -> str:
    """
    Get comprehensive performance metrics for campaigns.

    Args:
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        campaign_id: Optional ID of a specific campaign to query
        timezone: Timezone for the report (default: UTC)

    Returns:
        JSON string with performance metrics
    """
    global jampp_client

    # Define the GraphQL query with filter for specific campaign
    query = """
    query campaignPerformance($from: DateTime!, $to: DateTime!, $campaignId: Int, $timezone: String) {
      performance: pivot(
        from: $from,
        to: $to,
        filter: {campaignId: {equals: $campaignId}},
        context: {
          sqlTimeZone: $timezone
        }
      ) @include(if: $campaignId != null) {
        results {
          campaignId
          campaign
          impressions
          clicks
          ctr
          spend
          cpc
          cpm
          installs
          installsCpi
          installsCvr
        }
        totals {
          impressions
          clicks
          spend
          installs
        }
      }
    }
    """

    # 如果没有指定campaign_id，使用不带过滤器的查询
    if campaign_id is None:
        query = """
        query campaignPerformance($from: DateTime!, $to: DateTime!, $timezone: String) {
          performance: pivot(
            from: $from,
            to: $to,
            context: {
              sqlTimeZone: $timezone
            }
          ) {
            results {
              campaignId
              campaign
              impressions
              clicks
              ctr
              spend
              cpc
              cpm
              installs
              installsCpi
              installsCvr
            }
            totals {
              impressions
              clicks
              spend
              installs
            }
          }
        }
        """

    variables = {
        "from": from_date,
        "to": to_date,
        "campaignId": campaign_id,
        "timezone": timezone
    }

    try:
        result = await jampp_client.execute_graphql(query, variables)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching campaign performance: {str(e)}"

# Tool to create an asynchronous report
@mcp.tool()
async def create_async_report(
    ctx: Context,
    from_date: str,
    to_date: str,
    dimensions: List[str],
    metrics: List[str]
) -> str:
    """
    Create an asynchronous report for larger data sets.

    Args:
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        dimensions: List of dimensions to include (e.g. ["campaignId", "campaign"])
        metrics: List of metrics to include (e.g. ["impressions", "clicks", "spend"])

    Returns:
        JSON string with the async report ID and status
    """
    global jampp_client

    # Define the GraphQL mutation
    mutation = """
    mutation createAsyncPivot($from: DateTime!, $to: DateTime!, $dimensions: [String!]!, $metrics: [String!]!) {
      createAsyncPivot(
        Input: {
          from: $from,
          to: $to,
          dimensions: $dimensions,
          metrics: $metrics
        }
      ) {
        asyncPivot {
          id
          status
        }
      }
    }
    """

    variables = {
        "from": from_date,
        "to": to_date,
        "dimensions": dimensions,
        "metrics": metrics
    }

    try:
        result = await jampp_client.execute_graphql(mutation, variables)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating async report: {str(e)}"

# Tool to check the status of an asynchronous report
@mcp.tool()
async def get_async_report_status(
    ctx: Context,
    report_id: str
) -> str:
    """
    Check the status of an asynchronous report.

    Args:
        report_id: ID of the async report to check

    Returns:
        JSON string with the report status
    """
    global jampp_client

    # Define the GraphQL query
    query = """
    query getAsyncPivotStatus($id: String) {
      asyncPivot(id: $id) {
        id
        status
        createdAt
        updatedAt
      }
    }
    """

    variables = {
        "id": report_id
    }

    try:
        result = await jampp_client.execute_graphql(query, variables)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error checking report status: {str(e)}"

# Tool to get the results of a completed asynchronous report
@mcp.tool()
async def get_async_report_results(
    ctx: Context,
    report_id: str
) -> str:
    """
    Get the results of a completed asynchronous report.

    Args:
        report_id: ID of the async report to retrieve

    Returns:
        JSON string with the report results
    """
    global jampp_client

    # Define the GraphQL query
    query = """
    query getAsyncPivotResults($id: String) {
      asyncPivot(id: $id) {
        id
        status
        result {
          results
          totals
        }
      }
    }
    """

    variables = {
        "id": report_id
    }

    try:
        result = await jampp_client.execute_graphql(query, variables)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching report results: {str(e)}"

# Tool to get available metrics and dimensions
@mcp.tool()
async def get_available_metrics_and_dimensions(
    ctx: Context
) -> str:
    """
    Get a list of all available metrics and dimensions for reporting.

    Returns:
        JSON string with available metrics and dimensions
    """
    # This is a static list based on the API documentation
    # In a real implementation, you might want to fetch this dynamically if the API supports it

    metrics = [
        "impressions", "clicks", "eviews", "cpc", "cpm", "ctr", "spend", "wins",
        "bidToWinRate", "uniqueImpressions", "uniqueClicks", "skadAssistedInstalls",
        "simps", "sourceViewa", "uniqueEvents", "events", "assistedEvents",
        "assistedEventValue", "eventValue", "eventsCpa", "eventsRoas", "eventsIte",
        "eventsRate", "installs", "installsCpi", "installsCvr", "installsIti",
        "assistedInstalls", "uniqueEventsCpa", "vtaShare"
    ]

    dimensions = [
        "date", "campaignId", "campaign", "app", "platform", "country", "site",
        "adType", "adSize", "status", "bidType", "bidStrategy"
    ]

    result = {
        "metrics": metrics,
        "dimensions": dimensions
    }

    return json.dumps(result, indent=2)

# Run the server when executed directly
if __name__ == "__main__":
    mcp.run()

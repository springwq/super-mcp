import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from servers.redshift_query import query_redshift

mcp = FastMCP("Spend Rate")

@mcp.tool()
def spend_rate_by_date(click_url_id: int, date: str) -> dict:
    """Get the Gross CPI and Net CPI from the redshift database according to the corresponding date and click_url_id"""
    
    sql = f"""
    SELECT gross_cpi, net_cpi 
    FROM click_url_infos
    WHERE event_date = '{date}'
    AND click_url_id = {click_url_id}
    """

    results = query_redshift(sql)
    
    if results:
        return results[0]
    else:
        return {"gross_rate": None, "net_rate": None}  

if __name__ == "__main__":
    mcp.run()

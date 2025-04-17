import os
import httpx
from typing import Dict, Optional, List
from mcp.server import FastMCP
from prance import ResolvingParser
from urllib.parse import urlparse


class OpenAPIer:
    def __init__(self, spec_url: str):
        """
        初始化 OpenAPI 解析工具
        :param spec_url: OpenAPI 规范文件路径或 URL（支持.json/.yaml）
        """
        self.parser = ResolvingParser(spec_url, backend='openapi-spec-validator')
        self.base_url = self.parser.specification.get('servers', [{}])[0].get('url', '')
        self.interfaces = self._parse_interfaces()
        self.host_domain = "{0}://{1}".format(*urlparse(spec_url)[:2])

    def _parse_interfaces(self) -> List[Dict]:
        """解析 OpenAPI 文档获取所有接口信息"""
        interfaces = []
        paths = self.parser.specification.get('paths', {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    interfaces.append({
                        'path': path,
                        'method': method.upper(),
                        'parameters': details.get('parameters', []),
                        'summary': details.get('summary', 'No summary'),
                        'operationId': details.get('operationId', '')
                    })
        return interfaces


# Initialize FastMCP server
mcp = FastMCP("mcp-server-swagger")

# 设置环境变量
# os.environ["OPEN_API_URL"] = "https://petstore3.swagger.io/api/v3/openapi.json"

# 获取环境变量
open_api_url = os.getenv('OPEN_API_URL')

# Initialize OpenAPIer instance globally
OPENER = OpenAPIer(open_api_url)


@mcp.tool()
async def call_api(
        url: str,
        method: str,
        query_params: Optional[Dict] = None,
        body: Optional[Dict] = None,
        headers: Optional[Dict] = None
):
    """Make an HTTP request or call to an external API.

    Args:
        url (str): [REQUIRED] The target URL for the API request. Example: "https://api.example.com/data"
        method (str): [REQUIRED] HTTP method to use. Must be one of: GET, POST, PUT, DELETE.
        query_params (dict): URL query parameters. Example: {"page": 1, "limit": 10}
        body (dict): Request body for POST/PUT. Example: {"name": "John", "age": 30}
        headers (dict): Custom headers. Example: {"Authorization": "Bearer token"}

    Returns:
        dict: API response in JSON format
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method.upper(),
                url=url,
                params=query_params or {},
                json=body or {},
                headers=headers or {}
            )

            response.raise_for_status()
            return response.json()
        except Exception as e:
            return str(e)


@mcp.tool()
async def get_all_interfaces(verbose: bool = False):
    """Get all API interfaces from OpenAPI document.

    Args:
        verbose: 是否显示详细信息 (默认为False)

    Returns:
        list: 当verbose=True时返回完整接口详细信息，否则返回包含Function摘要的列表
    """

    if verbose:
        return OPENER.interfaces
    return [{'Function': item['summary']} for item in OPENER.interfaces]


@mcp.tool()
async def get_detail_interface(summary: str) -> list[dict]:
    """
    Get the detail of an API interface based on its summary.

    Args:
        summary (str): The summary description of the interface.

    Returns:
        list[dict]: A list of matching interfaces with their host and function details.
    """

    # Construct the base URL
    base_url = f"{OPENER.host_domain.rstrip('/')}/{OPENER.base_url.lstrip('/')}"

    # Filter and return matching items using fuzzy matching (substring check)
    matching_items = [
        {'Host': base_url, 'Function': item}
        for item in OPENER.interfaces
        if summary.lower() in item.get('summary', '').lower()
    ]

    return matching_items


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

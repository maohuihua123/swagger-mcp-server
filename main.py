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
        self.host_domain = "{0}://{1}".format(*urlparse(spec_url)[:2])
        self.interfaces = self._parse_interfaces()

    def _parse_interfaces(self) -> List[Dict]:
        """解析 OpenAPI 文档获取所有接口信息"""
        interfaces = []
        paths = self.parser.specification.get('paths', {})
        # Construct the base URL
        base_url = f"{self.host_domain.rstrip('/')}/{self.base_url.lstrip('/')}"

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    # 根据base_url与path构造接口的url
                    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
                    # 提取 requestBody 信息
                    request_body = details.get('requestBody', {})
                    request_body_info = None
                    if request_body:
                        # 解析通用约束和 content
                        request_body_info = {
                            "required": request_body.get("required", False),
                            "content": {}
                        }
                        # 遍历所有支持的媒体类型（如 application/json）
                        for content_type, content_def in request_body.get("content", {}).items():
                            # 提取 schema（可能包含直接定义或已解析的 $ref）
                            schema = content_def.get("schema", {})
                            request_body_info["content"][content_type] = schema
                    # 构造接口信息
                    interface = {
                        'url': url,
                        'method': method.upper(),
                        'summary': details.get('summary', 'No summary'),
                        'operationId': details.get('operationId', '')
                    }

                    # 如果 parameters 不为空，则添加到接口信息
                    parameters = details.get('parameters', [])
                    if parameters:
                        interface['parameters'] = parameters

                    # 如果 request_body_info 不为 None，则添加到接口信息
                    if request_body_info:
                        interface['requestBody'] = request_body_info

                    # 将接口描述添加到List中
                    interfaces.append(interface)
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
    """
    Retrieve all API interfaces from the OpenAPI document.

    Args:
        verbose (bool): Whether to display detailed information (default is False).

    Returns:
        list: If verbose=True, returns the complete interface details.
              Otherwise, returns a list containing only the function summaries.
    """
    if verbose:
        return OPENER.interfaces
    return [{'Function': item['summary']} for item in OPENER.interfaces]


@mcp.tool()
async def get_detail_interface(summary: str) -> dict | None:
    """
    Retrieve the details of the first API interface that matches the given summary.

    Args:
        summary (str): A substring to search for in the interface summary description.

    Returns:
        dict: The first matching interface with its details.
              If no match is found, returns None.
    """
    # Iterate through the available interfaces and perform case-insensitive fuzzy matching
    for item in OPENER.interfaces:
        if summary.lower() in item.get('summary', '').lower():
            return item

    # Return None if no matching interface is found
    return None


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

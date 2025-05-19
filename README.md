# swagger-mcp-server
Swagger-MCP-Server 基于 Swagger 文档作为接口约束标准，允许用户通过自然语言方式与大模型（如 ChatGPT）对话，触发网站接口调用，完成数据的查询、分析和处理，具备即席分析、实时反馈等特点，为用户提供了全新的体验。

## 1.使用配置

### 1.1.安装Cherry Studio

官网网站：[https://cherry-ai.com/](https://cherry-ai.com/)

### 1.2.拉取项目

```
https://github.com/maohuihua123/swagger-mcp-server.git
```

### 1.3.配置MCP-Server

> [!NOTE]
>
> 路径修改为自己的本地项目路径：例如`c:/Users/Administrator/Desktop/swagger-mcp-server`
>
> Swagger文件链接需要可访问：例如`http://localhost:8080/v3/api-docs/openapi.json`

```json
{
  "mcpServers": {
    "ct8e9lwgcZCYAp_c5UErc": {
      "name": "swagger-mcp",
      "type": "stdio",
      "isActive": true,
      "registryUrl": "",
      "command": "uv",
      "args": [
        "--directory",
        "c:/Users/Administrator/Desktop/swagger-mcp-server",
        "run",
        "main.py"
      ],
      "env": {
        "OPEN_API_URL": "http://localhost:8080/v3/api-docs/openapi.json"
      }
    }
  }
}
```

## 2.使用案例

### 2.1.查看接口列表

`告诉我网站有哪些功能？` `告诉我有哪些功能接口？`

### 2.2.调用具体接口

> [!TIP]
>
> 在输入指令时，让大模型先调用接口详细工具，从而获得准确的接口URL、接口参数等，再发起调用

`调用创建用户接口，创建新用户，用户名为张三，邮箱为123456@qq.com；在调用之前，先查询接口详细信息`

### 2.3.生成接口测试计划

`你是一位资深软件测试工程师，结合网站的接口文档，请基于等价类划分、边界值分析等测试设计方法，自动生成测试计划、测试用例。`

### 2.4.自动化接口测试

`基于制定的测试计划，对网站接口进行自动化测试调用，并输出最终测试报告。`

## 3.想法来源

> [!TIP]
>
> MCP协议解决的是大模型无法随意调用服务的问题，如果能通过清晰的接口定义，让大模型可以自己构造参数调用服务，是否可以减少MCP-Server的开发？

* 基于 Swagger 文档作为约束标准，能够快速适配不同的网站和服务，无需为每个网站单独开发集成逻辑。
* 通过接口调用获取数据后，结合大模型的分析能力，快速生成数据洞察、图表或预测结果，实现即席分析，实时反馈。
* 基于大模型的自然语言交互界面，未来是否能够作为传统UI界面的补充，从而为用户提供了新的体验？

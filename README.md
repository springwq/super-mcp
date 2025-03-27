# Direct Spend Automations

- 这个项目是一个 Direct Spend 自动录入系统，支持从 FeedMob 系统和 Parter 系统分别获取 Gross Spend 和 Net Spend
- 该系统集成了 AWS Bedrock 的 Claude 3.5 模型，并使用 LangChain 和 MCP 适配器进行数据处理和分析。


## 技术栈

- Python 3.11+
- AWS Bedrock (Claude 3.5 Sonnet)
- LangGraph & LangChain
- LangChain AWS 集成
- LangChain MCP 适配器
- MCP 1.2.0+
- HTTPX
- Python-dotenv

## 主要功能

### 通过 MCP Server 从 Partner (Jampp/Kayzen) 获取 Spend 数据

- 智能查询重试机制，支持多种查询策略：
  - 自动修正未来日期查询
  - 动态扩展查询时间范围
  - 自动切换到最近可用数据
- 集成了多个 MCP Server：
  - Jampp MCP Server
  - Kayzen MCP Server
- 自动数据验证


## 安装说明

1. 确保安装了 Python 3.11 或更高版本

2. 克隆仓库：
```bash
git clone [repository-url]
cd direct_spend_automations
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 环境变量配置：
- 复制 `.env.example` 到 `.env`（如果存在）
- 配置以下必要的环境变量：
  - AWS Bedrock 访问凭证
  - 其他必要的服务配置


## 许可证

MIT

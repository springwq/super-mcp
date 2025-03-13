# Direct Spend Automations

这个项目是一个自动化支出分析系统，专注于广告活动（Campaign）支出数据的智能查询和分析。该系统集成了 AWS Bedrock 的 Claude 3.5 模型，并使用 LangChain 和 MCP 适配器进行数据处理和分析。

## 项目结构

```
.
├── clients/            # 客户端代码
│   └── calc_spend.py   # 智能支出查询客户端
├── servers/            # 服务器端代码
│   └── jampp_mcp_server.py  # Jampp MCP 服务器实现
├── requirements.txt    # Python 依赖
└── .env               # 环境变量配置
```

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

### Campaign Spend 查询工具

- 智能查询重试机制，支持多种查询策略：
  - 自动修正未来日期查询
  - 动态扩展查询时间范围
  - 自动切换到最近可用数据
- 集成了多个 MCP Server：
  - Jampp MCP Server
  - Time Server
- 自动数据验证
- 交互式命令行界面

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

## 使用指南

### 运行支出查询工具

```bash
python clients/calc_spend.py
```

支持的查询示例：
- "查询昨天的 campaign spend"
- "获取本周支出最高的 campaign"
- "分析最近7天的广告支出趋势"

### 启动 Jampp MCP 服务器

```bash
python servers/jampp_mcp_server.py
```

## 查询重试策略

系统会在以下情况下自动调整查询策略：

1. 初始查询：使用用户原始查询
2. 第一次重试：扩大查询范围到目标日期前后 3 天
3. 第二次重试：获取最近 7 天的数据
4. 第三次重试：获取当月汇总数据
5. 最后尝试：获取最新可用的数据

## 最佳实践

1. 查询优化
   - 使用具体的时间范围进行查询
   - 避免查询未来日期
   - 合理使用聚合查询

2. 监控和维护
   - 监控 MCP 服务器运行状态
   - 检查查询响应时间
   - 定期更新依赖包

3. 安全建议
   - 妥善保管 AWS 凭证
   - 定期更新访问密钥
   - 遵循最小权限原则

## 故障排除

- 如果查询返回空结果，系统会自动尝试其他查询策略
- MCP 服务器连接问题，检查服务是否正常运行
- AWS Bedrock 访问问题，验证凭证配置是否正确

## 许可证

MIT

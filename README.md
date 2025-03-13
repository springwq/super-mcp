# Direct Spend Automations

这个项目是一个自动化支出分析系统，用于跟踪和分析直接支出数据。该系统集成了 AWS Redshift 数据库，并使用 LangChain 和 MCP 适配器进行数据处理和分析。

## 项目结构

```
.
├── clients/            # 客户端代码
│   └── calc_spend.py   # 支出计算客户端
├── servers/            # 服务器端代码
│   ├── jampp_mcp_server.py  # MCP 服务器实现
│   ├── redshift_query.py    # Redshift 查询处理
│   └── spend_rate.py        # 支出率计算
├── requirements.txt    # Python 依赖
└── .env               # 环境变量配置
```

## 技术栈

- Python 3.11+
- LangGraph & LangChain
- LangChain AWS 集成
- LangChain MCP 适配器
- PostgreSQL (psycopg2-binary)
- MCP 1.2.0+
- HTTPX
- Python-dotenv

## 主要功能

- 自动化支出数据收集和分析
- Redshift 数据库查询和集成
- 支出率实时计算和监控
- AWS 服务集成
- MCP 服务器实现

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
  - AWS 相关配置
  - Redshift 连接信息
  - MCP 服务器配置

## 使用指南

### 运行支出计算

```bash
python clients/calc_spend.py
```

### 启动 MCP 服务器

```bash
python servers/jampp_mcp_server.py
```

### 执行 Redshift 查询

```bash
python servers/redshift_query.py
```

### 计算支出率

```bash
python servers/spend_rate.py
```

## 最佳实践

1. 数据库操作
   - 定期检查 Redshift 连接状态
   - 优化查询性能
   - 定期备份重要数据

2. 监控和维护
   - 监控 MCP 服务器运行状态
   - 检查日志文件
   - 定期更新依赖包

3. 安全建议
   - 妥善保管环境变量和密钥
   - 定期更新访问凭证
   - 遵循最小权限原则

## 故障排除

- 如果遇到数据库连接问题，检查 `.env` 文件中的配置
- MCP 服务器异常时，查看日志并确保端口未被占用
- 支出计算异常时，验证输入数据格式是否正确

## 许可证

MIT

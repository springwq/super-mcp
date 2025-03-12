# Direct Spend Automations

这个项目是一个自动化支出分析系统，用于跟踪和分析直接支出数据。

## 项目结构

```
.
├── clients/            # 客户端代码
│   └── calc_spend.py   # 支出计算客户端
├── servers/            # 服务器端代码
│   ├── redshift_query.py  # Redshift 查询处理
│   └── spend_rate.py      # 支出率计算
├── requirements.txt    # Python 依赖
└── .env               # 环境变量配置
```

## 技术栈

- Python
- LangGraph
- LangChain AWS
- LangChain MCP Adapters
- PostgreSQL (psycopg2)

## 功能特性

- 自动化支出数据收集和分析
- Redshift 数据库集成
- 支出率计算和监控
- AWS 服务集成

## 安装说明

0. 安装 Python 3.11

1. 克隆仓库：
```bash
git clone [repository-url]
cd direct_spend_automations
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
- 复制 `.env.example` 到 `.env`（如果存在）
- 填写必要的环境变量

## 使用方法

### 计算支出

```bash
python clients/calc_spend.py
```

### 查询 Redshift 数据

```bash
python servers/redshift_query.py
```

### 计算支出率

```bash
python servers/spend_rate.py
```

## 注意事项

- 确保已正确配置所有必要的环境变量
- 确保有适当的数据库访问权限
- 定期检查日志以监控系统运行状况

## 维护

- 定期更新依赖包
- 监控系统性能
- 检查数据准确性

## 许可证

MIT

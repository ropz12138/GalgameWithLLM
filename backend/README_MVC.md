# LLM文字游戏 - MVC架构版本

## 📋 项目概述

这是一个基于 **LangGraph** 和 **FastAPI** 的 LLM 驱动文字游戏项目，采用 **MVC三层架构** 设计，提供清晰的分层结构和良好的可维护性。

## 🏗️ 架构设计

### MVC三层架构

```
backend/src/
├── models/          # Model层 - 数据模型
├── controllers/     # Controller层 - 控制器
├── services/        # Service层 - 业务逻辑
├── routers/         # Router层 - 路由定义
├── utils/           # Utils层 - 工具类
└── app.py          # 主应用文件
```

### 架构层次

1. **Model层** (`models/`)
   - 定义数据结构和模型类
   - 为未来数据库交互做准备
   - 包含：`GameStateModel`, `PlayerModel`, `NPCModel`, `MessageModel`

2. **Controller层** (`controllers/`)
   - 处理HTTP请求和响应
   - 调用Service层处理业务逻辑
   - 包含：`GameController`, `DebugController`, `LLMController`

3. **Service层** (`services/`)
   - 实现核心业务逻辑
   - 处理数据转换和格式化
   - 包含：`GameService`, `WorkflowService`, `StateService`, `LLMService`

4. **Router层** (`routers/`)
   - 定义API路由和端点
   - 处理请求参数验证
   - 包含：`game_router`, `debug_router`, `llm_router`

5. **Utils层** (`utils/`)
   - 提供通用工具功能
   - 包含：`ResponseUtils`, `ValidationUtils`, `LoggerUtils`

## 🚀 快速开始

### 环境要求

- Python 3.8+
- FastAPI
- Uvicorn
- LangGraph
- LangChain

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 启动服务

```bash
# 使用新的MVC架构启动脚本
python start_mvc_app.py

# 或者直接运行主应用
cd src
python app.py
```

### 访问服务

- **API文档**: http://localhost:8001/docs
- **ReDoc文档**: http://localhost:8001/redoc
- **健康检查**: http://localhost:8001/health

## 📚 API接口

### 游戏相关接口

- `GET /api/game_state` - 获取游戏状态
- `POST /api/process_action` - 处理玩家行动
- `POST /api/stream_action` - 流式处理玩家行动
- `POST /api/initialize_game` - 初始化游戏
- `GET /api/npc_dialogue_history/{npc_name}` - 获取NPC对话历史
- `POST /api/continue_dialogue/{npc_name}` - 继续与NPC对话

### 调试接口

- `GET /api/debug/workflow_state` - 获取工作流状态
- `GET /api/debug/workflow_info` - 获取工作流信息
- `GET /api/debug/locations` - 获取位置信息
- `GET /api/debug/npc_locations` - 获取NPC位置
- `GET /api/debug/npcs` - 获取NPC信息
- `GET /api/debug/messages` - 获取消息历史
- `POST /api/debug/reset_session` - 重置会话
- `GET /api/debug/all_sessions` - 获取所有会话

### LLM相关接口

- `GET /api/llm/models` - 获取可用模型列表
- `GET /api/llm/test_connection` - 测试LLM连接
- `POST /api/llm/invoke` - 调用LLM
- `POST /api/llm/reset` - 重置LLM实例
- `GET /api/llm/config/{model_name}` - 获取LLM配置

## 🔧 配置说明

### LLM配置

在 `config/config.json` 中配置不同的LLM模型：

```json
{
  "llm": {
    "gemini": {
      "url": "https://generativelanguage.googleapis.com/v1beta/openai/",
      "model": "gemini-2.5-flash-preview-05-20",
      "api_key": "your_api_key"
    },
    "doubao": {
      "url": "https://ark.cn-beijing.volces.com/api/v3",
      "model": "ep-20240710020216-6xdhr",
      "api_key": "your_api_key"
    }
  }
}
```

## 📊 日志系统

项目集成了完整的日志系统，日志文件保存在 `logs/` 目录下：

- `game.log` - 游戏相关日志
- `llm.log` - LLM请求日志
- `api.log` - API请求日志
- `error.log` - 错误日志
- `performance.log` - 性能日志

## 🛡️ 安全特性

- 输入验证和清理
- 统一的错误处理
- 敏感信息隐藏
- 请求日志记录
- 异常捕获和处理

## 🔄 与原有架构的兼容性

新的MVC架构完全兼容原有的API接口，前端无需修改即可使用。主要改进：

1. **清晰的分层结构** - 职责分离，易于维护
2. **统一的错误处理** - 标准化的错误响应格式
3. **完整的日志系统** - 便于调试和监控
4. **数据验证** - 提高系统安全性
5. **工具类支持** - 减少代码重复

## 🚀 部署说明

### 开发环境

```bash
python start_mvc_app.py
```

### 生产环境

```bash
uvicorn src.app:app --host 0.0.0.0 --port 8001 --workers 4
```

## 📝 开发指南

### 添加新的API端点

1. 在 `routers/` 中定义路由
2. 在 `controllers/` 中实现控制器逻辑
3. 在 `services/` 中实现业务逻辑
4. 在 `models/` 中定义数据模型（如需要）

### 添加新的服务

1. 在 `services/` 中创建新的服务类
2. 在 `controllers/` 中调用服务
3. 在 `routers/` 中定义API端点

### 数据验证

使用 `utils/validation_utils.py` 中的验证方法：

```python
from utils.validation_utils import ValidationUtils

# 验证输入
if not ValidationUtils.validate_action(action):
    raise HTTPException(status_code=400, detail="无效的行动")
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 🆘 支持

如有问题，请查看：
- API文档：http://localhost:8001/docs
- 项目Issues
- 项目Wiki 
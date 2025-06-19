# LLM驱动的文字游戏网页

这是一个基于LLM（大型语言模型）驱动的文字游戏网页应用，模拟了一个拍摄园区的互动环境，玩家可以在其中探索不同地点、与NPC角色互动，并通过自然语言输入执行各种行动。

## 项目结构

```
llm_text_game/
├── data/                  # 游戏数据文件
│   ├── characters.py      # NPC角色数据
│   └── locations.py       # 地点和地图数据
├── backend/               # FastAPI后端
│   ├── src/               # 源代码
│   │   ├── api/           # API接口
│   │   ├── core/          # 核心游戏逻辑
│   │   │   └── game_state.py  # 游戏状态管理器
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 服务层
│   │   │   ├── llm_service.py     # LLM服务
│   │   │   └── langchain_tools.py # Langchain工具
│   │   └── main.py        # 主入口文件
│   ├── venv/              # 虚拟环境
│   └── requirements.txt   # 依赖项
├── frontend/              # React前端
│   ├── src/               # 源代码
│   │   ├── App.tsx        # 主应用组件
│   │   └── App.css        # 样式文件
│   └── ...                # 其他React项目文件
├── todo.md                # 项目任务列表
└── README.md              # 项目说明文档
```

## 主要功能

1. **动态游戏世界**：基于角色和地点数据，构建了一个可交互的拍摄园区世界。
2. **LLM驱动的交互**：玩家可以通过自然语言输入与游戏世界互动，LLM Agent会解析玩家意图并驱动游戏进展。
3. **NPC互动**：玩家可以与当前地点出现的NPC进行对话，NPC会根据自身性格和当前活动做出回应。
4. **实时状态更新**：游戏界面会实时显示玩家当前位置、时间、地点描述、可前往地点以及NPC信息。

## 技术栈

- **前端**：React + TypeScript
- **后端**：Python + FastAPI
- **LLM集成**：Langchain + Volcengine LLM API
- **状态管理**：自定义游戏状态管理器

## 运行方式

### 后端

1. 进入后端目录：`cd /home/ubuntu/llm_text_game/backend`
2. 激活虚拟环境：`. venv/bin/activate`
3. 安装依赖：`pip install -r requirements.txt`
4. 运行服务：`cd src && uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

### 前端

1. 进入前端目录：`cd /home/ubuntu/llm_text_game/frontend`
2. 安装依赖：`pnpm install`
3. 运行开发服务器：`pnpm run dev`
4. 在浏览器中访问：`http://localhost:5173/`

## 开发经验总结

1. **LLM集成挑战**：将LLM集成到游戏逻辑中需要精心设计提示词和工具，以确保模型能够正确理解玩家意图并执行相应操作。
2. **状态管理**：游戏状态管理是核心挑战，需要处理玩家位置、NPC位置、时间流逝等多种状态变化。
3. **前后端交互**：确保前端UI与后端API的无缝集成，特别是在处理异步操作和状态更新时。
4. **Pydantic 2.x兼容性**：在使用Langchain工具时，需要注意Pydantic 2.x的新规范，为所有字段添加类型注解。

## 后续改进方向

1. **NPC对话深度优化**：进一步优化LLM的prompt和对话管理逻辑，使NPC对话更丰富、更符合角色个性。
2. **持久化存储**：添加数据库支持，实现游戏存档和读档功能。
3. **永久部署**：将应用部署到生产环境，提供稳定的访问入口。
4. **游戏内容扩展**：增加更多地点、角色和互动事件，丰富游戏内容。
5. **用户界面优化**：改进UI/UX设计，提升用户体验。

## API文档

后端API服务提供以下端点：

- `GET /api/game_state`：获取当前游戏状态
- `POST /api/process_action`：处理玩家行动
- `POST /api/start_dialogue/{npc_name}`：开始与NPC对话
- `POST /api/continue_dialogue/{npc_name}`：继续与NPC对话

## 访问方式

- **前端游戏界面**：`http://localhost:5173/`
- **后端API服务**：`https://8000-iiyqpzasbgji5ijebfyhe-7e42e626.manus.computer/api`

# LLM文字游戏 - LangGraph重构版本

> 🎮 基于LangGraph的新一代LLM驱动文字游戏架构

## 🌟 重构亮点

### 架构升级
- **工作流引擎**: 从传统Langchain迁移到LangGraph
- **状态管理**: 统一的状态图管理，支持持久化和回滚
- **节点设计**: 模块化的处理节点，职责清晰
- **路由系统**: 智能的行动路由，自动识别玩家意图

### 核心优势
- ✅ **更强的可维护性**: 清晰的节点分工和数据流
- ✅ **更好的可扩展性**: 易于添加新功能和节点
- ✅ **更强的错误恢复**: 内置重试和状态回滚机制
- ✅ **原生流式支持**: 实时的交互反馈
- ✅ **可视化调试**: 工作流图可视化，便于调试

## 🏗️ 架构概览

```
🎮 玩家输入
    ↓
🧠 Supervisor Node (督导节点)
    ├── 分析行动类型
    ├── 更新NPC位置
    └── 路由决策
    ↓
🔀 条件路由
    ├── 移动处理 → Move Handler Node
    ├── 对话处理 → Dialogue Handler Node  
    ├── 探索处理 → Exploration Handler Node
    └── 通用处理 → General Handler Node
    ↓
🔄 System Update Node (系统更新)
    ├── 清理状态
    ├── 准备下次输入
    └── 记录日志
    ↓
✅ 输出结果
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装LangGraph依赖
cd backend/src/langgraph_refactor
pip install -r requirements.txt

# 或安装到现有环境
pip install langgraph
```

### 2. 启动服务

```bash
# 方式1: 直接启动LangGraph版本
cd backend/src
python langgraph_main.py

# 方式2: 创建并使用启动脚本
python langgraph_main.py --create-script
./start_langgraph_game.sh

# 方式3: 测试工作流
python langgraph_main.py --test
```

### 3. 访问游戏

- **游戏界面**: http://localhost:5173
- **LangGraph API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs

## 📁 项目结构

```
backend/src/langgraph_refactor/
├── __init__.py              # 包初始化
├── game_state.py           # 游戏状态定义
├── nodes.py                # 核心处理节点
├── workflow.py             # 工作流图构建
├── api_integration.py      # FastAPI集成
└── requirements.txt        # 依赖文件

backend/src/
└── langgraph_main.py       # 主启动文件
```

## 🎯 核心组件

### 1. 游戏状态 (GameState)

```python
class GameState(TypedDict):
    # 玩家状态
    player_location: str
    player_personality: str  
    current_time: str
    
    # 消息历史 - 自动累加
    messages: Annotated[List[Dict], operator.add]
    
    # NPC状态
    npc_locations: Dict[str, str]
    npc_dialogue_histories: Dict[str, List[Dict]]
    
    # 游戏事件
    game_events: Annotated[List[Dict], operator.add]
    
    # 当前操作上下文
    current_action: str
    session_id: str
```

### 2. 处理节点

#### Supervisor Node (督导节点)
- 分析玩家输入意图
- 更新游戏世界状态
- 智能路由到相应处理节点

#### Move Handler Node (移动处理节点)
- 解析目标地点
- 验证移动合法性
- 执行移动并计算耗时

#### Dialogue Handler Node (对话处理节点)
- 解析对话对象和内容
- 检查NPC位置
- 生成NPC回复

#### Exploration Handler Node (探索处理节点)
- 生成环境感官反馈
- 描述当前场景
- 处理探索行为

### 3. 工作流图

```python
def create_game_workflow():
    workflow = StateGraph(GameState)
    
    # 添加节点
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("move_handler", move_handler_node)
    workflow.add_node("dialogue_handler", dialogue_handler_node)
    workflow.add_node("exploration_handler", exploration_handler_node)
    workflow.add_node("general_handler", general_handler_node)
    workflow.add_node("system_update", system_update_node)
    
    # 条件路由
    workflow.add_conditional_edges("supervisor", route_function)
    
    # 编译工作流
    return workflow.compile(checkpointer=MemorySaver())
```

## 🔧 API接口

### 兼容原有API

所有原有的API接口都得到保留和增强：

- `GET /api/game_state` - 获取游戏状态
- `POST /api/process_action` - 处理玩家行动
- `POST /api/continue_dialogue/{npc_name}` - NPC对话

### 新增功能

- `POST /api/stream_action` - 流式处理行动
- `POST /api/initialize_game` - 初始化游戏
- `GET /api/debug/workflow_state` - 调试工作流状态

## 🆚 对比原版本

| 特性 | 原版本 (Langchain) | LangGraph版本 |
|------|-------------------|---------------|
| **状态管理** | 自定义GameStateManager | LangGraph内置状态图 |
| **工作流控制** | 线性工具链 | 图状工作流 |
| **错误处理** | 手动异常处理 | 自动重试和回滚 |
| **可视化调试** | 无 | 工作流图可视化 |
| **持久化** | 内存存储 | 内置checkpointer |
| **流式处理** | 基础支持 | 原生流式支持 |
| **扩展性** | 需修改核心逻辑 | 添加节点即可 |

## 🧪 测试示例

```bash
# 运行完整测试套件
python langgraph_main.py --test
```

测试包括：
1. 初始化游戏状态
2. 移动功能测试
3. 对话功能测试  
4. 探索功能测试
5. 状态持久化测试

## 🛠️ 高级功能

### 1. 状态持久化

```python
# 自动保存状态
config = {"configurable": {"thread_id": session_id}}
result = await game_graph.ainvoke(state, config=config)

# 获取历史状态
state_history = game_graph.get_state_history(config)
```

### 2. 流式处理

```python
# 实时获取处理进度
async for chunk in game_graph.astream(state, stream_mode="updates"):
    print(f"节点更新: {chunk}")
```

### 3. 工作流可视化

```python
# 生成工作流图
from IPython.display import Image
Image(game_graph.get_graph().draw_mermaid_png())
```

## 🔮 未来规划

### 短期目标
- [ ] 完善错误处理机制
- [ ] 添加更多调试工具
- [ ] 优化性能和内存使用

### 中期目标
- [ ] 集成更高级的NPC Agent
- [ ] 实现动态剧情生成
- [ ] 添加多玩家支持

### 长期目标
- [ ] 支持自定义工作流
- [ ] 可视化编辑器
- [ ] 云端部署方案

## 🤝 迁移指南

### 从原版本迁移

1. **保持API兼容性**: 前端无需修改
2. **数据格式兼容**: 游戏数据完全兼容
3. **功能增强**: 所有原功能都得到保留和增强

### 并行运行

可以同时运行两个版本进行对比：
- 原版本: http://localhost:8000
- LangGraph版本: http://localhost:8001

## 📝 开发者指南

### 添加新节点

```python
def my_custom_node(state: GameState) -> Dict[str, Any]:
    # 自定义处理逻辑
    return {"messages": [create_message("系统", "自定义处理完成")]}

# 添加到工作流
workflow.add_node("my_custom", my_custom_node)
workflow.add_edge("supervisor", "my_custom")
```

### 自定义路由逻辑

```python
def custom_router(state: GameState) -> str:
    if "特殊关键词" in state["current_action"]:
        return "custom_handler"
    return "general_handler"
```

## 🐛 故障排除

### 常见问题

1. **LangGraph未安装**
   ```bash
   pip install langgraph
   ```

2. **端口冲突**
   - 原版本使用8000端口
   - LangGraph版本使用8001端口

3. **依赖版本冲突**
   - 检查requirements.txt中的版本要求
   - 建议使用虚拟环境

### 调试工具

```python
# 检查工作流状态
GET /api/debug/workflow_state

# 查看节点执行日志
python langgraph_main.py --test

# 可视化工作流
from langgraph_refactor.workflow import get_game_graph
graph = get_game_graph()
print(graph.get_graph().nodes)
```

## 📄 许可证

本项目遵循原项目的许可证协议。

## 🙏 致谢

感谢LangGraph团队提供强大的工作流框架，让复杂的AI应用开发变得更加简单和可维护。

---

**LangGraph重构版本** - 让AI游戏开发更简单、更强大、更可维护！ 🎮✨ 
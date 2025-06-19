# 🚀 完整系统启动指南

## 📋 系统概述

本项目是一个完整的LLM驱动文字游戏系统，包含：
- **后端**: FastAPI + LangGraph + 用户认证
- **前端**: React + TypeScript + 现代化UI
- **数据库**: PostgreSQL/SQLite 持久化存储
- **认证**: JWT令牌认证系统

## 🎯 快速启动

### 方法一：一键启动（推荐）

```bash
# 给脚本执行权限（首次运行）
chmod +x start_full_system.sh

# 一键启动完整系统
./start_full_system.sh
```

### 方法二：分步启动

#### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（首次运行）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_database.py

# 启动后端服务
python src/app.py
```

#### 2. 启动前端

```bash
# 新开一个终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动前端服务
npm run dev
```

## 🌐 访问地址

启动成功后，可以通过以下地址访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端界面** | http://localhost:5173 | 游戏主界面 |
| **后端API** | http://localhost:8001 | API服务 |
| **API文档** | http://localhost:8001/docs | Swagger文档 |
| **健康检查** | http://localhost:8001/health | 服务状态 |

## 🔐 认证功能

### 注册新用户
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com"
  }'
```

### 用户登录
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

## 🧪 测试功能

### 运行认证测试
```bash
cd backend
python test_auth.py
```

### 运行API示例
```bash
cd backend
python api_examples.py
```

## 📁 项目结构

```
GalgameWithLLM/
├── backend/                 # 后端代码
│   ├── src/
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── controllers/    # 控制器
│   │   ├── routers/        # 路由
│   │   └── utils/          # 工具类
│   ├── config/             # 配置文件
│   ├── requirements.txt    # Python依赖
│   └── init_database.py    # 数据库初始化
├── frontend/               # 前端代码
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── package.json       # Node.js依赖
├── start_full_system.sh   # 一键启动脚本
└── README.md              # 项目说明
```

## ⚙️ 配置说明

### 数据库配置
编辑 `backend/config/config.json`：
```json
{
    "db": {
        "host": "localhost",
        "port": 5432,
        "user": "your_username",
        "password": "your_password",
        "database": "galgame_db"
    }
}
```

### 前端环境配置
前端会自动创建 `.env.local` 文件：
```env
VITE_API_URL=http://localhost:8001
VITE_APP_TITLE=LLM文字游戏
VITE_APP_VERSION=2.1.0
```

## 🔧 环境要求

### 必需软件
- **Python 3.8+**
- **Node.js 16+**
- **npm 8+**

### 推荐软件
- **PostgreSQL** (生产环境)
- **Git** (版本控制)

## 🚨 常见问题

### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :8001  # 后端端口
lsof -i :5173  # 前端端口

# 杀死进程
kill -9 <PID>
```

### 2. 数据库连接失败
- 检查 `config/config.json` 中的数据库配置
- 确保数据库服务正在运行
- 系统会自动使用SQLite作为备用

### 3. 依赖安装失败
```bash
# 清理缓存
pip cache purge
npm cache clean --force

# 重新安装
pip install -r requirements.txt
npm install
```

### 4. 前端无法连接后端
- 检查后端是否正常启动
- 确认API地址配置正确
- 检查CORS设置

## 📝 开发模式

### 后端开发
```bash
cd backend
source venv/bin/activate
python src/app.py  # 自动重载
```

### 前端开发
```bash
cd frontend
npm run dev  # 热重载
```

## 🎮 使用示例

### 1. 注册用户
```javascript
fetch('http://localhost:8001/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'player1',
        password: 'password123',
        email: 'player1@example.com'
    })
})
```

### 2. 登录游戏
```javascript
fetch('http://localhost:8001/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'player1',
        password: 'password123'
    })
})
.then(response => response.json())
.then(data => {
    const token = data.access_token;
    // 使用token访问游戏API
});
```

### 3. 开始游戏
```javascript
fetch('http://localhost:8001/api/initialize_game?session_id=player1', {
    headers: { 'Authorization': `Bearer ${token}` }
})
```

## 🛑 停止服务

### 一键停止
按 `Ctrl+C` 停止所有服务

### 手动停止
```bash
# 查找进程
ps aux | grep python
ps aux | grep node

# 杀死进程
kill -9 <PID>
```

## 📞 技术支持

- **API文档**: http://localhost:8001/docs
- **健康检查**: http://localhost:8001/health
- **项目文档**: README.md
- **认证文档**: backend/README_AUTH.md

---

�� **享受您的LLM文字游戏之旅！** 
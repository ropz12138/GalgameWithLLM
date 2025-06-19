# 🔐 用户认证系统

## 📋 概述

本项目已集成完整的用户认证系统，支持用户注册、登录和JWT令牌认证。系统采用密码加密存储，确保用户数据安全。

## 🏗️ 架构设计

### 技术栈
- **数据库**: PostgreSQL (主) / SQLite (备用)
- **ORM**: SQLAlchemy
- **认证**: JWT (JSON Web Token)
- **密码加密**: bcrypt
- **API框架**: FastAPI

### 目录结构
```
backend/src/
├── models/
│   └── user_model.py          # 用户数据模型
├── services/
│   └── auth_service.py        # 认证业务逻辑
├── controllers/
│   └── auth_controller.py     # 认证控制器
├── routers/
│   └── auth_router.py         # 认证路由
└── utils/
    ├── database.py            # 数据库连接
    └── auth.py                # JWT认证工具
```

## 🚀 快速开始

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库
编辑 `config/config.json` 文件：
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

### 3. 初始化数据库
```bash
python init_database.py
```

### 4. 启动服务器
```bash
python src/app.py
```

## 📡 API端点

### 认证端点

#### 1. 用户注册
```http
POST /auth/register
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com",
    "phone": "13800138000"
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "用户注册成功",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone": "13800138000",
        "created_at": "2024-01-01T00:00:00"
    }
}
```

#### 2. 用户登录
```http
POST /auth/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123"
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "登录成功",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone": "13800138000",
        "created_at": "2024-01-01T00:00:00"
    }
}
```

#### 3. 获取用户信息
```http
GET /auth/me
Authorization: Bearer <access_token>
```

**响应示例:**
```json
{
    "success": true,
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone": "13800138000",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
}
```

#### 4. 验证用户名
```http
GET /auth/validate-username?username=testuser
```

**响应示例:**
```json
{
    "success": true,
    "username": "testuser",
    "available": false,
    "message": "用户名已存在"
}
```

## 🔒 安全特性

### 密码安全
- 使用 bcrypt 算法加密存储密码
- 密码长度至少6位
- 密码永远不会以明文形式存储或传输

### JWT令牌
- 令牌有效期：30分钟
- 使用HS256算法签名
- 包含用户身份信息

### 数据验证
- 用户名唯一性检查
- 邮箱唯一性检查（可选）
- 电话号码唯一性检查（可选）
- 输入数据验证和清理

## 🗄️ 数据库设计

### 用户表 (users)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| username | String(50) | 用户名，唯一 |
| email | String(100) | 邮箱，唯一，可选 |
| phone | String(20) | 电话，唯一，可选 |
| hashed_password | String(255) | 加密后的密码 |
| is_active | Boolean | 用户状态 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 🧪 测试

### 运行测试脚本
```bash
python test_auth.py
```

### 手动测试
1. 启动服务器
2. 访问 http://localhost:8001/docs
3. 使用Swagger UI测试API

## 🔧 配置选项

### JWT配置
在 `utils/auth.py` 中可以修改：
- `SECRET_KEY`: JWT签名密钥
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 令牌过期时间

### 数据库配置
在 `config/config.json` 中可以修改：
- 数据库连接参数
- 数据库类型（PostgreSQL/SQLite）

## 📝 使用示例

### Python客户端示例
```python
import requests

# 注册用户
register_data = {
    "username": "newuser",
    "password": "password123",
    "email": "newuser@example.com"
}
response = requests.post("http://localhost:8001/auth/register", json=register_data)
print(response.json())

# 登录
login_data = {
    "username": "newuser",
    "password": "password123"
}
response = requests.post("http://localhost:8001/auth/login", json=login_data)
token = response.json()["access_token"]

# 获取用户信息
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8001/auth/me", headers=headers)
print(response.json())
```

### JavaScript客户端示例
```javascript
// 注册用户
const registerData = {
    username: "newuser",
    password: "password123",
    email: "newuser@example.com"
};

fetch("http://localhost:8001/auth/register", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(registerData)
})
.then(response => response.json())
.then(data => console.log(data));

// 登录
const loginData = {
    username: "newuser",
    password: "password123"
};

fetch("http://localhost:8001/auth/login", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => {
    const token = data.access_token;
    
    // 获取用户信息
    fetch("http://localhost:8001/auth/me", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(userData => console.log(userData));
});
```

## 🚨 注意事项

1. **生产环境安全**：
   - 修改 `SECRET_KEY` 为强密钥
   - 使用HTTPS
   - 配置适当的CORS策略

2. **数据库备份**：
   - 定期备份用户数据
   - 保护数据库连接信息

3. **密码策略**：
   - 可以添加密码复杂度要求
   - 实现密码重置功能

4. **令牌管理**：
   - 可以实现令牌刷新机制
   - 添加令牌黑名单功能

## 🔄 版本历史

- **v2.1.0**: 添加用户认证系统
  - 用户注册和登录
  - JWT令牌认证
  - 密码加密存储
  - 数据库持久化

## 📞 支持

如有问题，请查看：
- API文档：http://localhost:8001/docs
- 健康检查：http://localhost:8001/health 
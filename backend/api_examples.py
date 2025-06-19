#!/usr/bin/env python3
"""
API使用示例
演示如何使用认证和游戏API
"""
import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8001"

def print_response(title, response):
    """打印响应信息"""
    print(f"\n{title}")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应文本: {response.text}")

def example_1_register_and_login():
    """示例1: 注册和登录"""
    print("=" * 60)
    print("示例1: 用户注册和登录")
    print("=" * 60)
    
    # 1. 注册用户
    register_data = {
        "username": "demo_user",
        "password": "demo123456",
        "email": "demo@example.com",
        "phone": "13900139000"
    }
    
    print("1. 注册用户...")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response("注册响应", response)
    
    if response.status_code != 200:
        print("注册失败，跳过后续步骤")
        return None
    
    # 2. 用户登录
    login_data = {
        "username": "demo_user",
        "password": "demo123456"
    }
    
    print("\n2. 用户登录...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("登录响应", response)
    
    if response.status_code != 200:
        print("登录失败")
        return None
    
    # 获取访问令牌
    token = response.json()["access_token"]
    print(f"\n✅ 获取到访问令牌: {token[:20]}...")
    
    return token

def example_2_get_user_info(token):
    """示例2: 获取用户信息"""
    print("\n" + "=" * 60)
    print("示例2: 获取用户信息")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("获取当前用户信息...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("用户信息响应", response)

def example_3_validate_username():
    """示例3: 验证用户名"""
    print("\n" + "=" * 60)
    print("示例3: 验证用户名")
    print("=" * 60)
    
    # 验证已存在的用户名
    print("验证已存在的用户名...")
    response = requests.get(f"{BASE_URL}/auth/validate-username?username=demo_user")
    print_response("验证响应", response)
    
    # 验证新用户名
    print("\n验证新用户名...")
    response = requests.get(f"{BASE_URL}/auth/validate-username?username=new_user_123")
    print_response("验证响应", response)

def example_4_game_api(token):
    """示例4: 游戏API调用"""
    print("\n" + "=" * 60)
    print("示例4: 游戏API调用")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取游戏状态
    print("获取游戏状态...")
    response = requests.get(f"{BASE_URL}/api/game_state?session_id=demo_user", headers=headers)
    print_response("游戏状态响应", response)
    
    # 初始化游戏
    print("\n初始化游戏...")
    response = requests.get(f"{BASE_URL}/api/initialize_game?session_id=demo_user", headers=headers)
    print_response("初始化游戏响应", response)
    
    # 处理玩家行动
    print("\n处理玩家行动...")
    action_data = {
        "action": "查看周围",
        "session_id": "demo_user"
    }
    response = requests.post(f"{BASE_URL}/api/process_action", json=action_data, headers=headers)
    print_response("处理行动响应", response)

def example_5_health_check():
    """示例5: 健康检查"""
    print("\n" + "=" * 60)
    print("示例5: 健康检查")
    print("=" * 60)
    
    print("检查服务健康状态...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("健康检查响应", response)

def main():
    """主函数"""
    print("🎮 LLM文字游戏 API 使用示例")
    print("请确保服务器已启动: python src/app.py")
    print("=" * 60)
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    try:
        # 示例1: 注册和登录
        token = example_1_register_and_login()
        
        if token:
            # 示例2: 获取用户信息
            example_2_get_user_info(token)
            
            # 示例3: 验证用户名
            example_3_validate_username()
            
            # 示例4: 游戏API调用
            example_4_game_api(token)
        
        # 示例5: 健康检查
        example_5_health_check()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例执行完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败！请确保服务器已启动:")
        print("   python src/app.py")
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")

if __name__ == "__main__":
    main() 
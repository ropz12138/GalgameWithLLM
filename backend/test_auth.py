#!/usr/bin/env python3
"""
认证功能测试脚本
"""
import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8001"

def test_register():
    """测试用户注册"""
    print("🔍 测试用户注册...")
    
    # 注册数据
    register_data = {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com",
        "phone": "13900139000"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 注册成功:")
            print(f"  👤 用户ID: {result['user']['id']}")
            print(f"  👤 用户名: {result['user']['username']}")
            return True
        else:
            print(f"❌ 注册失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_login():
    """测试用户登录"""
    print("\n🔍 测试用户登录...")
    
    # 登录数据
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 登录成功:")
            print(f"  🔑 令牌类型: {result['token_type']}")
            print(f"  👤 用户名: {result['user']['username']}")
            return result.get('access_token')
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_get_user_info(token):
    """测试获取用户信息"""
    print("\n🔍 测试获取用户信息...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取用户信息成功:")
            print(f"  👤 用户ID: {result['user']['id']}")
            print(f"  👤 用户名: {result['user']['username']}")
            print(f"  📧 邮箱: {result['user']['email']}")
            print(f"  📱 电话: {result['user']['phone']}")
            return True
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_validate_username():
    """测试用户名验证"""
    print("\n🔍 测试用户名验证...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/validate-username?username=testuser")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 用户名验证成功:")
            print(f"  👤 用户名: {result['username']}")
            print(f"  ✅ 可用性: {result['available']}")
            return True
        else:
            print(f"❌ 用户名验证失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_health_check():
    """测试健康检查"""
    print("\n🔍 测试健康检查...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 健康检查成功:")
            print(f"  🏥 状态: {result['status']}")
            print(f"  🗄️ 数据库: {result['database']}")
            print(f"  📅 版本: {result['version']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 认证功能测试")
    print("=" * 60)
    
    # 测试健康检查
    if not test_health_check():
        print("❌ 服务器可能未启动，请先启动服务器")
        return
    
    # 测试注册
    if not test_register():
        print("❌ 注册测试失败")
        return
    
    # 测试登录
    token = test_login()
    if not token:
        print("❌ 登录测试失败")
        return
    
    # 测试获取用户信息
    if not test_get_user_info(token):
        print("❌ 获取用户信息测试失败")
        return
    
    # 测试用户名验证
    if not test_validate_username():
        print("❌ 用户名验证测试失败")
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    main() 
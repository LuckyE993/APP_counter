#!/usr/bin/env python3
"""
简单的认证功能测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_login():
    """测试登录功能"""
    print("🔐 测试登录功能...")
    
    # 测试正确的登录信息
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ 登录成功!")
        print(f"Token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None

def test_protected_endpoint(token):
    """测试受保护的端点"""
    print("\n🔒 测试受保护的端点...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 测试获取账户配置
    response = requests.get(f"{BASE_URL}/config/accounts", headers=headers)
    
    if response.status_code == 200:
        print("✅ 访问受保护端点成功!")
        return True
    else:
        print(f"❌ 访问受保护端点失败: {response.status_code} - {response.text}")
        return False

def test_unauthorized_access():
    """测试未授权访问"""
    print("\n🚫 测试未授权访问...")
    
    response = requests.get(f"{BASE_URL}/config/accounts")
    
    if response.status_code == 401:
        print("✅ 未授权访问被正确拒绝!")
        return True
    else:
        print(f"❌ 未授权访问应该被拒绝: {response.status_code}")
        return False

def main():
    print("🧪 开始认证功能测试\n")
    
    try:
        # 测试未授权访问
        test_unauthorized_access()
        
        # 测试登录
        token = test_login()
        if not token:
            return
        
        # 测试受保护端点
        test_protected_endpoint(token)
        
        print("\n🎉 所有测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()
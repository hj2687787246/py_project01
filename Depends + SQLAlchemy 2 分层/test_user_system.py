import requests
import time
import json
import logging
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 基础URL
BASE_URL = "http://localhost:8000"

def safe_json_parse(response):
    """安全地解析JSON响应"""
    try:
        return response.json()
    except json.JSONDecodeError:
        return {
            "error": "无法解析响应", 
            "status_code": response.status_code, 
            "text": response.text[:500]
        }

def check_service_health():
    """检查服务健康状态"""
    print("=== 检查服务健康状态 ===")
    try:
        # 首先检查文档页面
        docs_response = requests.get(f"{BASE_URL}/docs")
        print(f"文档页面状态: {docs_response.status_code}")
        
        # 检查健康检查端点
        health_response = requests.get(f"{BASE_URL}/health")
        print(f"健康检查状态: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = safe_json_parse(health_response)
            print(f"服务状态: {health_data}")
            return True
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保FastAPI应用正在运行")
        print("启动命令: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ 检查服务状态时出错: {e}")
        return False

def test_create_user():
    """测试创建用户 - 包含所有边界情况"""
    print("\n=== 测试1: 创建用户 ===")
    
    test_cases = [
        # 正常情况
        {
            "name": "正常创建用户",
            "data": {
                "username": "testuser1",
                "age": 25,
                "email": "testuser1@example.com"
            },
            "expected_status": 200
        },
        # 边界情况 - 年龄边界值
        {
            "name": "年龄为0",
            "data": {
                "username": "testuser2",
                "age": 0,
                "email": "testuser2@example.com"
            },
            "expected_status": 200
        },
        {
            "name": "年龄为150",
            "data": {
                "username": "testuser3",
                "age": 150,
                "email": "testuser3@example.com"
            },
            "expected_status": 200
        },
        # 错误情况 - 无效邮箱
        {
            "name": "无效邮箱格式",
            "data": {
                "username": "testuser4",
                "age": 25,
                "email": "invalid-email"
            },
            "expected_status": 422  # Pydantic验证错误
        },
        # 错误情况 - 用户名过短
        {
            "name": "用户名过短",
            "data": {
                "username": "ab",
                "age": 25,
                "email": "testuser5@example.com"
            },
            "expected_status": 422
        }
    ]
    
    created_user_ids = []
    
    for case in test_cases:
        print(f"\n--- 测试用例: {case['name']} ---")
        try:
            response = requests.post(f"{BASE_URL}/users", json=case["data"])
            print(f"状态码: {response.status_code}")
            
            response_data = safe_json_parse(response)
            print(f"响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 记录成功创建的用户ID
            if (response.status_code == case["expected_status"] and 
                response.status_code == 200 and 
                'data' in response_data and 
                response_data['data']):
                created_user_ids.append(response_data['data'].get('id'))
                
        except Exception as e:
            print(f"请求失败: {e}")
    
    return created_user_ids[0] if created_user_ids else None

def test_get_user(user_id: int):
    """测试查询单个用户"""
    print("\n=== 测试2: 查询单个用户 ===")
    
    if not user_id:
        print("没有有效的用户ID")
        return
    
    # 正常查询
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"查询用户 - 状态码: {response.status_code}")
        
        response_data = safe_json_parse(response)
        print(f"响应内容: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"查询用户失败: {e}")
    
    # 查询不存在的用户
    print("\n--- 查询不存在的用户 ---")
    try:
        response = requests.get(f"{BASE_URL}/users/999999")
        print(f"状态码: {response.status_code}")
        response_data = safe_json_parse(response)
        print(f"响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"查询失败: {e}")

def test_list_users():
    """测试分页查询用户列表"""
    print("\n=== 测试3: 分页查询用户列表 ===")
    
    test_cases = [
        {"page": 1, "page_size": 5},
        {"page": 1, "page_size": 0},  # 测试默认值
        {"page": 999, "page_size": 10}  # 测试空结果
    ]
    
    for case in test_cases:
        print(f"\n--- 分页参数: page={case['page']}, page_size={case['page_size']} ---")
        try:
            url = f"{BASE_URL}/users?page={case['page']}&page_size={case['page_size']}"
            response = requests.get(url)
            print(f"状态码: {response.status_code}")
            
            response_data = safe_json_parse(response)
            if 'data' in response_data and response_data['data']:
                print(f"返回用户数量: {len(response_data['data'])}")
                if len(response_data['data']) > 0:
                    print(f"第一条记录: {response_data['data'][0]}")
            else:
                print("没有返回用户数据")
                
        except Exception as e:
            print(f"请求失败: {e}")

def test_search_users():
    """测试模糊查询"""
    print("\n=== 测试4: 模糊查询用户 ===")
    
    search_terms = ["testuser", "@example.com", "nonexistent"]
    
    for term in search_terms:
        print(f"\n--- 搜索关键词: '{term}' ---")
        try:
            response = requests.get(f"{BASE_URL}/users/search/?keyword={term}")
            print(f"状态码: {response.status_code}")
            
            response_data = safe_json_parse(response)
            if 'data' in response_data and response_data['data']:
                print(f"找到 {len(response_data['data'])} 个结果")
            else:
                print("没有找到结果")
                
        except Exception as e:
            print(f"搜索失败: {e}")

def test_update_user(user_id: int):
    """测试更新用户"""
    print("\n=== 测试5: 更新用户信息 ===")
    
    if not user_id:
        print("没有有效的用户ID")
        return
    
    update_cases = [
        {
            "name": "正常更新",
            "data": {
                "age": 26,
                "email": "updated_email@example.com"
            }
        },
        {
            "name": "只更新部分字段",
            "data": {
                "age": 27
            }
        }
    ]
    
    for case in update_cases:
        print(f"\n--- {case['name']} ---")
        try:
            response = requests.put(f"{BASE_URL}/users/{user_id}", json=case["data"])
            print(f"状态码: {response.status_code}")
            
            response_data = safe_json_parse(response)
            print(f"响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
        except Exception as e:
            print(f"更新失败: {e}")

def test_delete_user(user_id: int):
    """测试删除用户"""
    print("\n=== 测试6: 删除用户 ===")
    
    if not user_id:
        print("没有有效的用户ID")
        return
    
    # 删除存在的用户
    try:
        response = requests.delete(f"{BASE_URL}/users/{user_id}")
        print(f"删除用户 - 状态码: {response.status_code}")
        
        response_data = safe_json_parse(response)
        print(f"响应内容: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        
        # 验证用户是否被删除
        print("\n--- 验证用户是否被删除 ---")
        verify_response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"验证查询状态码: {verify_response.status_code}")
        
    except Exception as e:
        print(f"删除失败: {e}")

def run_comprehensive_test():
    """运行全面测试"""
    print("=" * 50)
    print("开始全面测试用户管理系统")
    print("=" * 50)
    
    # 1. 检查服务健康状态
    if not check_service_health():
        print("❌ 服务未运行，无法继续测试")
        return
    
    print("✅ 服务运行正常，开始功能测试...")
    
    # 2. 执行所有测试
    user_id = test_create_user()
    
    if user_id:
        test_get_user(user_id)
        test_list_users()
        test_search_users()
        test_update_user(user_id)
        test_delete_user(user_id)
    else:
        print("⚠️  创建用户失败，跳过后续测试")
    
    print("\n" + "=" * 50)
    print("全面测试完成")
    print("=" * 50)

if __name__ == "__main__":
    run_comprehensive_test()

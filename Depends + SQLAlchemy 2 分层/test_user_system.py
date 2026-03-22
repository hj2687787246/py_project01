import json
from datetime import datetime
from typing import Optional

import requests


BASE_URL = "http://127.0.0.1:8000"
TEST_SUFFIX = datetime.now().strftime("%Y%m%d%H%M%S")
TEST_USERNAME = f"user_{TEST_SUFFIX}"
TEST_EMAIL = f"{TEST_USERNAME}@example.com"
UPDATED_TEST_EMAIL = f"updated_{TEST_USERNAME}@example.com"
TEST_PASSWORD = "123456"


def safe_json(response: requests.Response):
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"raw_text": response.text}


def print_response(title: str, response: requests.Response):
    print(f"\n=== {title} ===")
    print(f"Status: {response.status_code}")
    print(json.dumps(safe_json(response), ensure_ascii=False, indent=2))


def check_health() -> bool:
    response = requests.get(f"{BASE_URL}/health")
    print_response("健康检查", response)
    return response.status_code == 200


def create_user(username: str, password: str, age: int, email: str) -> Optional[int]:
    payload = {
        "username": username,
        "password": password,
        "age": age,
        "email": email,
    }
    response = requests.post(f"{BASE_URL}/users", json=payload)
    print_response("注册用户", response)

    data = safe_json(response)
    if response.status_code == 200 and data.get("data"):
        return data["data"].get("id")
    return None


def login(username: str, password: str) -> Optional[str]:
    form_data = {
        "username": username,
        "password": password,
    }
    response = requests.post(f"{BASE_URL}/users/token", data=form_data)
    print_response("登录获取 Token", response)

    data = safe_json(response)
    if response.status_code == 200:
        return data.get("access_token")
    return None


def get_user_id_by_username(username: str, admin_token: str) -> Optional[int]:
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/users/search/?keyword={username}", headers=headers)
    print_response("按用户名查找用户", response)

    data = safe_json(response)
    if response.status_code == 200 and data.get("data"):
        for user in data["data"]:
            if user.get("username") == username:
                return user.get("id")
    return None


def get_user(user_id: int, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
    print_response("查询当前用户", response)


def update_user(user_id: int, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "age": 20,
        "email": UPDATED_TEST_EMAIL,
    }
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=payload, headers=headers)
    print_response("修改当前用户", response)


def list_users(admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/users?page=1&page_size=10", headers=headers)
    print_response("管理员查看用户列表", response)


def search_users(admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/users/search/?keyword=user", headers=headers)
    print_response("管理员模糊搜索用户", response)


def delete_user(user_id: int, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
    print_response("管理员删除用户", response)


def run_basic_flow():
    if not check_health():
        print("\n服务未正常启动，请先运行：uvicorn main:app --reload")
        return

    print(f"\n本次测试用户: username={TEST_USERNAME}, email={TEST_EMAIL}")

    user_id = create_user(username=TEST_USERNAME, password=TEST_PASSWORD, age=18, email=TEST_EMAIL)
    token = login(username=TEST_USERNAME, password=TEST_PASSWORD)

    if token and not user_id:
        admin_token = login(username="admin", password="123456")
        if admin_token:
            user_id = get_user_id_by_username(username=TEST_USERNAME, admin_token=admin_token)

    if user_id and token:
        get_user(user_id=user_id, token=token)
        update_user(user_id=user_id, token=token)
    else:
        print("\n基础流程未完成，跳过后续用户操作。")


def run_admin_flow():
    print("\n=== 管理员接口测试说明 ===")
    print("如果你数据库里已经有管理员账号，可以取消下面两行注释后测试管理员接口。")
    print("默认管理员账号示例：admin / 123456")

    admin_token = login(username="admin", password="123456")
    if admin_token:
        list_users(admin_token)
        search_users(admin_token)
        target_user_id = get_user_id_by_username(username=TEST_USERNAME, admin_token=admin_token)
        if target_user_id:
            delete_user(user_id=target_user_id, admin_token=admin_token)
        else:
            print(f"\n未找到 {TEST_USERNAME}，跳过管理员删除用户测试。")


if __name__ == "__main__":
    run_basic_flow()
    run_admin_flow()

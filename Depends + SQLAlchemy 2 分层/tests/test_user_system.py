import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import get_logger

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
# 测试环境关闭登录限流，避免批量用例触发 429。
os.environ.setdefault("TESTING", "1")

import main
import routers.user_routes as user_routes
import utils.file_utils as file_utils
import utils.security as security

security.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
user_routes.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
from dao import role_dao, user_dao
from schemas import UserCreate
from session import db_session
from session.db_session import Base

logger = get_logger()


def cleanup_test_avatars():
    """清理测试生成的头像文件，保留默认头像。"""
    if not file_utils.STATIC_DIR.exists():
        return
    for avatar_file in file_utils.STATIC_DIR.iterdir():
        if avatar_file.is_file() and avatar_file.name != "default.jpg":
            avatar_file.unlink()


def setup_module():
    """测试模块启动前清理遗留测试库。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    if db_path.exists():
        logger.info(f"删除遗留测试数据库: path={db_path}")
        db_path.unlink()
    cleanup_test_avatars()


def teardown_module():
    """测试模块结束后清理测试库。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    if db_path.exists():
        logger.info(f"清理测试数据库: path={db_path}")
        db_path.unlink()
    cleanup_test_avatars()


def build_test_client():
    """构建独立测试库和 TestClient。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    logger.info(f"构建测试客户端: db_path={db_path}")
    test_engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    db_session.engine = test_engine
    db_session.SessionLocal = testing_session_local
    main.engine = test_engine
    main.SessionLocal = testing_session_local

    # 每次构建测试客户端都重置库，确保测试之间互不污染。
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # 初始化角色和管理员账号，避免依赖外部环境已有数据。
    with testing_session_local() as db:
        role_dao.create_role(db, name="admin", description="系统管理员")
        role_dao.create_role(db, name="user", description="普通用户")
        admin_user = UserCreate(
            username="admin",
            password="123456",
            age=30,
            email="admin@example.com",
        )
        user_dao.create_user(db, admin_user, role_name="admin")

    cleanup_test_avatars()
    client = TestClient(main.app)
    logger.success("测试客户端构建完成")
    return client, test_engine


def auth_headers(token: str) -> dict:
    """构建 Bearer Token 请求头。"""
    return {"Authorization": f"Bearer {token}"}


def login(client: TestClient, username: str, password: str) -> str:
    """执行登录并返回访问令牌。"""
    logger.info(f"测试登录: username={username}")
    response = client.post(
        "/users/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    logger.success(f"测试登录成功: username={username}")
    return response.json()["access_token"]


def create_user(
    client: TestClient,
    username: str = "alice",
    password: str = "Aa123456!",
    age: int = 18,
    email: str = "alice@example.com",
) -> dict:
    """通过注册接口创建测试用户。"""
    logger.info(f"测试创建用户: username={username}, email={email}")
    response = client.post(
        "/users",
        json={
            "username": username,
            "password": password,
            "age": age,
            "email": email,
        },
    )
    assert response.status_code == 200, response.text
    logger.success(f"测试创建用户成功: username={username}")
    return response.json()["data"]


def test_health_check():
    """验证健康检查接口。"""
    client, engine = build_test_client()
    try:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "message": "服务正常运行"}
    finally:
        client.close()
        engine.dispose()


def test_user_basic_flow():
    """验证普通用户注册、登录、查询、更新主流程。"""
    client, engine = build_test_client()
    try:
        created_user = create_user(client)
        token = login(client, "alice", "Aa123456!")

        get_response = client.get(
            f"/users/{created_user['id']}",
            headers=auth_headers(token),
        )
        assert get_response.status_code == 200, get_response.text
        assert get_response.json()["data"]["username"] == "alice"
        assert get_response.json()["data"]["role"] == "user"

        update_response = client.put(
            f"/users/{created_user['id']}",
            json={"age": 20, "email": "alice.updated@example.com"},
            headers=auth_headers(token),
        )
        assert update_response.status_code == 200, update_response.text
        assert update_response.json()["data"]["age"] == 20
        assert update_response.json()["data"]["email"] == "alice.updated@example.com"
    finally:
        client.close()
        engine.dispose()


def test_exception_responses():
    """验证常见异常响应格式和业务码。"""
    client, engine = build_test_client()
    try:
        create_user(client)

        duplicate_username = client.post(
            "/users",
            json={
                "username": "alice",
                "password": "Aa123456!",
                "age": 18,
                "email": "alice2@example.com",
            },
        )
        assert duplicate_username.status_code == 400, duplicate_username.text
        assert duplicate_username.json()["code"] == 4001

        duplicate_email = client.post(
            "/users",
            json={
                "username": "alice2",
                "password": "Aa123456!",
                "age": 18,
                "email": "alice@example.com",
            },
        )
        assert duplicate_email.status_code == 400, duplicate_email.text
        assert duplicate_email.json()["code"] == 4002

        bad_login = client.post(
            "/users/token",
            data={"username": "alice", "password": "wrong-password"},
        )
        assert bad_login.status_code == 400, bad_login.text
        assert bad_login.json()["code"] == 400

        no_token = client.get("/users/1")
        assert no_token.status_code == 401, no_token.text
        assert no_token.json()["code"] == 401
    finally:
        client.close()
        engine.dispose()


def test_permission_and_admin_flows():
    """验证管理员权限相关接口和删除限制。"""
    client, engine = build_test_client()
    try:
        user = create_user(client)
        user_token = login(client, "alice", "Aa123456!")
        admin_token = login(client, "admin", "123456")

        forbidden_role_update = client.put(
            f"/users/{user['id']}",
            json={"role_id": 1},
            headers=auth_headers(user_token),
        )
        assert forbidden_role_update.status_code == 403, forbidden_role_update.text
        assert forbidden_role_update.json()["code"] == 4004

        list_response = client.get(
            "/users?page=1&page_size=10",
            headers=auth_headers(admin_token),
        )
        assert list_response.status_code == 200, list_response.text
        list_data = list_response.json()["data"]
        assert list_data["total"] == 2
        assert len(list_data["items"]) == 2

        search_response = client.get(
            "/users/search/?keyword=alice",
            headers=auth_headers(admin_token),
        )
        assert search_response.status_code == 200, search_response.text
        assert len(search_response.json()["data"]) == 1

        delete_admin = client.delete(
            "/users/1",
            headers=auth_headers(admin_token),
        )
        assert delete_admin.status_code == 403, delete_admin.text
        assert delete_admin.json()["code"] == 4003

        delete_user_response = client.delete(
            f"/users/{user['id']}",
            headers=auth_headers(admin_token),
        )
        assert delete_user_response.status_code == 200, delete_user_response.text
        assert delete_user_response.json()["data"]["user_id"] == user["id"]
    finally:
        client.close()
        engine.dispose()


def test_create_admin_user_api():
    """验证管理员创建管理员账号接口。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.post(
            "/roles/admin/users",
            json={
                "username": "boss2",
                "password": "Aa123456!",
                "age": 35,
                "email": "boss2@example.com",
            },
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["username"] == "boss2"
        assert data["role"] == "admin"
    finally:
        client.close()
        engine.dispose()


def test_create_admin_user_api_duplicate_cases():
    """验证创建管理员账号时的重复校验。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")
        create_user(client, username="alice", email="alice@example.com")

        duplicate_username = client.post(
            "/roles/admin/users",
            json={
                "username": "alice",
                "password": "Aa123456!",
                "age": 28,
                "email": "alice_admin@example.com",
            },
            headers=auth_headers(admin_token),
        )
        assert duplicate_username.status_code == 400, duplicate_username.text
        assert duplicate_username.json()["code"] == 4001

        duplicate_email = client.post(
            "/roles/admin/users",
            json={
                "username": "alice_admin",
                "password": "Aa123456!",
                "age": 28,
                "email": "alice@example.com",
            },
            headers=auth_headers(admin_token),
        )
        assert duplicate_email.status_code == 400, duplicate_email.text
        assert duplicate_email.json()["code"] == 4002
    finally:
        client.close()
        engine.dispose()


def test_create_role_api():
    """验证管理员创建角色接口。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.post(
            "/roles",
            json={"name": "editor", "description": "编辑角色"},
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["name"] == "editor"
        assert data["description"] == "编辑角色"
    finally:
        client.close()
        engine.dispose()


def test_create_role_api_duplicate_role():
    """验证创建重复角色时返回业务错误。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.post(
            "/roles",
            json={"name": "admin", "description": "系统管理员"},
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 400, response.text
        assert response.json()["code"] == 4006
    finally:
        client.close()
        engine.dispose()


def test_get_all_roles():
    """验证管理员查询全部角色接口。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.get(
            "/roles",
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        role_names = [item["name"] for item in data]
        assert "admin" in role_names
        assert "user" in role_names
    finally:
        client.close()
        engine.dispose()


def test_reset_password_by_self():
    """验证用户可以重置自己的密码。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="alice", email="alice@example.com")
        user_token = login(client, "alice", "Aa123456!")

        response = client.post(
            f"/roles/{user['id']}/reset-password",
            json="654321",
            headers=auth_headers(user_token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["message"] == "密码重置成功"

        bad_login = client.post(
            "/users/token",
            data={"username": "alice", "password": "Aa123456!"},
        )
        assert bad_login.status_code == 400, bad_login.text

        new_token = login(client, "alice", "654321")
        assert new_token
    finally:
        client.close()
        engine.dispose()


def test_reset_password_by_admin():
    """验证管理员可以重置其他用户密码。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="alice", email="alice@example.com")
        admin_token = login(client, "admin", "123456")

        response = client.post(
            f"/roles/{user['id']}/reset-password",
            json="654321",
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["message"] == "密码重置成功"

        new_token = login(client, "alice", "654321")
        assert new_token
    finally:
        client.close()
        engine.dispose()


def test_reset_password_permission_denied():
    """验证普通用户不能重置他人密码。"""
    client, engine = build_test_client()
    try:
        alice = create_user(client, username="alice", email="alice@example.com")
        bob = create_user(client, username="bob", email="bob@example.com")
        alice_token = login(client, "alice", "Aa123456!")

        response = client.post(
            f"/roles/{bob['id']}/reset-password",
            json="654321",
            headers=auth_headers(alice_token),
        )
        assert response.status_code == 403, response.text
        assert response.json()["code"] == 403
    finally:
        client.close()
        engine.dispose()


def test_reset_password_user_not_found():
    """验证重置不存在用户密码时返回 404。"""
    client, engine = build_test_client()
    try:
        admin_token = login(client, "admin", "123456")

        response = client.post(
            "/roles/999/reset-password",
            json="654321",
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 404, response.text
        assert response.json()["code"] == 404
    finally:
        client.close()
        engine.dispose()


def test_upload_avatar_success_with_png():
    """验证用户可上传 PNG 头像，并写入数据库。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="avatar_user", email="avatar_user@example.com")
        token = login(client, "avatar_user", "Aa123456!")

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.png", b"fake-png-bytes", "image/png")},
            headers=auth_headers(token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["code"] == 200

        with db_session.SessionLocal() as db:
            db_user = user_dao.get_user_by_id(db, user["id"])
            assert db_user.avatar_url is not None
            assert db_user.avatar_url.startswith("static/avatars/")
            assert db_user.avatar_url.endswith(".png")
            assert db_user.avatar_url != "static/avatars/default.jpg"
            assert (PROJECT_ROOT / db_user.avatar_url).exists()
    finally:
        client.close()
        engine.dispose()


def test_upload_avatar_reject_invalid_content_type():
    """验证上传非图片文件时返回 400。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="bad_file_user", email="bad_file_user@example.com")
        token = login(client, "bad_file_user", "Aa123456!")

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.txt", b"not-an-image", "text/plain")},
            headers=auth_headers(token),
        )
        assert response.status_code == 400, response.text
        assert response.json()["code"] == 400
    finally:
        client.close()
        engine.dispose()


def test_upload_avatar_reject_oversized_file():
    """验证上传超过 2MB 的文件时返回 400。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="large_file_user", email="large_file_user@example.com")
        token = login(client, "large_file_user", "Aa123456!")
        large_content = b"a" * (2 * 1024 * 1024 + 1)

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.jpg", large_content, "image/jpeg")},
            headers=auth_headers(token),
        )
        assert response.status_code == 400, response.text
        assert response.json()["code"] == 400
    finally:
        client.close()
        engine.dispose()
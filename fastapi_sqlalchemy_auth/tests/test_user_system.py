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
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
# 测试环境关闭登录限流，避免批量用例触发 429。
os.environ.setdefault("TESTING", "1")
os.environ.setdefault(
    "TEST_SQLALCHEMY_DATABASE_URL",
    "mysql+pymysql://root:hejie%402244@127.0.0.1:3306/fastapi_test?charset=utf8mb4",
)

import main
import utils.file_utils as file_utils
from config import get_settings
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
    test_database_url = os.environ["TEST_SQLALCHEMY_DATABASE_URL"]
    if test_database_url.startswith("sqlite:///") and db_path.exists():
        logger.info(f"删除遗留测试数据库: path={db_path}")
        db_path.unlink()
    cleanup_test_avatars()


def teardown_module():
    """测试模块结束后清理测试库。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    test_database_url = os.environ["TEST_SQLALCHEMY_DATABASE_URL"]
    if test_database_url.startswith("sqlite:///") and db_path.exists():
        logger.info(f"清理测试数据库: path={db_path}")
        db_path.unlink()
    cleanup_test_avatars()


def build_test_client():
    """构建独立测试库和 TestClient。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    test_database_url = os.environ["TEST_SQLALCHEMY_DATABASE_URL"]
    logger.info(f"构建测试客户端: database_url={test_database_url}")
    # test_engine = create_engine(
    #     f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    # )
    test_engine = create_engine(test_database_url, pool_pre_ping=True)
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    db_session.engine = test_engine
    db_session.SessionLocal = testing_session_local
    main.engine = test_engine
    main.SessionLocal = testing_session_local
    get_settings.cache_clear()

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


def login_response(client: TestClient, username: str, password: str) -> dict:
    """执行登录并返回完整响应数据。"""
    logger.info(f"测试登录: username={username}")
    response = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    logger.success(f"测试登录成功: username={username}")
    return data


def login(client: TestClient, username: str, password: str) -> tuple[str, str]:
    """执行登录并返回访问令牌和刷新令牌。"""
    data = login_response(client, username, password)
    return data["access_token"], data["refresh_token"]


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
        access_token, _ = login(client, "alice", "Aa123456!")

        get_response = client.get(
            f"/users/{created_user['id']}",
            headers=auth_headers(access_token),
        )
        assert get_response.status_code == 200, get_response.text
        assert get_response.json()["data"]["username"] == "alice"
        assert get_response.json()["data"]["role"] == "user"

        update_response = client.put(
            f"/users/{created_user['id']}",
            json={"age": 20, "email": "alice.updated@example.com"},
            headers=auth_headers(access_token),
        )
        assert update_response.status_code == 200, update_response.text
        assert update_response.json()["data"]["age"] == 20
        assert update_response.json()["data"]["email"] == "alice.updated@example.com"
    finally:
        client.close()
        engine.dispose()


def test_login_and_refresh_flow():
    """验证登录返回 token 和当前用户信息，并可刷新 access token。"""
    client, engine = build_test_client()
    try:
        create_user(client)
        login_data = login_response(client, "alice", "Aa123456!")
        assert login_data["access_token"]
        assert login_data["refresh_token"]
        assert login_data["token_type"] == "bearer"
        assert login_data["user"]["username"] == "alice"
        assert login_data["user"]["role"] == "user"

        refresh_response = client.post(
            "/users/auth/refresh",
            json={"refresh_token": login_data["refresh_token"]},
        )
        assert refresh_response.status_code == 200, refresh_response.text
        refresh_data = refresh_response.json()["data"]
        assert refresh_data["access_token"]
        assert refresh_data["token_type"] == "bearer"
    finally:
        client.close()
        engine.dispose()


def test_get_current_user_profile():
    """验证可通过 token 获取当前登录用户信息。"""
    client, engine = build_test_client()
    try:
        create_user(client)
        access_token, _ = login(client, "alice", "Aa123456!")

        response = client.get(
            "/users/me",
            headers=auth_headers(access_token),
        )
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["username"] == "alice"
        assert data["role"] == "user"
    finally:
        client.close()
        engine.dispose()


def test_swagger_oauth2_token_endpoint():
    """验证 Swagger OAuth2 标准 token 接口。"""
    client, engine = build_test_client()
    try:
        create_user(client)

        response = client.post(
            "/users/token",
            data={"username": "alice", "password": "Aa123456!"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["access_token"]
        assert data["token_type"] == "bearer"
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
            "/users/login",
            json={"username": "alice", "password": "wrong-password"},
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
        user_access_token, _ = login(client, "alice", "Aa123456!")
        admin_access_token, _ = login(client, "admin", "123456")

        forbidden_role_update = client.put(
            f"/users/{user['id']}",
            json={"role_id": 1},
            headers=auth_headers(user_access_token),
        )
        assert forbidden_role_update.status_code == 403, forbidden_role_update.text
        assert forbidden_role_update.json()["code"] == 4004

        list_response = client.get(
            "/users?page=1&page_size=10",
            headers=auth_headers(admin_access_token),
        )
        assert list_response.status_code == 200, list_response.text
        list_data = list_response.json()["data"]
        assert list_data["total"] == 2
        assert len(list_data["items"]) == 2

        search_response = client.get(
            "/users/search/?keyword=alice",
            headers=auth_headers(admin_access_token),
        )
        assert search_response.status_code == 200, search_response.text
        assert len(search_response.json()["data"]) == 1

        delete_admin = client.delete(
            "/users/1",
            headers=auth_headers(admin_access_token),
        )
        assert delete_admin.status_code == 403, delete_admin.text
        assert delete_admin.json()["code"] == 4003

        delete_user_response = client.delete(
            f"/users/{user['id']}",
            headers=auth_headers(admin_access_token),
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
        admin_access_token, _ = login(client, "admin", "123456")

        response = client.post(
            "/roles/admin/users",
            json={
                "username": "boss2",
                "password": "Aa123456!",
                "age": 35,
                "email": "boss2@example.com",
            },
            headers=auth_headers(admin_access_token),
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
        admin_access_token, _ = login(client, "admin", "123456")
        create_user(client, username="alice", email="alice@example.com")

        duplicate_username = client.post(
            "/roles/admin/users",
            json={
                "username": "alice",
                "password": "Aa123456!",
                "age": 28,
                "email": "alice_admin@example.com",
            },
            headers=auth_headers(admin_access_token),
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
            headers=auth_headers(admin_access_token),
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
        admin_access_token, _ = login(client, "admin", "123456")

        response = client.post(
            "/roles",
            json={"name": "editor", "description": "编辑角色"},
            headers=auth_headers(admin_access_token),
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
        admin_access_token, _ = login(client, "admin", "123456")

        response = client.post(
            "/roles",
            json={"name": "admin", "description": "系统管理员"},
            headers=auth_headers(admin_access_token),
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
        admin_access_token, _ = login(client, "admin", "123456")

        response = client.get(
            "/roles",
            headers=auth_headers(admin_access_token),
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
        user_access_token, _ = login(client, "alice", "Aa123456!")

        response = client.post(
            f"/users/{user['id']}/reset-password",
            json={"password": "Aa123456!", "new_password": "Bb123456!"},
            headers=auth_headers(user_access_token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["message"] == "密码重置成功"

        bad_login = client.post(
            "/users/login",
            json={"username": "alice", "password": "Aa123456!"},
        )
        assert bad_login.status_code == 400, bad_login.text

        new_access_token, _ = login(client, "alice", "Bb123456!")
        assert new_access_token
    finally:
        client.close()
        engine.dispose()


def test_reset_password_by_admin():
    """验证管理员可以重置其他用户密码。"""
    client, engine = build_test_client()
    try:
        user = create_user(client, username="alice", email="alice@example.com")
        admin_access_token, _ = login(client, "admin", "123456")

        response = client.post(
            f"/users/{user['id']}/reset-password",
            json={"password": "Aa123456!", "new_password": "Bb123456!"},
            headers=auth_headers(admin_access_token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["message"] == "密码重置成功"

        new_access_token, _ = login(client, "alice", "Bb123456!")
        assert new_access_token
    finally:
        client.close()
        engine.dispose()


def test_reset_password_permission_denied():
    """验证普通用户不能重置他人密码。"""
    client, engine = build_test_client()
    try:
        create_user(client, username="alice", email="alice@example.com")
        bob = create_user(client, username="bob", email="bob@example.com")
        alice_access_token, _ = login(client, "alice", "Aa123456!")

        response = client.post(
            f"/users/{bob['id']}/reset-password",
            json={"password": "whatever123", "new_password": "654321"},
            headers=auth_headers(alice_access_token),
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
        admin_access_token, _ = login(client, "admin", "123456")

        response = client.post(
            "/users/999/reset-password",
            json={"password": "123456", "new_password": "654321"},
            headers=auth_headers(admin_access_token),
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
        access_token, _ = login(client, "avatar_user", "Aa123456!")

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.png", b"fake-png-bytes", "image/png")},
            headers=auth_headers(access_token),
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
        access_token, _ = login(client, "bad_file_user", "Aa123456!")

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.txt", b"not-an-image", "text/plain")},
            headers=auth_headers(access_token),
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
        access_token, _ = login(client, "large_file_user", "Aa123456!")
        large_content = b"a" * (2 * 1024 * 1024 + 1)

        response = client.post(
            f"/users/{user['id']}/avatar",
            files={"file": ("avatar.jpg", large_content, "image/jpeg")},
            headers=auth_headers(access_token),
        )
        assert response.status_code == 400, response.text
        assert response.json()["code"] == 400
    finally:
        client.close()
        engine.dispose()



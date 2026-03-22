import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.logger import get_logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("SECRET_KEY", "test-secret-key")

import main
from dao import role_dao, user_dao
from schemas import UserCreate
from session import db_session
from session.db_session import Base

logger = get_logger()


def setup_module():
    """测试模块启动前清理遗留测试库。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    if db_path.exists():
        logger.info(f"删除遗留测试数据库: path={db_path}")
        db_path.unlink()


def teardown_module():
    """测试模块结束后清理测试库。"""
    db_path = PROJECT_ROOT / "tests" / "_test_user_system.db"
    if db_path.exists():
        logger.info(f"清理测试数据库: path={db_path}")
        db_path.unlink()


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
    password: str = "123456",
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
        token = login(client, "alice", "123456")

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
                "password": "123456",
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
                "password": "123456",
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
        user_token = login(client, "alice", "123456")
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

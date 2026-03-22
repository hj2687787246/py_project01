# FastAPI 分层项目说明

## 目录结构

```text
Depends + SQLAlchemy 2 分层/
├─ core/                    # 核心能力：日志
├─ dao/                     # 数据访问层
├─ models/                  # ORM 模型
├─ routers/                 # 路由层
├─ schemas/                 # 请求 / 响应模型
├─ session/                 # 数据库连接与会话
├─ tests/                   # 集成测试脚本
├─ utils/                   # 密码、JWT、安全依赖
├─ .env.example             # 环境变量示例
├─ fastapi_test.db          # SQLite 数据库
├─ main.py                  # 应用入口
└─ requirements.txt
```

## 分层职责

### `routers`
- 定义接口
- 接收参数
- 做权限判断和业务流程编排

### `dao`
- 只负责数据库增删改查
- 不直接处理接口响应格式

### `models`
- 定义 SQLAlchemy ORM 模型

### `schemas`
- 定义 Pydantic 请求体和响应体
- 统一响应格式使用 `UnifiedResponse`

### `session`
- 管理数据库连接、`engine`、`SessionLocal`、`get_db`

### `utils`
- 放密码哈希、JWT、当前用户 / 管理员依赖

### `core`
- 放日志等基础能力

## 功能说明

当前已完成：
- 用户注册
- 用户登录
- JWT 鉴权
- 用户查询 / 更新
- 管理员分页 / 搜索 / 删除
- 禁止删除 `admin` 角色账号
- 时间统一按 UTC 存储、按北京时间返回
- 统一异常响应格式

## 异常处理设计

项目同时保留两类异常：

### `HTTPException`
- 用于通用 HTTP 语义错误
- 例如：登录失败、未认证、权限不足、资源不存在

### `BusinessException`
- 用于业务规则错误
- 例如：用户名重复、邮箱重复、普通用户修改角色、删除 `admin` 账号

两类异常最终都会被全局异常处理器包装成统一格式：

```json
{
  "code": 4001,
  "message": "用户名已存在",
  "data": null
}
```

区别在于：
- `HTTPException` 的 `code` 直接等于 HTTP 状态码
- `BusinessException` 的 `code` 是更细粒度的业务码

当前业务码约定：
- `4001` 用户名已存在 / 用户名已被占用
- `4002` 邮箱已存在 / 邮箱已被占用
- `4003` 不能删除 `admin` 角色账号
- `4004` 无权修改用户角色

## 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 `.env`

复制示例文件后至少配置：

```env
SECRET_KEY=replace-with-your-secret-key
```

可用下面命令生成随机密钥：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 启动方式

在当前目录执行：

```bash
uvicorn main:app --reload
```

默认地址：

```text
http://127.0.0.1:8000
```

## 测试方式

先安装测试依赖：

```bash
pip install -r requirements.txt
```

然后在项目目录下执行：

```bash
pytest tests/test_user_system.py -q
```

当前 `pytest` 集成测试会覆盖：
- 基础注册 / 登录 / 查询 / 更新流程
- `BusinessException` 响应验证
  - 用户名重复
  - 邮箱重复
  - 普通用户修改角色
  - 删除 `admin` 账号
- `HTTPException` 响应验证
  - 登录失败
  - 缺少 Token

## 当前响应策略

### 成功响应

成功接口返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 异常响应

#### `BusinessException`

保留真实 HTTP 状态码，同时返回业务码：

```json
{
  "code": 4003,
  "message": "不能删除admin角色账号",
  "data": null
}
```

#### `HTTPException`

保留真实 HTTP 状态码，同时统一包装：

```json
{
  "code": 401,
  "message": "Not authenticated",
  "data": null
}
```

## 开发约定

- 不要在 DAO 层写权限判断
- 不要在路由层直接写 SQL
- 业务规则错误优先考虑 `BusinessException`
- 通用 HTTP 错误优先使用 `HTTPException`
- 修改测试时，注意测试数据是否真的构成“重复”或“无权限”场景

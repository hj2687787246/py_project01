# FastAPI 标准分层说明

## 目录结构

```text
Depends + SQLAlchemy 2 分层/
├─ app/
│  ├─ main.py                # 应用入口
│  ├─ config/                # 配置层
│  ├─ core/                  # 核心能力：日志、安全
│  ├─ db/                    # 数据库连接、Base、ORM 模型
│  ├─ deps/                  # 通用依赖：会话、认证、权限
│  ├─ dao/                   # 数据访问层
│  ├─ services/              # 业务逻辑层
│  ├─ schemas/               # 请求/响应模型
│  ├─ api/                   # 路由层
│  └─ utils/                 # 通用工具
├─ tests/                    # 集成测试脚本
├─ .env.example              # 环境变量示例
├─ fastapi_test.db           # SQLite 数据库
├─ main.py                   # 根入口，供 uvicorn 启动
└─ requirements.txt
```

## 分层职责

### `config`
- 管理环境变量和项目配置
- 例如：`DATABASE_URL`、`SECRET_KEY`、Token 过期时间

### `db`
- 管理数据库连接和 ORM 基础设施
- `session.py`：`engine`、`SessionLocal`、`get_db`
- `models/`：数据库表模型

### `dao`
- 只负责直接操作数据库
- 编写 `select / insert / update / delete`
- 不处理复杂业务规则

### `services`
- 负责业务逻辑
- 调用 DAO
- 处理规则校验、数据组装、业务流程

### `api/routes`
- 负责定义接口
- 接收参数、调用 service、返回响应
- 不直接写 SQL

### `deps`
- 负责可复用依赖
- 例如：`get_db`、`get_current_user`、`get_current_admin`

### `core`
- 放项目基础能力
- 例如：日志、JWT、安全相关核心逻辑

### `schemas`
- 定义请求体和响应体
- 使用 Pydantic 做参数校验和序列化

## 启动方式

### 1. 创建 `.env`

复制环境变量模板：

```bash
copy .env .env
```

至少配置：

```env
SECRET_KEY=replace-with-your-secret-key
```

### 2. 启动服务

```bash
uvicorn main:app --reload
```

## 测试方式

启动服务后执行：

```bash
python tests/test_user_system.py
```

## 开发约定

### 新增模型
1. 在 `app/db/models/` 下新增模型文件
2. 在 `app/schemas/` 下新增对应请求/响应模型
3. 在 `app/dao/` 下新增 DAO
4. 在 `app/services/` 下新增业务逻辑
5. 在 `app/api/routes/` 下新增路由

### 不建议做的事
- 不要在路由层直接写 SQL
- 不要在 DAO 层写权限判断
- 不要把配置写死在代码里
- 不要把日志、认证、数据库逻辑全部堆进一个文件

## 当前模块

当前已完成：
- 用户注册
- 用户登录
- JWT 鉴权
- 用户查询 / 更新
- 管理员分页 / 搜索 / 删除
- 日志记录
- 时间统一按 UTC 存储、按北京时间返回

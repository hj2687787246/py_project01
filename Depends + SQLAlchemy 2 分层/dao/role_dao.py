from typing import Optional
from sqlalchemy.orm import Session

from core.exceptions import BusinessException
from models.role import Role

# 获取角色名称
def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """根据角色名查询角色。"""
    return db.query(Role).filter(Role.name == name).first()

# 新增角色
def create_role(db: Session, name: str, description: str | None = None) -> Role:
    """创建角色并写入数据库。"""
    db_role = Role(name=name, description=description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# 查重后新增角色
def create_role_with_check(db: Session, name: str, description: str | None = None) -> Role:
    """先校验是否重复，再创建角色。"""
    db_role = get_role_by_name(db, name)
    if db_role:
        raise BusinessException(400, 4006, "该角色已存在")
    return create_role(db, name, description)

# 获取所有角色信息
def get_all_roles(db: Session) -> list[type[Role]]:
    """查询全部角色。"""
    return db.query(Role).all()
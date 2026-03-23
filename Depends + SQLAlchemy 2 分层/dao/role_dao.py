from typing import List, Optional

from sqlalchemy.orm import Session

import models
from core.exceptions import BusinessException
from models.role import Role

# 获取角色名称
def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name).first()

# 新增角色
def create_role(db: Session, name: str, description: str | None = None) -> Role:
    # 这里只负责角色落库，不处理是否重复等业务校验。
    db_role = Role(name=name, description=description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def create_role_with_check(db: Session, name: str, description: str | None = None) -> Role:
    # 这个方法给 service 层用，统一封装“查重后创建”的数据库流程。
    db_role = get_role_by_name(db, name)
    if db_role:
        raise BusinessException(400, 4006, "该角色已存在")
    return create_role(db, name, description)

# 获取所有角色信息
def get_all_roles(db: Session) -> List[models.Role]:
    return db.query(models.Role).all()

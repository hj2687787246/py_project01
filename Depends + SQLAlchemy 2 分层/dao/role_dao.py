from sqlalchemy.orm import Session

from models.role import Role


def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()


def create_role(db: Session, name: str, description: str = None):
    # 创建角色（仅用于初始化测试数据）
    db_role = Role(name=name,description=description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

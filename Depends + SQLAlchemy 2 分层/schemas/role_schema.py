from typing import Optional
from pydantic import BaseModel, ConfigDict

class RoleBase(BaseModel):
    """角色基础模型。"""

    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """创建角色请求模型。"""

    pass

class RoleResponse(RoleBase):
    """角色响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int

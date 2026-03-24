from typing import Optional
from pydantic import BaseModel, ConfigDict,Field

class RoleBase(BaseModel):
    """角色基础模型。"""

    name: str = Field(min_length=3,max_length=50,description="角色名")
    description: Optional[str] = Field(min_length=3,max_length=50,description="角色描述")

class RoleCreate(RoleBase):
    """创建角色请求模型。"""

    pass

class RoleResponse(RoleBase):
    """角色响应模型。"""
    # 模型配置 把「数据库模型层 (Model)」转换成「DTO」
    model_config = ConfigDict(from_attributes=True)

    id: int

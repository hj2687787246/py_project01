#子依赖（层级嵌套）
# 支持依赖之间的嵌套调用，比如「获取 token → 解析用户 → 权限校验」的完整链路：
from fastapi import FastAPI,Depends,HTTPException



# 第一层依赖：获取token
def get_token(token:str = None):
    if not token:
        raise HTTPException(status_code=401,detail="未携带token")
    return token
# 第二层依赖：依赖get_token:解析当前用户
def get_current_user(token:str = Depends(get_token)):
    user_db ={"admin":{"username":"admin","role":"admin"}}
    if token not in user_db:
        raise HTTPException(status_code=401,detail="token无效")
    return user_db[token]
app = FastAPI()

# 接口仅需注入最终阶段的用户依赖
@app.get("/users/me",summary="获取当前用户信息")
def get_me(current_user:dict = Depends(get_current_user)):
    return current_user
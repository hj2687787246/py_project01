import os
import time
from pathlib import Path

from fastapi import UploadFile, HTTPException

# 限制文件类型和大小
ALLOWED_TYPES = {"image/jpeg","image/png"}
MAX_SIZE = 2 * 1024 * 1024 #限制2MB文件大小

# 保存相对路径
STATIC_DIR = Path(__file__).resolve().parents[1] / "static" / "avatars"


def save_avatar(file: UploadFile,avatar_url) -> str:
    # 校验类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "只允许上传jpg/png图片")

    # 校验大小 2MB
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0) # 重置指针
    if size > MAX_SIZE:
        raise HTTPException(400,"图片大小不能超过2MB")

    # 时间戳命名
    suffix = Path(file.filename or "avatar.jpg").suffix or ".jpg"
    filename = f"{int(time.time() * 1000)}{suffix}"

    # 删除旧图片
    if not avatar_url == "static/avatars/default.jpg":
        static = Path(__file__).resolve().parents[1]
        # 删除该图片
        file_path = static / avatar_url
        if file_path.exists():
            file_path.unlink()
    # 保存文件
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    file_path = STATIC_DIR / filename
    with open(file_path,"wb") as f:
        f.write(file.file.read())

    return f"static/avatars/{filename}"
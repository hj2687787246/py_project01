"""
递归练习：递归查找文件/目录

目标：
1) 练习“递归”思想：目录里还有目录 -> 一层层往下走
2) 实战：在指定目录下递归查找满足条件的文件（如 .txt）

本文件提供两种常用写法：
- 手写递归（更适合练习递归）
- pathlib.rglob / os.walk（更适合实际开发）
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import sys


@dataclass(frozen=True)
class FindOptions:
    suffix: str | None = ".txt"  # 只找某种后缀；传 None 表示不过滤
    name_contains: str | None = None  # 文件名包含某个关键字（不含路径）
    case_sensitive: bool = False


def _name_match(filename: str, options: FindOptions) -> bool:
    if options.suffix is not None and not filename.endswith(options.suffix):
        return False

    if options.name_contains:
        if options.case_sensitive:
            return options.name_contains in filename
        return options.name_contains.lower() in filename.lower()

    return True


def find_files_recursive(root: Path, options: FindOptions | None = None) -> list[Path]:
    """
    手写递归版：从 root 开始递归查找文件，返回所有匹配的文件路径。
    """
    options = options or FindOptions()
    root = root.resolve()

    results: list[Path] = []

    def walk(current: Path) -> None:
        # current 可能不存在/没有权限，做一层保护
        try:
            entries = list(current.iterdir())
        except (FileNotFoundError, PermissionError):
            return

        for entry in entries:
            if entry.is_dir():
                walk(entry)
            elif entry.is_file() and _name_match(entry.name, options):
                results.append(entry)

    walk(root)
    return results


def find_files_rglob(root: Path, options: FindOptions | None = None) -> list[Path]:
    """
    pathlib 版：用 rglob 递归查找（更简洁）。
    """
    options = options or FindOptions()
    root = root.resolve()

    if options.suffix is None:
        candidates = root.rglob("*")
    else:
        # 注意：rglob 支持通配符
        candidates = root.rglob(f"*{options.suffix}")

    results: list[Path] = []
    for p in candidates:
        if p.is_file() and _name_match(p.name, options):
            results.append(p)
    return results


def find_files_os_walk(root: Path, options: FindOptions | None = None) -> list[Path]:
    """
    os.walk 版：标准库自带的递归遍历（很常用）。
    """
    options = options or FindOptions()
    root = root.resolve()

    results: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            if _name_match(filename, options):
                results.append(Path(dirpath) / filename)
    return results


def _default_test_root() -> Path:
    # 方便直接运行：默认扫描同级的 test 目录
    return Path(__file__).parent / "test"


def main(argv: list[str]) -> int:
    """
    用法示例：
    - 直接运行（默认找 test 下的 .txt）
      python 第2章/补充/08.递归练习2.py

    - 指定目录
      python 第2章/补充/08.递归练习2.py "第2章/补充/test"

    - 只找包含关键字的 txt
      python 第2章/补充/08.递归练习2.py "第2章/补充/test" root

    - 找其他后缀（例如 .py）
      python 第2章/补充/08.递归练习2.py "第2章/补充" "" .py
    """
    root = Path(argv[1]) if len(argv) >= 2 and argv[1].strip() else _default_test_root()
    keyword = argv[2] if len(argv) >= 3 and argv[2].strip() else None
    suffix = argv[3] if len(argv) >= 4 and argv[3].strip() else ".txt"

    options = FindOptions(suffix=suffix, name_contains=keyword)

    print(f"Root: {root.resolve()}")
    print(f"Filter: suffix={options.suffix!r}, name_contains={options.name_contains!r}")

    # 1) 递归练习：手写递归
    files = find_files_recursive(root, options)
    print(f"\n[手写递归] Found {len(files)} files:")
    for p in sorted(files):
        print(p)

    # 2) 参考写法：rglob / os.walk
    files2 = find_files_rglob(root, options)
    print(f"\n[pathlib.rglob] Found {len(files2)} files.")

    files3 = find_files_os_walk(root, options)
    print(f"[os.walk] Found {len(files3)} files.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

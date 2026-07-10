#!/usr/bin/env python3
"""构建红楼梦 Wiki 的 MkDocs 静态站，并将严格构建作为可重复闸门。"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd):
    """执行命令，并返回完整输出以便统一写入证据日志。"""
    print(f"$ {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(result.stdout, end="")
    return result.returncode, result.stdout


def write_log_entry(log_handle, command, output, exit_code):
    """把已经执行过的命令和输出写入可追溯日志。"""
    log_handle.write(f"$ {' '.join(command)}\n")
    log_handle.write(output)
    log_handle.write(f"\nEXIT={exit_code}\n\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wiki-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Wiki 根目录（默认：本脚本所在 Wiki 根目录）",
    )
    parser.add_argument(
        "--log-output",
        type=Path,
        help="严格构建日志路径（默认：_mkdocs_build/mkdocs-strict-build.log）",
    )
    args = parser.parse_args()

    wiki_root = args.wiki_root.resolve()
    builder = wiki_root / "scripts" / "build_mkdocs.py"
    if not builder.is_file():
        print(f"ERROR: 未找到转换器：{builder}", file=sys.stderr)
        return 2

    mkdocs = shutil.which("mkdocs")
    if not mkdocs:
        print("ERROR: 未找到 mkdocs 命令，请先安装 MkDocs。", file=sys.stderr)
        return 2

    convert_command = [sys.executable, str(builder), str(wiki_root)]
    convert_exit, convert_output = run_command(convert_command, wiki_root)

    # 转换器会清空 _mkdocs_build/，所以日志只能在转换结束后才写入该目录。
    log_output = args.log_output or wiki_root / "_mkdocs_build" / "mkdocs-strict-build.log"
    log_output = log_output.resolve()
    log_output.parent.mkdir(parents=True, exist_ok=True)
    with log_output.open("w", encoding="utf-8") as log_handle:
        write_log_entry(log_handle, convert_command, convert_output, convert_exit)
        if convert_exit:
            print(f"MKDOCS_BUILD_CHECK: convert_exit={convert_exit} strict_exit=SKIPPED status=FAIL")
            print(f"MKDOCS_BUILD_LOG: {log_output}")
            return convert_exit

        # MkDocs 对 docs_dir: . 会按配置路径的书写形式解析；使用相对于 wiki_root 的
        # 配置路径，与转换器输出的命令保持一致，避免绝对路径触发 docs_dir 父目录校验。
        config = Path("_mkdocs_build/docs/mkdocs.yml")
        strict_command = [mkdocs, "build", "--strict", "-f", str(config)]
        strict_exit, strict_output = run_command(strict_command, wiki_root)
        write_log_entry(log_handle, strict_command, strict_output, strict_exit)

    result = "OK" if strict_exit == 0 else "FAIL"
    print(f"MKDOCS_BUILD_CHECK: convert_exit={convert_exit} strict_exit={strict_exit} status={result}")
    print(f"MKDOCS_BUILD_LOG: {log_output}")
    return strict_exit


if __name__ == "__main__":
    sys.exit(main())

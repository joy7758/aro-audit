from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import typer

app = typer.Typer(help="ARO/AAR 工具集：生成、校验、导出（v1.0）")


def _python_cmd() -> str:
    return sys.executable or "python"


def _to_arcname(path: Path) -> str:
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return path.name


def _write_verify_script(out_dir: Path, journal: str, pubkey: str) -> Path:
    script_path = out_dir / "verify.sh"
    content = (
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        f"tools/python sdk/verify/verify.py {shlex.quote(journal)} {shlex.quote(pubkey)}\n"
    )
    script_path.write_text(content, encoding="utf-8")
    os.chmod(script_path, 0o755)
    return script_path


def _write_packet_readme(out_dir: Path) -> Path:
    readme_path = out_dir / "README.txt"
    content = (
        "AAR/ALC 审计包（demo）\n\n"
        "包含：\n"
        "- journal.jsonl：事实源（JSONL，append-only）\n"
        "- AAR-Manifest.json：合规导出摘要（含 checkpoint 信息与复核命令）\n"
        "- org_pubkey_ed25519.pem：用于第三方独立验签的公钥\n"
        "- verify.sh：一键复核脚本（使用 tools/python + 公钥）\n\n"
        "复核方法：\n"
        "1) 激活虚拟环境（或确保有 python + 依赖）\n"
        "2) 执行：./verify.sh\n"
    )
    readme_path.write_text(content, encoding="utf-8")
    return readme_path


def _build_audit_packet(
    out_dir: Path,
    journal_path: Path,
    manifest_path: Path,
    verify_script_path: Path,
    readme_path: Path,
    pubkey_path: Path,
) -> Path:
    packet_path = out_dir / "audit_packet.zip"
    with ZipFile(packet_path, "w", compression=ZIP_DEFLATED) as zf:
        for path in (journal_path, manifest_path, verify_script_path, readme_path, pubkey_path):
            zf.write(path, arcname=_to_arcname(path))
    return packet_path

@app.command()
def gen_demo(
    out_dir: str = typer.Option("demo/out", help="输出目录"),
    checkpoint_every: int = typer.Option(4, help="checkpoint 间隔（demo 默认 4 方便观察）"),
):
    """
    生成 demo journal（事实源）+ 子密钥（如不存在则生成）
    """
    typer.echo("开始生成 demo journal...")
    # gen_journal.py 当前固定输出 demo/out，保留参数以保持 CLI 兼容。
    _ = out_dir, checkpoint_every
    cmd = [_python_cmd(), "demo/gen_journal.py"]
    rc = subprocess.run(cmd, shell=False).returncode
    if rc != 0:
        raise typer.Exit(code=rc)
    typer.echo(f"完成：{out_dir}/journal.jsonl")

@app.command()
def verify(
    journal: str = typer.Option("demo/out/journal.jsonl", help="journal.jsonl 路径"),
    key: str = typer.Option("demo/out/org_pubkey_ed25519.pem", help="ORG 公钥 pem 路径"),
):
    """
    校验 journal：链条 + checkpoint + 签名
    """
    typer.echo("开始校验...")
    cmd = [_python_cmd(), "sdk/verify/verify.py", journal, key]
    rc = subprocess.run(cmd, shell=False).returncode
    raise typer.Exit(code=rc)

@app.command()
def export(
    journal: str = typer.Option("demo/out/journal.jsonl", help="journal.jsonl 路径"),
    key: str = typer.Option("demo/out/org_pubkey_ed25519.pem", help="ORG 公钥 pem 路径"),
    out: str = typer.Option("demo/out/AAR-Manifest.json", help="manifest 输出路径"),
):
    """
    导出 Manifest（Compliance Export Kit）
    """
    typer.echo("开始导出 Manifest...")
    env = os.environ.copy()
    env["JOURNAL"] = journal
    env["KEY"] = key
    env["OUT"] = out
    cmd = [_python_cmd(), "pro/export/manifest.py"]
    rc = subprocess.run(cmd, env=env, shell=False).returncode
    if rc != 0:
        raise typer.Exit(code=rc)

    out_dir = Path(out).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    verify_path = _write_verify_script(out_dir, journal, key)
    readme_path = _write_packet_readme(out_dir)
    packet_path = _build_audit_packet(
        out_dir=out_dir,
        journal_path=Path(journal),
        manifest_path=Path(out),
        verify_script_path=verify_path,
        readme_path=readme_path,
        pubkey_path=Path(key),
    )
    typer.echo(f"完成：{out}")
    typer.echo(f"完成：{packet_path}")

if __name__ == "__main__":
    app()

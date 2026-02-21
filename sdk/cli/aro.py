from __future__ import annotations

import os
import sys
import typer

app = typer.Typer(help="ARO/AAR 工具集：生成、校验、导出（v1.0）")

@app.command()
def gen_demo(
    out_dir: str = typer.Option("demo/out", help="输出目录"),
    checkpoint_every: int = typer.Option(4, help="checkpoint 间隔（demo 默认 4 方便观察）"),
):
    """
    生成 demo journal（事实源）+ 子密钥（如不存在则生成）
    """
    # 延迟导入，避免 CLI 启动时路径问题
    from demo.gen_journal import main as gen_main
    # gen_journal.py 已写死输出路径 demo/out/journal.jsonl；这里保持一致
    typer.echo("开始生成 demo journal...")
    rc = gen_main()
    if rc != 0:
        raise typer.Exit(code=rc)
    typer.echo(f"完成：{out_dir}/journal.jsonl")

@app.command()
def verify(
    journal: str = typer.Option("demo/out/journal.jsonl", help="journal.jsonl 路径"),
    key: str = typer.Option("demo/out/org_subkey_ed25519.pem", help="ORG 子密钥 pem 路径"),
):
    """
    校验 journal：链条 + checkpoint + 签名
    """
    from sdk.verify.verify import main as verify_main
    typer.echo("开始校验...")
    rc = verify_main.__wrapped__([journal, key]) if hasattr(verify_main, "__wrapped__") else None
    # 兼容我们目前 verify.py 是脚本式 main；直接调用子进程最稳
    os.system(f'python sdk/verify/verify.py "{journal}" "{key}"')

@app.command()
def export(
    journal: str = typer.Option("demo/out/journal.jsonl", help="journal.jsonl 路径"),
    key: str = typer.Option("demo/out/org_subkey_ed25519.pem", help="ORG 子密钥 pem 路径"),
    out: str = typer.Option("demo/out/AAR-Manifest.json", help="manifest 输出路径"),
):
    """
    导出 Manifest（Compliance Export Kit）
    """
    typer.echo("开始导出 Manifest...")
    os.environ["JOURNAL"] = journal
    os.environ["KEY"] = key
    os.environ["OUT"] = out
    os.system("python pro/export/manifest.py")
    typer.echo(f"完成：{out}")

if __name__ == "__main__":
    app()

import os
import subprocess


def check_sovereignty() -> None:
    print("=== 开始主权环境安全审计 ===")

    # 1. 探测 Sudo 权限（看看你是不是这里的“隐形老板”）
    try:
        subprocess.check_call(["sudo", "-n", "true"], stderr=subprocess.DEVNULL)
        print("[!] 风险：发现免密 Sudo 权限！你已接管该机器逻辑层。")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("[+] 正常：未发现直接的免密 Sudo。")

    # 2. 探测 Docker 插座（看看有没有通往地基的后门）
    if os.path.exists("/var/run/docker.sock"):
        print("[!] 风险：发现 Docker Socket 暴露！可以实施物理层逃逸。")
    else:
        print("[+] 正常：未发现 Docker Socket 暴露。")

    # 3. 探测代谢残留（看看衣柜里有没有别人的“旧衣服”）
    try:
        result = subprocess.check_output(
            ["sudo", "docker", "images"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if "days ago" in result:
            print("[!] 风险：检测到陈旧镜像残留。环境并非瞬时销毁，存在跨任务泄露可能。")
        else:
            print("[+] 提示：镜像环境看起来比较干净。")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("[-] 提示：无法执行 Docker 扫描（可能权限不足）。")


if __name__ == "__main__":
    check_sovereignty()

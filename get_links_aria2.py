#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import requests
import subprocess
import os
import socket
import time

# ============ 配置区域 ============
API_URL = "https://hyp-api.mihoyo.com/hyp/hyp-connect/api/getGamePackages"
LAUNCHER_ID = "jGHBHlcOq1"

GAME_IDS = {
    "1": {"name": "崩坏：星穹铁道", "id": "64kMb5iAWu"},
    "2": {"name": "原神", "id": "1Z8W5NHUQb"},
    "3": {"name": "崩坏3", "id": "osvnlOc0S8"},
    "4": {"name": "绝区零", "id": "x6znKlJ0xK"},
}

# aria2 RPC 默认配置
ARIA2_RPC_DEFAULT = {
    "host": "127.0.0.1",
    "port": 6800,
    "secret": "",  # 如果设置了 RPC 密钥，请填写
}
# =================================


def fetch_game_packages(game_id):
    params = {
        "game_ids[]": game_id,
        "launcher_id": LAUNCHER_ID,
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        sys.exit(1)


def extract_urls(obj, url_set):
    if isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, str) and value.lower().startswith(('http://', 'https://')):
                url_set.add(value)
            else:
                extract_urls(value, url_set)
    elif isinstance(obj, list):
        for item in obj:
            extract_urls(item, url_set)


def check_aria2_local():
    """检测本地 aria2 是否可用（先查 PATH，再查默认安装路径）"""
    # 检查 PATH
    try:
        subprocess.run(["aria2c", "--version"], capture_output=True, check=True)
        return "command"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Windows 常见安装路径
    if sys.platform == "win32":
        common_paths = [
            "C:\\Program Files\\aria2\\aria2c.exe",
            "C:\\Program Files (x86)\\aria2\\aria2c.exe",
            os.path.expanduser("~\\scoop\\apps\\aria2\\current\\aria2c.exe"),
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path

    return None


def check_rpc_connectivity(host, port, secret=""):
    """测试 RPC 连接是否正常"""
    rpc_url = f"http://{host}:{port}/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "id": "ping",
        "method": "aria2.getVersion",
        "params": []
    }
    if secret:
        payload["params"] = [f"token:{secret}"]
    try:
        resp = requests.post(rpc_url, json=payload, timeout=5)
        if resp.status_code == 200:
            result = resp.json()
            if "result" in result:
                return True, rpc_url
            elif "error" in result and result["error"].get("code") == -32600:
                # 可能是需要 token
                return False, rpc_url
        return False, rpc_url
    except requests.exceptions.RequestException:
        return False, rpc_url


def discover_aria2_rpc():
    """自动发现 aria2 RPC 服务"""
    # 测试本地默认端口
    host = "127.0.0.1"
    port = 6800
    ok, url = check_rpc_connectivity(host, port)
    if ok:
        print(f"✅ 自动检测到本地 aria2 RPC 服务: {url}")
        return {"host": host, "port": port, "url": url, "secret": ""}

    # 尝试常见端口
    common_ports = [6800, 6888, 6999, 8080]
    for p in common_ports:
        if p == port:
            continue
        ok, url = check_rpc_connectivity(host, p)
        if ok:
            print(f"✅ 自动检测到本地 aria2 RPC 服务: {url}")
            return {"host": host, "port": p, "url": url, "secret": ""}

    return None


def get_aria2_rpc_config():
    """获取 aria2 RPC 配置（自动检测或手动输入）"""
    # 1. 尝试自动检测
    print("🔍 正在自动检测 aria2 RPC 服务...")
    detected = discover_aria2_rpc()
    if detected:
        use_detected = input(f"   使用自动检测到的服务？(y/n): ").strip().lower()
        if use_detected == 'y':
            return detected

    # 2. 手动输入
    print("\n📝 请手动输入 aria2 RPC 配置：")
    host = input(f"   RPC 主机 (默认 {ARIA2_RPC_DEFAULT['host']}): ").strip()
    if not host:
        host = ARIA2_RPC_DEFAULT['host']

    port = input(f"   RPC 端口 (默认 {ARIA2_RPC_DEFAULT['port']}): ").strip()
    if not port:
        port = ARIA2_RPC_DEFAULT['port']
    try:
        port = int(port)
    except ValueError:
        print("❌ 端口必须是数字，使用默认值 6800")
        port = 6800

    secret = input("   RPC 密钥 (没有则直接回车): ").strip()

    rpc_url = f"http://{host}:{port}/jsonrpc"

    # 验证连接
    print(f"\n🔗 正在测试连接到 {rpc_url} ...")
    ok, _ = check_rpc_connectivity(host, port, secret)
    if ok:
        print("✅ 连接成功")
        return {"host": host, "port": port, "url": rpc_url, "secret": secret}
    else:
        print("❌ 连接失败，请检查 aria2 RPC 是否已开启")
        retry = input("   是否重试？(y/n): ").strip().lower()
        if retry == 'y':
            return get_aria2_rpc_config()
        else:
            print("⚠️ 跳过下载")
            return None


def download_via_rpc(urls, rpc_config):
    """通过 RPC 批量添加下载任务"""
    if not urls:
        print("❌ 没有链接可下载")
        return False

    url_count = len(urls)
    print(f"\n🚀 正在通过 RPC 添加 {url_count} 个下载任务...")
    print(f"   RPC 地址: {rpc_config['url']}")

    success_count = 0
    fail_count = 0

    for idx, url in enumerate(sorted(urls), 1):
        # 构造 RPC 请求
        params = [[url]]
        if rpc_config['secret']:
            params.insert(0, f"token:{rpc_config['secret']}")

        payload = {
            "jsonrpc": "2.0",
            "id": f"task_{idx}",
            "method": "aria2.addUri",
            "params": params
        }

        try:
            resp = requests.post(rpc_config['url'], json=payload, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                if "result" in result:
                    print(f"  ✅ [{idx}/{url_count}] {url[:80]}...")
                    success_count += 1
                elif "error" in result:
                    error_msg = result["error"].get("message", "未知错误")
                    print(f"  ❌ [{idx}/{url_count}] {error_msg}")
                    fail_count += 1
            else:
                print(f"  ❌ [{idx}/{url_count}] HTTP {resp.status_code}")
                fail_count += 1
        except requests.exceptions.RequestException as e:
            print(f"  ❌ [{idx}/{url_count}] 请求失败: {e}")
            fail_count += 1

        # 避免请求过快
        if idx < url_count:
            time.sleep(0.1)

    print(f"\n📊 任务添加完成：成功 {success_count}，失败 {fail_count}")
    return success_count > 0


def download_with_aria2(urls_file, options):
    """本地 aria2 命令行下载（保留作为备选）"""
    if not os.path.exists(urls_file):
        print(f"❌ 文件 {urls_file} 不存在")
        return False

    cmd = ["aria2c", "-i", urls_file]
    cmd.extend(["-j", str(options["concurrent"])])
    cmd.extend(["-s", str(options["split"])])
    if options["dir"]:
        cmd.extend(["-d", options["dir"]])

    print(f"\n🚀 正在调用本地 aria2 下载，保存目录: {options['dir'] or '当前目录'}")
    print(f"   并发任务: {options['concurrent']}，分片: {options['split']}")

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 所有下载任务已完成")
        return True
    except KeyboardInterrupt:
        print("\n⏸️ 用户中断下载")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ aria2 运行出错: {e}")
        return False


def main():
    # 显示菜单
    print("🎮 请选择要获取下载链接的游戏：")
    for key, info in GAME_IDS.items():
        print(f"  {key}. {info['name']} (ID: {info['id']})")
    print("  q. 退出")

    choice = input("\n请输入数字: ").strip()

    if choice.lower() == 'q':
        print("👋 已退出")
        sys.exit(0)

    if choice not in GAME_IDS:
        print("❌ 无效选择")
        sys.exit(1)

    game_info = GAME_IDS[choice]
    game_name = game_info["name"]
    game_id = game_info["id"]

    print(f"\n📡 正在获取 {game_name} 的下载信息...")

    data = fetch_game_packages(game_id)

    if data.get("retcode") != 0:
        print(f"❌ API 返回错误: {data.get('message', '未知错误')}")
        sys.exit(1)

    urls = set()
    extract_urls(data, urls)

    if not urls:
        print("❌ 未找到任何下载链接")
        sys.exit(0)

    print(f"\n✅ 共找到 {len(urls)} 个下载链接：\n")
    for url in sorted(urls):
        print(url)

    # 保存到文件
    urls_file = "urls.txt"
    with open(urls_file, "w", encoding="utf-8") as f:
        for url in sorted(urls):
            f.write(url + "\n")
    print(f"\n💾 链接已保存到 {urls_file}")

    # 询问下载方式
    print("\n⬇️ 选择下载方式：")
    print("  1. 通过 RPC 添加任务（aria2 在远程/本机运行）")
    print("  2. 调用本地 aria2 命令行直接下载")
    print("  3. 仅保存链接，稍后手动下载")

    dl_choice = input("请选择 (1/2/3，默认 1): ").strip() or "1"

    if dl_choice == "1":
        # RPC 模式
        rpc_config = get_aria2_rpc_config()
        if rpc_config:
            download_via_rpc(urls, rpc_config)
        else:
            print("⚠️ 已跳过下载")

    elif dl_choice == "2":
        # 本地命令行模式
        aria2_cmd = check_aria2_local()
        if not aria2_cmd:
            print("❌ 未找到本地 aria2，请先安装 aria2 或使用 RPC 模式")
            print("   官网: https://aria2.github.io/")
            return
        # 使用默认下载配置
        options = {"concurrent": 5, "split": 16, "dir": "./downloads"}
        custom_dir = input(f"   请输入下载目录（回车使用默认 './downloads'）: ").strip()
        if custom_dir:
            options["dir"] = custom_dir
        download_with_aria2(urls_file, options)

    else:
        print("\nℹ️ 你可以稍后手动使用以下命令下载：")
        print(f"   aria2c -i {urls_file} -j 5")


if __name__ == "__main__":
    main()
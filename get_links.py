#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import requests

# ============ 配置区域 ============
# 官方 API 地址
API_URL = "https://hyp-api.mihoyo.com/hyp/hyp-connect/api/getGamePackages"

# 启动器 ID（固定）
LAUNCHER_ID = "jGHBHlcOq1"

# 游戏 ID 映射
GAME_IDS = {
    "1": {"name": "崩坏：星穹铁道", "id": "64kMb5iAWu"},
    "2": {"name": "原神", "id": "1Z8W5NHUQb"},
    "3": {"name": "崩坏3", "id": "osvnlOc0S8"},
    "4": {"name": "绝区零", "id": "x6znKlJ0xK"},
}
# =================================


def fetch_game_packages(game_id):
    """请求官方 API，获取 JSON 数据"""
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
    """递归提取所有 HTTP/HTTPS 链接"""
    if isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, str) and value.lower().startswith(('http://', 'https://')):
                url_set.add(value)
            else:
                extract_urls(value, url_set)
    elif isinstance(obj, list):
        for item in obj:
            extract_urls(item, url_set)


def main():
    # 显示游戏列表
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

    # 请求 API
    data = fetch_game_packages(game_id)

    # 检查返回码
    if data.get("retcode") != 0:
        print(f"❌ API 返回错误: {data.get('message', '未知错误')}")
        sys.exit(1)

    # 提取链接
    urls = set()
    extract_urls(data, urls)

    if not urls:
        print("❌ 未找到任何下载链接")
        sys.exit(0)

    # 输出结果
    print(f"\n✅ 共找到 {len(urls)} 个下载链接：\n")
    for url in sorted(urls):
        print(url)

    # 可选择保存到文件
    save = input("\n💾 是否保存到 urls.txt？(y/n): ").strip().lower()
    if save == 'y':
        with open("urls.txt", "w", encoding="utf-8") as f:
            for url in sorted(urls):
                f.write(url + "\n")
        print("✅ 已保存到 urls.txt")


if __name__ == "__main__":
    main()
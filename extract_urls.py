#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os

def extract_urls(obj, url_set):
    """
    递归遍历 JSON 对象，提取所有以 http:// 或 https:// 开头的字符串值。
    将链接存入 url_set（自动去重）。
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            # 如果值是字符串且以 http 开头，则添加
            if isinstance(value, str) and value.lower().startswith(('http://', 'https://')):
                url_set.add(value)
            else:
                # 否则递归处理该值
                extract_urls(value, url_set)
    elif isinstance(obj, list):
        for item in obj:
            extract_urls(item, url_set)
    # 其他类型（int, float, bool, None）忽略

def main():
    # 检查参数
    if len(sys.argv) < 2:
        print("用法: python extract_all_urls.py <json文件路径> [输出文件名]")
        print("示例: python extract_all_urls.py getGamePackages.json urls.txt")
        sys.exit(1)

    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "urls.txt"

    # 读取 JSON 文件
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件 '{json_file}' 不存在")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败 - {e}")
        sys.exit(1)

    # 提取所有链接
    urls = set()
    extract_urls(data, urls)

    if not urls:
        print("未找到任何有效的 URL")
        sys.exit(0)

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in sorted(urls):   # 排序便于查看
            f.write(url + '\n')

    print(f"✅ 已提取 {len(urls)} 个链接，保存到 '{output_file}'")
    print("\n你可以用以下命令批量下载：")
    print(f"  aria2c -i {output_file} -j 5")
    print(f"  wget -i {output_file}")
    print("\n如果配合比特彗星，可手动导入此文本文件。")

if __name__ == "__main__":
    main()
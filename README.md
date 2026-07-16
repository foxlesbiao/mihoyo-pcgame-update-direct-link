---

# 🎮 米哈游 PC 游戏更新包链接获取工具

一键获取米哈游 PC 游戏（原神、崩坏：星穹铁道、崩坏3、绝区零）的官方更新包下载链接，并支持通过 **aria2 RPC** 远程批量下载。

## ✨ 功能特点

- 🚀 **一键运行**：直接运行脚本，自动请求官方 API 获取最新下载信息
- 📋 **交互式菜单**：选择游戏，无需记忆复杂的游戏 ID
- 💾 **自动保存**：自动将链接保存到 `urls.txt` 文件
- 🔄 **实时获取**：每次运行都从官方服务器获取最新数据，无需手动保存 JSON
- 📦 **全部链接**：包含主包分卷、语音包、补丁包等所有资源链接
- 🌐 **远程下载支持**：支持通过 **aria2 RPC** 连接本机或远程 aria2 服务
- 🔍 **自动检测**：自动检测本机 aria2 RPC 服务（若 aria2 在本地运行）

## 📦 依赖

- Python 3.6+
- requests 库（用于 API 请求）

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 运行脚本

```bash
python get_links.py or get_links_aria2.py
```

### 3. 选择游戏

按提示输入对应数字选择要获取下载链接的游戏：

```
🎮 请选择要获取下载链接的游戏：
  1. 崩坏：星穹铁道 (ID: 64kMb5iAWu)
  2. 原神 (ID: 1Z8W5NHUQb)
  3. 崩坏3 (ID: osvnlOc0S8)
  4. 绝区零 (ID: x6znKlJ0xK)
  q. 退出

请输入数字: 1
```

### 4. 获取链接

脚本会自动请求官方 API 并输出所有下载链接：

```
✅ 共找到 22 个下载链接：

https://autopatchcn.bhsr.com/client/cn/20260703112555_FMCGg2vPuwTaJGyg/PC/Chinese.7z
https://autopatchcn.bhsr.com/client/cn/20260703112555_FMCGg2vPuwTaJGyg/PC/English.7z
...
```

### 5. 选择下载方式

获取链接后，脚本会询问下载方式：

```
⬇️ 选择下载方式：
  1. 通过 RPC 添加任务（aria2 在远程/本机运行）
  2. 调用本地 aria2 命令行直接下载
  3. 仅保存链接，稍后手动下载
请选择 (1/2/3，默认 1):
```

### 6. RPC 配置（如果选择方式 1）

脚本会**自动检测**本机 aria2 RPC 服务（默认 `127.0.0.1:6800`）：

```
🔍 正在自动检测 aria2 RPC 服务...
✅ 自动检测到本地 aria2 RPC 服务: http://127.0.0.1:6800/jsonrpc
   使用自动检测到的服务？(y/n): y
```

如果自动检测失败，可**手动输入**配置：

```
📝 请手动输入 aria2 RPC 配置：
  RPC 主机 (默认 127.0.0.1): 192.168.1.100
  RPC 端口 (默认 6800): 6800
  RPC 密钥 (没有则直接回车): your_secret_key
```

选择方式 2（本地命令行）时，需要 aria2 已安装并在 PATH 中。

## 📂 输出文件

- `urls.txt`：提取的所有下载链接，每行一个，兼容 aria2、wget 等工具。

## 🎯 支持的游戏

| 编号 | 游戏名称 | 游戏 ID |
|:---:|---------|--------|
| 1 | 崩坏：星穹铁道 | `64kMb5iAWu` |
| 2 | 原神 | `1Z8W5NHUQb` |
| 3 | 崩坏3 | `osvnlOc0S8` |
| 4 | 绝区零 | `x6znKlJ0xK` |

## 脚本解释
| 脚本 | 用途 |
|:---:|---------|
| extract_urls.py | 解析本地json |
| get_links.py | 不包含 aria2 |
| get_links_aria2.py | arai2 版本 |
## 🔧 高级用法

### 跳过菜单直接指定游戏

如果你希望直接指定游戏 ID（不经过菜单），可以在 `get_links.py` 末尾添加以下代码：

```python
if len(sys.argv) > 1:
    game_id = sys.argv[1]
    # 直接处理该 game_id，可自行扩展
```

### 自定义 aria2 RPC 配置

脚本中的 `ARIA2_RPC_DEFAULT` 字典可以修改默认主机、端口和密钥。

### 使用 aria2 命令行手动下载

如果不想用脚本的下载功能，也可以直接用生成的 `urls.txt`：

```bash
aria2c -i urls.txt -j 5
```

## 📡 技术原理

1. 向米哈游官方 API 发起请求：
   ```
   https://hyp-api.mihoyo.com/hyp/hyp-connect/api/getGamePackages
   ```

2. 参数说明：
   - `game_ids[]`：游戏 ID（如 `64kMb5iAWu`）
   - `launcher_id`：启动器 ID（固定为 `jGHBHlcOq1`）

3. 解析返回的 JSON 数据，提取所有 `http://` 或 `https://` 开头的链接

4. 通过 aria2 RPC 接口批量添加下载任务（可选）

## 📁 项目结构

```
.
├── get_links.py          # 主脚本
├── urls.txt              # 提取的链接（自动生成）
└── README.md             # 本文件
```

## ⚠️ 注意事项

- 所有链接来自米哈游官方 CDN，请遵守官方服务条款
- 链接有时效性，建议每次下载前重新运行脚本获取最新链接
- 部分游戏包体积较大（超过 100GB），请确保有足够的磁盘空间
- 下载大文件时建议使用支持断点续传的下载工具（如 aria2）
- 若使用 RPC 方式且 aria2 在远程，请确保防火墙允许 RPC 端口访问

## ❓ 常见问题

### 1. 脚本提示 "未找到 aria2 RPC 服务"

- 确认 aria2 是否已启动并开启 RPC（`--enable-rpc`）
- 检查防火墙是否开放了 RPC 端口（默认 6800）
- 尝试手动输入正确的 IP 和端口

### 2. 选择本地命令行模式时报错 "未找到 aria2c"

- 请先安装 aria2（官网 https://aria2.github.io/）
- 确保 aria2c 在系统 PATH 中

### 3. 下载任务添加成功但文件没有下载

- 检查 aria2 的下载目录是否有写入权限
- 查看 aria2 日志排查错误（如果 RPC 模式，可查看 aria2 控制台输出）

## 💡 推荐软件

- **[Aria2-Pro](https://github.com/p3terx/aria2-pro)**：轻量级多协议下载工具，支持多线程、BT、RPC 远程控制。本脚本已集成其 RPC 接口，可实现一键批量下载。

- **[Starward](https://github.com/Scighost/Starward)**：米哈游第三方 PC 启动器，支持原神、星穹铁道、崩坏3、绝区零，内置多账号切换、抽卡记录、游戏时长统计等功能。

## 📄 许可证

本工具仅供学习交流使用，请勿用于商业用途。

---

如有问题或建议，欢迎提 Issue 或 Pull Request。

---

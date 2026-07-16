# 🎮 米哈游 PC 游戏更新包链接获取工具

一键获取米哈游 PC 游戏（原神、崩坏：星穹铁道、崩坏3、绝区零）的官方更新包下载链接。

## ✨ 功能特点

- 🚀 **一键运行**：直接运行脚本，自动请求官方 API 获取最新下载信息
- 📋 **交互式菜单**：选择游戏，无需记忆复杂的游戏 ID
- 💾 **自动保存**：可选择将链接保存到 `urls.txt` 文件
- 🔄 **实时获取**：每次运行都从官方服务器获取最新数据，无需手动保存 JSON
- 📦 **全部链接**：包含主包分卷、语音包、补丁包等所有资源链接

## 📦 依赖

- Python 3.6+
- requests 库

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 运行脚本

```bash
python get_links.py
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

### 5. 保存到文件

根据需要选择是否将链接保存到 `urls.txt`：

```
💾 是否保存到 urls.txt？(y/n): y
✅ 已保存到 urls.txt
```

## 📂 输出格式

生成的 `urls.txt` 每行一个链接，兼容所有主流下载工具：

```bash
# aria2 下载（并发5个任务）
aria2c -i urls.txt -j 5

# wget 下载
wget -i urls.txt

# 比特彗星：文件 → 批量添加下载HTTP/FTP任务 → 选择 urls.txt
```

## 🎯 支持的游戏

| 编号 | 游戏名称 | 游戏 ID |
|:---:|---------|--------|
| 1 | 崩坏：星穹铁道 | `64kMb5iAWu` |
| 2 | 原神 | `1Z8W5NHUQb` |
| 3 | 崩坏3 | `osvnlOc0S8` |
| 4 | 绝区零 | `x6znKlJ0xK` |

## 🔧 高级用法

### 直接获取特定游戏（跳过菜单）

如果你需要直接指定游戏 ID，可以修改脚本添加命令行参数支持：

```python
# 在文件末尾添加
if len(sys.argv) > 1:
    game_id = sys.argv[1]
    # 直接处理该 game_id
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

## ⚠️ 注意事项

- 所有链接来自米哈游官方 CDN，请遵守官方服务条款
- 链接有时效性，建议每次下载前重新运行脚本获取最新链接
- 部分游戏包体积较大（超过 100GB），请确保有足够的磁盘空间
- 下载大文件时建议使用支持断点续传的下载工具（如 aria2）

## 📄 许可证

本工具仅供学习交流使用，请勿用于商业用途。

---

如果有任何问题或建议，欢迎提 Issue 或 Pull Request！

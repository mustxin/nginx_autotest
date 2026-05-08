# Nginx 白盒测试自动化框架

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-7.0+-blue.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一款基于 Python + pytest 的 Nginx 白盒测试自动化框架，采用数据与脚本分离的设计理念，支持跨平台运行（Windows/macOS/Linux）。

## 特性

- **数据-脚本分离**：测试用例使用 YAML 定义，测试逻辑使用 Python 实现
- **跨平台支持**：自动适配 Windows、macOS、Linux 系统
- **配置智能注入**：自动将测试配置注入 Nginx 配置文件
- **测试隔离**：每个测试模块自动备份和恢复 Nginx 配置
- **丰富的测试模块**：支持 add_header、location、proxy、server、server_name 等多种指令测试

## 目录结构

```
nginx_autotest/
├── comms/                    # 公共工具模块
│   ├── cmd_operate.py       # 命令执行封装
│   ├── constants.py         # 路径常量
│   ├── data_read.py         # YAML/INI 配置读取
│   ├── nginx_operate.py     # Nginx 操作（备份/恢复/重载）
│   └── platform_utils.py    # 跨平台工具
├── config/
│   └── config.ini           # Nginx 路径配置
├── test_data/               # 测试数据（YAML）
│   ├── add_header.yaml
│   ├── location.yaml
│   ├── proxy_set_header.yaml
│   ├── server.yaml
│   └── server_name.yaml
├── test_script/             # 测试脚本
│   ├── conftest.py         # pytest 全局夹具
│   ├── test_add_header.py
│   ├── test_location.py
│   ├── test_proxy_set_header.py
│   ├── test_server.py
│   └── test_server_name.py
├── CLAUDE.md               # 项目文档
└── README.md               # 本文件
```

## 快速开始

### 环境要求

- Python 3.8+
- Nginx 1.18+ (Windows/macOS/Linux)
- curl 命令行工具

### 安装依赖

```bash
pip install pytest pyyaml
```

### 配置 Nginx 路径

编辑 `config/config.ini`，根据你的系统配置 Nginx 路径：

**Windows:**
```ini
[nginx]
nginx_path = D:\Tools\nginx-1.30.0\conf\nginx.conf
nginx_bin_path = D:\Tools\nginx-1.30.0\nginx.exe
backup_path = D:\Tools\nginx-1.30.0\backup\
error_log_path = D:\Tools\nginx-1.30.0\logs\error.log
```

**macOS (Homebrew):**
```ini
[nginx]
nginx_path = /usr/local/etc/nginx/nginx.conf
nginx_bin_path = /usr/local/bin/nginx
backup_path = /usr/local/etc/nginx/backup/
error_log_path = /usr/local/var/log/nginx/error.log
```

**Linux:**
```ini
[nginx]
nginx_path = /etc/nginx/nginx.conf
nginx_bin_path = /usr/sbin/nginx
backup_path = /etc/nginx/backup/
error_log_path = /var/log/nginx/error.log
```

> 提示：如果 `config/config.ini` 不存在或配置项缺失，框架会自动使用平台默认值。

### 运行测试

```bash
# 运行所有测试
pytest test_script/ -v

# 运行特定测试模块
pytest test_script/test_add_header.py -v

# 运行特定测试用例
pytest test_script/test_add_header.py -v -k "add_header_001"

# 生成 HTML 测试报告
pytest test_script/ -v --html=reports/report.html
```

## 测试数据格式

测试用例使用 YAML 格式定义，示例如下：

```yaml
case_id_001:
  test_purpose: "验证基础功能-添加自定义请求头"
  pre_condition:
    - Nginx配置文件路径已知
    - 已备份原始配置文件
    - Nginx服务已启动
  config_content: |
    location /test_add_header {
      proxy_pass http://127.0.0.1:80;
      proxy_set_header X-Test-Header "test123";
    }
  operate_commands:
    - "nginx -t"
    - "nginx -s reload"
    - "curl -v http://localhost/test_add_header"
  expected_result:
    - "configuration file"
    - "test is successful"
```

## 支持的测试模块

| 模块 | 描述 | 测试文件 |
|------|------|----------|
| add_header | 添加响应头 | `test_add_header.py` |
| location | location 匹配规则 | `test_location.py` |
| proxy_set_header | 设置代理请求头 | `test_proxy_set_header.py` |
| proxy_pass_header | 代理响应头传递 | `test_proxy_pass_header.py` |
| grpc_set_header | gRPC 请求头设置 | `test_grpc_set_header.py` |
| server | server 块配置 | `test_server.py` |
| server_name | server_name 匹配 | `test_server_name.py` |

## 跨平台兼容性

框架自动检测操作系统并适配相应配置：

| 功能 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 路径分隔符 | `\` | `/` | `/` |
| Nginx 工作目录 | 需要设置 | 可选 | 可选 |
| 权限要求 | 无 | 可能需要 sudo | 需要 sudo |
| 重启命令 | nginx -s reload | sudo nginx -s reload | sudo systemctl restart nginx |

检查平台支持：

```python
from comms.platform_utils import get_platform, check_nginx_installed

print(get_platform())  # 'windows', 'linux', 或 'darwin'
print(check_nginx_installed())  # (True/False, 版本信息)
```

## 添加新测试模块

1. 在 `test_data/` 目录创建 YAML 测试数据文件
2. 在 `test_script/` 目录创建对应的测试脚本
3. 复制现有测试脚本模板，修改 YAML 文件名即可

## 注意事项

1. **权限问题**：Linux/macOS 下修改系统 Nginx 配置可能需要 `sudo` 权限
2. **端口冲突**：确保测试使用的端口（默认 80）未被占用
3. **配置备份**：框架会自动备份和恢复 Nginx 配置，但建议手动备份重要配置
4. **Nginx 版本**：不同 Nginx 版本的指令支持可能有所差异

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

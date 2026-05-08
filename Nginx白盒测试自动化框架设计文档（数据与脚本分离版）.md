# Nginx白盒测试自动化框架设计文档（数据与脚本分离版）

## 一、框架设计核心目标

1. 核心原则：**测试数据与测试脚本完全分离**，数据单独管理，脚本仅负责执行逻辑，降低维护成本，小白可快速修改数据、新增用例，无需修改脚本核心代码。

2. 适配性：完全匹配原有Nginx白盒测试用例（proxy\_set\_header、grpc\_set\_header等7大模块），可直接复用原有测试场景。

3. 易用性：简化操作步骤，提供一键执行入口，自动生成测试报告，小白可快速上手，无需深入掌握编程细节。

4. 可维护性：模块划分清晰，脚本复用性强，新增测试模块、修改测试场景时，仅需新增/修改数据文件，无需改动执行脚本。

5. 容错性：增加异常捕获（如Nginx配置错误、命令执行失败、端口占用），输出清晰报错信息，方便小白排查问题。

## 二、技术选型（小白友好，环境易搭建）

|组件类型|选型|选型理由（小白友好性）|
|---|---|---|
|编程语言|Python 3\.8\+|语法简单，上手快，第三方库丰富，环境搭建步骤少|
|测试框架|pytest|用例组织灵活，支持参数化（适配数据分离），一键执行，报错信息清晰|
|数据存储|YAML文件|格式简洁、易读，无需编程基础，小白可直接编辑（类似编辑文本）|
|命令执行|subprocess（Python内置库）|无需额外安装，可直接执行系统命令（如nginx \-t、curl）|
|测试报告|pytest\-html|一键生成HTML格式报告，直观显示用例执行结果（通过/失败/跳过），小白可直接打开查看|
|配置管理|configparser（Python内置库）|管理全局配置（如Nginx路径、端口、日志路径），集中修改，无需改动脚本|

## 三、框架整体结构（数据与脚本分离核心设计）

框架采用“分层设计\+数据分离”模式，整体结构清晰，各模块职责明确，目录结构如下（小白可直接复制搭建）：

```plain text
nginx_whitebox_auto_test/  # 框架根目录
├── config/                # 全局配置目录（单独管理配置，无需改脚本）
│   └── config.ini         # 全局配置文件（Nginx路径、端口、报告路径等）
├── test_data/             # 测试数据目录（核心：所有测试数据单独存放）
│   ├── proxy_set_header.yaml  # proxy_set_header模块测试数据
│   ├── grpc_set_header.yaml   # grpc_set_header模块测试数据
│   ├── proxy_pass_header.yaml # proxy_pass_header模块测试数据
│   ├── server.yaml            # server块测试数据
│   ├── server_name.yaml       # server_name测试数据
│   ├── location.yaml          # location测试数据
│   └── add_header.yaml        # add_header模块测试数据
├── test_script/           # 测试脚本目录（仅负责执行逻辑，不包含测试数据）
│   ├── conftest.py         # 全局夹具（前置/后置操作，如Nginx重启、配置备份）
│   ├── test_proxy_set_header.py  # proxy_set_header模块执行脚本
│   ├── test_grpc_set_header.py   # grpc_set_header模块执行脚本
│   ├── test_proxy_pass_header.py # proxy_pass_header模块执行脚本
│   ├── test_server.py            # server块执行脚本
│   ├── test_server_name.py       # server_name执行脚本
│   ├── test_location.py          # location执行脚本
│   └── test_add_header.py        # add_header模块执行脚本
├── common/                # 公共工具目录（复用代码，降低冗余）
│   ├── nginx_operate.py    # Nginx操作工具（重启、配置检查、配置恢复、日志查看）
│   ├── cmd_operate.py      # 命令执行工具（执行curl、nginx命令，捕获输出）
│   └── data_read.py        # 数据读取工具（读取YAML测试数据、config配置）
├── reports/               # 测试报告目录（自动生成，无需手动创建）
│   └── report.html        # 自动化测试报告（HTML格式，可直接打开）
├── backup/                # 配置备份目录（自动备份Nginx原始配置，测试后恢复）
└── run_test.py            # 一键执行入口（小白仅需运行此文件，无需执行复杂命令）
```

## 四、各模块详细设计（核心：数据与脚本分离）

### 4\.1 全局配置模块（config/config\.ini）

集中管理所有全局配置，小白可直接编辑，无需修改任何脚本，示例如下：

```ini
[nginx]
nginx_path = /etc/nginx/nginx.conf  # Nginx配置文件路径（小白根据自己环境修改）
nginx_bin_path = /usr/sbin/nginx    # Nginx可执行文件路径
backup_path = ./backup/             # 配置备份路径
error_log_path = /var/log/nginx/error.log  # Nginx错误日志路径

[test_env]
localhost = 127.0.0.1               # 本地IP（无需修改）
grpc_port = 8080                    # gRPC测试端口
python_server_port = 8000           # Python后端服务端口
nginx_default_port = 80             # Nginx默认端口

[report]
report_path = ./reports/            # 测试报告路径
report_name = report.html           # 测试报告名称
```

### 4\.2 测试数据模块（test\_data/xxx\.yaml）

核心模块，所有测试数据（用例ID、测试目的、前置条件、配置内容、操作命令、预期结果）均存放在YAML文件中，与脚本完全分离。小白可通过修改YAML文件新增、修改用例，无需改动脚本。

以proxy\_set\_header模块为例（test\_data/proxy\_set\_header\.yaml），格式如下（与原有手动用例完全对应）：

```yaml
# proxy_set_header模块测试数据
# 格式：用例ID: {测试目的, 前置条件, 配置内容, 操作命令, 预期结果}
proxy_set_header_001:
  test_purpose: 验证基础功能-添加请求头
  pre_condition: ["Nginx配置文件路径已知", "已备份原始配置文件"]
  config_content: |  # Nginx新增配置（直接复制到脚本，无需修改）
    location /test_add {
      proxy_pass http://127.0.0.1:80;
      proxy_set_header X-Test-Header "test123";
    }
  operate_commands:  # 执行命令（按顺序执行）
    - "nginx -t"
    - "nginx -s reload"
    - "curl -v http://localhost/test_add"
  expected_result:  # 预期结果（支持多条件匹配）
    - "nginx: configuration file ... test is successful"
    - "X-Test-Header: test123"

proxy_set_header_002:
  test_purpose: 验证基础功能-修改请求头
  pre_condition: ["Nginx配置文件路径已知", "已备份原始配置文件"]
  config_content: |
    location /test_modify {
      proxy_pass http://127.0.0.1:80;
      proxy_set_header Host "modified.host.com";
    }
  operate_commands:
    - "nginx -t"
    - "nginx -s reload"
    - "curl -v http://localhost/test_modify"
  expected_result:
    - "Host: modified.host.com"

# 其他用例按此格式依次添加，与原有手动用例一一对应
```

说明：所有测试模块（grpc\_set\_header、add\_header等）的YAML文件均按此格式编写，确保小白可统一编辑，无需学习新格式。

### 4\.3 公共工具模块（common/）

封装所有复用逻辑，脚本仅需调用工具函数，无需重复编写代码，降低维护成本，小白无需关注工具实现细节。

1. nginx\_operate\.py（Nginx操作工具）：封装Nginx核心操作，供所有脚本调用
        

    - backup\_nginx\_config\(\)：备份Nginx原始配置（测试前置操作）

    - restore\_nginx\_config\(\)：恢复Nginx原始配置（测试后置操作）

    - check\_nginx\_config\(\)：执行nginx \-t，检查配置语法

    - restart\_nginx\(\)：重启Nginx服务

    - add\_nginx\_config\(config\_content\)：向Nginx配置文件添加测试配置

    - read\_nginx\_error\_log\(\)：读取Nginx错误日志，用于异常排查

2. cmd\_operate\.py（命令执行工具）：封装系统命令执行，捕获输出和异常
        

    - run\_cmd\(cmd\)：执行指定命令，返回命令输出结果

    - check\_cmd\_result\(cmd, expected\)：检查命令输出是否包含预期结果

3. data\_read\.py（数据读取工具）：封装数据读取逻辑，脚本无需关注数据读取细节
        

    - read\_yaml\(file\_path\)：读取指定YAML测试数据文件，返回字典格式数据

    - read\_config\(section, option\)：读取config\.ini中的配置项

### 4\.4 测试脚本模块（test\_script/）

核心逻辑：仅负责“读取测试数据→调用工具执行操作→验证结果”，不包含任何硬编码测试数据，所有数据均从YAML文件读取。小白无需修改脚本，仅需维护YAML数据。

以proxy\_set\_header模块脚本为例（test\_script/test\_proxy\_set\_header\.py）：

```python
import pytest
from common.data_read import read_yaml, read_config
from common.nginx_operate import add_nginx_config, check_nginx_config, restart_nginx
from common.cmd_operate import run_cmd, check_cmd_result

# 读取当前模块测试数据（从YAML文件读取，无需硬编码）
test_data = read_yaml("../test_data/proxy_set_header.yaml")

# 读取全局配置
nginx_path = read_config("nginx", "nginx_path")

# 测试用例（参数化，自动遍历YAML中的所有用例）
@pytest.mark.parametrize("case_id, case_info", test_data.items())
def test_proxy_set_header(case_id, case_info, backup_nginx_config, restore_nginx_config):
    """proxy_set_header模块自动化测试用例"""
    try:
        # 1. 打印用例信息（方便调试）
        print(f"\n执行用例：{case_id} - {case_info['test_purpose']}")
        
        # 2. 前置条件检查（提示小白确认前置条件）
        print("前置条件：")
        for condition in case_info["pre_condition"]:
            print(f"  - {condition}")
        input("确认前置条件已满足，按Enter继续...")  # 小白确认后继续，避免操作失误
        
        # 3. 添加Nginx测试配置
        add_nginx_config(nginx_path, case_info["config_content"])
        
        # 4. 执行测试命令（按顺序执行）
        for cmd in case_info["operate_commands"]:
            print(f"执行命令：{cmd}")
            result = run_cmd(cmd)
            print(f"命令输出：{result}")
            
            # 5. 验证结果（匹配预期结果中的所有条件）
            for expected in case_info["expected_result"]:
                assert expected in result, f"结果验证失败！预期包含：{expected}，实际输出：{result}"
        
        # 6. 用例执行成功
        print(f"用例 {case_id} 执行成功！")
    
    except Exception as e:
        # 异常捕获，输出详细错误信息，方便小白排查
        print(f"用例 {case_id} 执行失败！错误信息：{str(e)}")
        # 读取Nginx错误日志，辅助排查
        error_log = read_nginx_error_log()
        print(f"Nginx错误日志（最新10行）：\n{error_log}")
        raise  # 抛出异常，让pytest标记用例失败
```

说明：

- 所有测试脚本（test\_grpc\_set\_header\.py、test\_add\_header\.py等）均按此格式编写，逻辑统一，小白可快速理解。

- 使用pytest参数化（@pytest\.mark\.parametrize），自动遍历YAML文件中的所有用例，无需手动编写循环。

- 集成前置/后置操作（backup\_nginx\_config、restore\_nginx\_config），自动备份和恢复Nginx配置，避免测试影响原有环境。

### 4\.5 全局夹具（test\_script/conftest\.py）

封装所有测试用例的公共前置/后置操作，无需在每个脚本中重复编写，小白无需关注夹具实现，仅需调用。

```python
import pytest
from common.nginx_operate import backup_nginx_config, restore_nginx_config

# 全局前置操作：所有用例执行前，备份Nginx原始配置
@pytest.fixture(scope="session", autouse=True)
def backup_nginx_config_fixture():
    backup_nginx_config()
    yield  # 执行测试用例
    # 全局后置操作：所有用例执行完成后，恢复Nginx原始配置
    restore_nginx_config()

# 模块级前置/后置操作（可选，根据需求添加）
@pytest.fixture(scope="module")
def module_fixture():
    print("\n=== 开始执行当前模块测试 ===")
    yield
    print("\n=== 当前模块测试执行完成 ===")
```

### 4\.6 一键执行入口（run\_test\.py）

小白核心操作文件，仅需运行此文件，即可一键执行所有测试用例，自动生成测试报告，无需执行复杂的pytest命令。

```python
import os
import pytest
from common.data_read import read_config

# 读取报告配置
report_path = read_config("report", "report_path")
report_name = read_config("report", "report_name")
full_report_path = os.path.join(report_path, report_name)

# 确保报告目录存在
if not os.path.exists(report_path):
    os.makedirs(report_path)

# 执行pytest，生成测试报告
print("=== 开始执行Nginx白盒自动化测试 ===")
print(f"测试报告将生成至：{full_report_path}")

# pytest执行命令（--html生成HTML报告，-v显示详细日志，--tb=short简化报错信息）
pytest.main([
    "test_script/",  # 执行所有测试脚本
    f"--html={full_report_path}",
    "-v",
    "--tb=short"
])

print(f"\n=== 测试执行完成！测试报告已生成：{full_report_path} ===")
print("提示：打开HTML报告，可查看详细执行结果（通过/失败/错误）")
```

## 五、框架使用步骤（小白友好版）

1. 环境搭建（仅需执行1次）
        

    - 安装Python 3\.8\+（官网下载，下一步下一步安装，勾选“Add Python to PATH”）。

    - 打开终端，执行命令安装依赖：`pip install pytest pytest\-html pyyaml`（一键安装所有依赖）。

    - 复制框架目录结构，创建对应的文件夹和文件（直接复制前面的目录结构，小白可手动创建）。

2. 配置修改（小白核心操作）
        

    - 修改`config/config\.ini`：根据自己的Nginx环境，修改nginx\_path、nginx\_bin\_path等配置（注释已说明，小白可对照修改）。

    - 完善`test\_data/`下的YAML文件：将原有手动用例按YAML格式补充完整（已提供示例，小白可复制粘贴修改）。

3. 执行测试（一键执行）
        

    - 打开终端，进入框架根目录（nginx\_whitebox\_auto\_test）。

    - 执行命令：`python run\_test\.py`，等待测试执行完成。

4. 查看结果
        

    - 测试完成后，打开`reports/report\.html`文件（双击即可打开）。

    - 报告中可查看所有用例的执行结果（通过/失败），失败用例会显示错误信息和Nginx日志，小白可对照排查。

## 六、维护说明（数据与脚本分离优势）

1. 新增用例：无需修改脚本，仅需在对应模块的YAML文件中，按格式新增一条用例数据（复制现有用例，修改内容即可）。

2. 修改用例：仅需修改YAML文件中的对应用例数据（如修改预期结果、配置内容），无需改动脚本。

3. 修改环境配置：仅需修改`config/config\.ini`，所有脚本自动读取最新配置，无需逐个修改脚本。

4. 新增测试模块：
        

    - 在`test\_data/`下新增对应模块的YAML文件（如test\_new\_module\.yaml）。

    - 在`test\_script/`下新增对应执行脚本（复制test\_proxy\_set\_header\.py，修改读取的YAML路径即可）。

## 七、小白注意事项

1. 执行测试前，务必备份Nginx原始配置（框架会自动备份，但建议小白手动再备份一次，避免意外）。

2. 修改YAML文件时，注意格式正确（缩进一致，冒号后加空格），否则会导致数据读取失败（报错会提示“YAML格式错误”）。

3. 若测试失败，优先查看终端输出的错误信息和Nginx错误日志，大部分问题是配置错误、端口占用或命令执行失败。

4. 测试完成后，框架会自动恢复Nginx原始配置，若中途中断测试，可手动执行`common/nginx\_operate\.py`中的restore\_nginx\_config\(\)函数恢复配置。

5. 若执行curl命令失败，检查本地Nginx是否正常启动，以及测试端口是否未被占用。

> （注：文档部分内容可能由 AI 生成）

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Nginx White-box Testing Automation Framework** (Nginx白盒测试自动化框架) that follows a data-script separation design. Test cases are defined in YAML files while test scripts handle execution logic only.

## Common Commands

### Run Tests

```bash
# Run all tests with HTML report
python run_test.py

# Run specific test module
pytest test_script/test_add_header.py -v

# Run specific test case by ID pattern
pytest test_script/test_add_header.py -v -k "add_header_001"

# Run with live output (no capture)
pytest test_script/test_add_header.py -v -s

# Run with detailed traceback
pytest test_script/ -v --tb=long
```

**Note:** The `run_test.py` entry point has a bug where it imports from `common.data_read` instead of `comms.data_read`. Use `pytest` commands directly or fix the import before using.

## Architecture Overview

### Data-Script Separation Design

The framework strictly separates test data from execution logic:

- **Test Data** (`test_data/*.yaml`): Contains test case ID, purpose, pre-conditions, Nginx config content, commands to execute, and expected results.
- **Test Scripts** (`test_script/test_*.py`): Only contain execution logic. They read YAML data and use shared utilities.
- **Shared Utilities** (`comms/`): Provide reusable functions for Nginx operations, command execution, and data reading.

### Key Modules

**`comms/` - Common Utilities**
- `nginx_operate.py`: Nginx operations (backup/restore config, check syntax, reload/restart)
- `cmd_operate.py`: Command execution wrappers
- `data_read.py`: YAML and INI config file parsers
- `constants.py`: Path constants and path helper functions

**`test_script/conftest.py`**
- Provides session-scoped pytest fixtures that automatically backup Nginx config before all tests and restore after completion.

**`config/config.ini`**
- Central configuration for Nginx paths, ports, and report settings. All scripts read from this file.

### Test Data Format

Each YAML file in `test_data/` follows this structure:

```yaml
case_id_001:
  test_purpose: "描述测试目的"
  pre_condition:
    - "前置条件1"
    - "前置条件2"
  config_content: |
    location /test {
      proxy_pass http://127.0.0.1:80;
      proxy_set_header X-Test "value";
    }
  operate_commands:
    - "nginx -t"
    - "nginx -s reload"
    - "curl -v http://localhost/test"
  expected_result:
    - "configuration file"
    - "test is successful"
```

### Test Execution Flow

1. `conftest.py` fixture backs up Nginx config before session starts
2. Test script reads YAML data via `read_yaml()`
3. `pytest.mark.parametrize` iterates over all cases in YAML
4. For each case:
   - `add_nginx_config()` injects config content into Nginx config
   - `check_nginx_config()` runs `nginx -t`
   - `reload_nginx()` applies changes
   - `run_cmd()` executes test commands (curl, etc.)
   - Assertions verify expected strings in output
5. Fixture restores original Nginx config after session ends

## Important Implementation Details

### Path Management

Use constants from `comms.constants` instead of hardcoded paths:

```python
from comms.constants import DATA_DIR, get_test_data_path

# Get test data file path
test_data_path = get_test_data_path("proxy_set_header.yaml")  # Returns absolute path
```

### Adding New Test Modules

1. Create YAML file in `test_data/{module_name}.yaml`
2. Create test script in `test_script/test_{module_name}.py` (copy from existing test and modify the YAML filename)
3. Import from `comms` package, not individual modules directly

### Nginx Config Injection

The `add_nginx_config()` function in `comms/nginx_operate.py` inserts test configurations before the closing brace of the http block. Configs are marked with comments for easy identification:
```
# ===== 自动化测试临时配置 =====
{config_content}
# ===== 自动化测试临时配置结束 =====
```

### Configuration Requirements

Before running tests, ensure `config/config.ini` has correct paths for your Nginx installation:
- `nginx_path`: Path to nginx.conf
- `nginx_bin_path`: Path to nginx binary
- `backup_path`: Where to store config backups
- `error_log_path`: For troubleshooting failures

If `config/config.ini` is not present or values are missing, the framework will use platform-specific defaults:

| Platform | nginx_path | nginx_bin_path | backup_path |
|----------|------------|----------------|-------------|
| Windows | `D:\Tools\nginx-1.30.0\conf\nginx.conf` | `D:\Tools\nginx-1.30.0\nginx.exe` | `D:\Tools\nginx-1.30.0\backup\` |
| macOS (Homebrew) | `/usr/local/etc/nginx/nginx.conf` | `/usr/local/bin/nginx` | `/usr/local/etc/nginx/backup/` |
| Linux | `/etc/nginx/nginx.conf` | `/usr/sbin/nginx` | `/etc/nginx/backup/` |

### Cross-Platform Compatibility

The framework supports Windows, macOS, and Linux with the following considerations:

1. **Paths**: Automatically adapted to platform-specific formats (backslashes on Windows, forward slashes on Unix)
2. **Permissions**: Linux/macOS may require `sudo` for modifying system Nginx configs
3. **Nginx Commands**: 
   - Windows: Requires setting working directory to Nginx install path
   - Linux/macOS: May need `sudo` for reload/restart operations
4. **Process Management**: Uses `systemctl`/`service` on Linux, direct binary calls on macOS/Windows

To check platform detection:
```python
from comms.platform_utils import get_platform, get_default_nginx_paths, check_nginx_installed

print(get_platform())  # 'windows', 'linux', or 'darwin'
print(get_default_nginx_paths())  # Platform-specific default paths
print(check_nginx_installed())  # Check if nginx is available
```

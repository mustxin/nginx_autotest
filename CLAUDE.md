# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Nginx White-box Testing Automation Framework** (Nginx白盒测试自动化框架) that follows a data-script separation design. Test cases are defined in YAML files while test scripts handle execution logic only. Currently has **29 test cases** across 7 modules.

## Common Commands

### Run Tests

```bash
# Run all tests
pytest test_script/ -v

# Run specific test module
pytest test_script/test_add_header.py -v

# Run specific test case by ID pattern
pytest test_script/test_add_header.py -v -k "add_header_001"

# Run with detailed traceback
pytest test_script/ -v --tb=long

# Generate HTML report
pytest test_script/ -v --html=reports/report.html
```

## Architecture Overview

### Data-Script Separation Design

The framework strictly separates test data from execution logic:

- **Test Data** (`test_data/*.yaml`): Contains test case ID, purpose, pre-conditions, Nginx config content, commands to execute, and expected/unexpected results.
- **Test Scripts** (`test_script/test_*.py`): Only contain execution logic. They read YAML data and use shared utilities.
- **Shared Utilities** (`comms/`): Provide reusable functions for Nginx operations, command execution, data reading, and logging.

### Key Modules

**`comms/` - Common Utilities**
- `nginx_operate.py`: Nginx operations (backup/restore config, check syntax, reload/restart, config injection)
- `cmd_operate.py`: Command execution wrappers (`run_cmd`, `run_cmd_with_code`)
- `data_read.py`: YAML and INI config file parsers
- `constants.py`: Path constants and path helper functions
- `log_utils.py`: Logging singleton — writes to `logs/info.log` and `logs/error.log`, no console output
- `platform_utils.py`: Cross-platform detection and Nginx path defaults
- `grpc_helper.py`: gRPC mock server lifecycle and client call helper for end-to-end gRPC tests

**`grpc_mock/` - gRPC Mock Server**
- `echo.proto`: Proto definition for Echo service
- `server.py`: Mock gRPC server that echoes received metadata
- `echo_pb2.py` / `echo_pb2_grpc.py`: Generated protobuf code

**`test_script/conftest.py`**
- Session-scoped fixture: backs up Nginx config before all tests, restores after completion
- Module-scoped fixture: restores Nginx config between test modules to ensure isolation

**`config/config.ini`**
- Central configuration for Nginx paths, ports, and report settings. Falls back to platform defaults if missing.

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
  unexpected_result:        # optional — negative assertions
    - "should not appear"
  grpc_verify:              # optional — gRPC e2e verification
    target: "localhost:19080"
    message: "test"
    expect_metadata:
      x-custom-header: "value"
```

### Test Execution Flow

1. `conftest.py` session fixture backs up Nginx config
2. `conftest.py` module fixture restores config to clean state
3. Test script reads YAML data via `read_yaml()`
4. `pytest.mark.parametrize` iterates over all cases in YAML
5. For each case:
   - `add_nginx_config()` injects config content into Nginx config
   - `check_nginx_config()` runs `nginx -t`
   - `reload_nginx()` applies changes
   - `run_cmd()` executes test commands (curl, etc.)
   - Assertions verify expected strings in output
   - Optional: verify unexpected strings are NOT in output
   - Optional: gRPC end-to-end verification via `grpc_call()`
6. Module fixture restores config after each module completes
7. Session fixture restores original config after all tests

### Logging

All test logging uses `comms.log_utils.logger` (not `print()`):
- `logs/info.log`: All INFO+ messages with timestamps, filenames, and line numbers
- `logs/error.log`: ERROR+ messages only
- Console: No output (StreamHandler removed)

Log format: `%(asctime)s - [%(filename)s - %(lineno)d] - %(levelname)s:%(message)s`

Import: `from comms.log_utils import logger`

## Important Implementation Details

### Path Management

Use constants from `comms.constants` instead of hardcoded paths:

```python
from comms.constants import DATA_DIR, get_test_data_path

test_data_path = get_test_data_path("proxy_set_header.yaml")  # Returns absolute path
```

### Adding New Test Modules

1. Create YAML file in `test_data/{module_name}.yaml`
2. Create test script in `test_script/test_{module_name}.py` (copy from existing test and modify the YAML filename)
3. Import from `comms` package, not individual modules directly
4. Use `from comms.log_utils import logger` for all logging

### Nginx Config Injection

The `add_nginx_config()` function in `comms/nginx_operate.py` intelligently inserts test configurations:
- **server blocks**: Inserted at the start of the `http` block (for priority matching)
- **location blocks / other directives**: Inserted into the last `server` block

Configs are marked with comments for identification and cleanup:
```
# ===== 自动化测试临时配置 =====
{config_content}
# ===== 自动化测试临时配置结束 =====
```

The `_remove_test_config()` function cleans up previous test configs before injecting new ones.

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

1. **Paths**: Automatically adapted to platform-specific formats
2. **Permissions**: Linux/macOS may require `sudo` for modifying system Nginx configs
3. **Nginx Commands**:
   - Windows: Requires setting working directory to Nginx install path
   - Linux/macOS: May need `sudo` for reload/restart operations
4. **Process Management**: Uses `systemctl`/`service` on Linux, direct binary calls on macOS/Windows
5. **gRPC**: Server binds to `0.0.0.0` (not `[::]`) for Windows IPv4 compatibility
6. **HTTP/2**: Uses `http2 on;` directive (not deprecated `listen ... http2` syntax for Nginx 1.25.1+)

### Known Constraints

- `listen ... http2` is deprecated since Nginx 1.25.1 — use `http2 on;` instead
- Windows may have Nginx reload timing issues — the framework adds `time.sleep(0.5)` after reload
- The `_remove_test_config` regex uses `[^\S\n]*` (not `\s*`) to avoid consuming newlines that break brace matching

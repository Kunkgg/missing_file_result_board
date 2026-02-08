## 缺失文件检查看板

使用 Django 和 DRF 构建的一个简单后端服务，用于展示和管理缺失文件检查结果。

### 功能

- 提供 RESTful API 以获取和管理缺失文件检查结果
- 接口的返回的数据主体部分为一个列表， 每个元素为一个字典， 包含以下字段：
  - `task_id`: 任务 ID
  - `search_version`: 搜索版本
  - `product`: 产品名称
  - `lan`: 语言
  - `source_type`: 源类型
  - `data_type`: 数据类型
  - `group_name`: 组名
  - `lastest_result`: 最新检查结果，包含所有工具最新的检查结果, 为一个字典, key 为工具类型，value 为该工具的检查结果, 例如：
    ```
    {
        "tool_a": {
            "status": "completed",
            "report_url": "http://example.com/report/tool_a",
            "missed": 10,
            "failed": 2,
            "passed": 88,
            "shielded": 5,
            "remapped": 3,
            "create_at": "2024-01-01T12:00:00Z",
            "finish_at": "2024-01-01T12:30:00Z"
        },
        "tool_b": {
            "status": "in_progress",
            ...
        }
    }
    ```
- 支持过滤功能，允许根据任务属性（如 `search_version`, `product`, `lan`, `source_type`, `data_type`, `group_name` ）进行筛选
- 当某个任务没有任何工具的检查结果时，`lastest_result` 字段为一个空字典 `{}`
- 当某个任务的某个工具没有检查结果时，该工具依然出现在 `lastest_result` 字典中
- lastest_result 的工具类型是固定的， 包括 "tool_a", "tool_b", "tool_c", "tool_d", "tool_e", "tool_f"

### 技术栈

- Django
- Django REST Framework
- Django Filters
- SQLite (开发环境)

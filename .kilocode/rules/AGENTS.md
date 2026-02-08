# AGENTS.md

> 这是一个用于快速实现我们工程内部的缺失文件检查结果看板 api 后端的代码库
> Goal: keep the system **simple, maintainable, and pragmatic** — avoid over-engineering.

---

## Dev environment tips

- 使用 `uv add` 添加依赖（不要直接修改 pyproject.toml）
- 使用 `uv run python` 运行 Python 代码
- Django 管理命令统一通过：
  - `uv run python manage.py <command>`
- 使用 `djangorestframework` 构建 API
- 使用 `django-filters` 实现过滤功能
- python 版本: `3.14`


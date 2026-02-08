from collections import defaultdict


class TaskAggregationService:
    """任务聚合服务类

    负责处理任务列表的按实体分组聚合逻辑
    """

    # 固定工具类型列表
    TOOL_TYPES = ["tool_a", "tool_b", "tool_c", "tool_d", "tool_e", "tool_f"]

    def get_aggregated_tasks(self, queryset):
        """
        获取按实体聚合的任务列表

        Args:
            queryset: 已过滤的任务查询集

        Returns:
            list: 聚合后的任务列表
        """
        # 按实体属性分组
        entity_tasks = self._group_tasks_by_entity(queryset)

        # 对每个实体聚合结果
        results = []
        for (
            search_version,
            product,
            lan,
            source_type,
            data_type,
            group_name,
        ), tasks in entity_tasks.items():
            aggregated_task = self._aggregate_entity_results(
                search_version, product, lan, source_type, data_type, group_name, tasks
            )
            results.append(aggregated_task)

        return results

    def _group_tasks_by_entity(self, queryset):
        """
        按实体属性对任务进行分组

        Args:
            queryset: 任务查询集

        Returns:
            dict: 按实体分组的任务字典
        """
        entity_tasks = defaultdict(list)
        for task in queryset:
            key = (
                task.search_version,
                task.product,
                task.lan,
                task.source_type,
                task.data_type,
                task.group_name,
            )
            entity_tasks[key].append(task)

        return entity_tasks

    def _aggregate_entity_results(
        self, search_version, product, lan, source_type, data_type, group_name, tasks
    ):
        """
        聚合单个实体的所有工具结果

        Args:
            search_version: 搜索版本
            product: 产品
            lan: 语言
            source_type: 源类型
            data_type: 数据类型
            group_name: 组名
            tasks: 该实体的任务列表

        Returns:
            dict: 聚合后的任务数据
        """
        # 取第一个任务 ID 作为代表
        first_task = tasks[0]

        # 构建 latest_result 字典
        latest_result = self._build_latest_result_dict(tasks)

        # 构建响应数据
        return {
            "task_id": first_task.id,
            "search_version": search_version,
            "product": product,
            "lan": lan,
            "source_type": source_type,
            "data_type": data_type,
            "group_name": group_name,
            "latest_result": latest_result,
        }

    def _build_latest_result_dict(self, tasks):
        """
        构建包含所有工具最新结果的字典

        Args:
            tasks: 任务列表

        Returns:
            dict: 最新结果字典
        """
        latest_result = {}

        for tool_type in self.TOOL_TYPES:
            tool_result = self._get_latest_tool_result(tasks, tool_type)
            latest_result[tool_type] = tool_result

        return latest_result

    def _get_latest_tool_result(self, tasks, tool_type):
        """
        获取指定工具类型的最新结果

        Args:
            tasks: 任务列表
            tool_type: 工具类型

        Returns:
            dict or None: 工具的最新结果，如果无结果则返回 None
        """
        # 查找对应工具的任务
        tool_task = next((t for t in tasks if t.tool_type == tool_type), None)

        if tool_task:
            # 获取该任务的最新结果
            latest_result_obj = tool_task.results.order_by("-create_at").first()

            if latest_result_obj:
                # 有结果，填充数据
                return {
                    "status": latest_result_obj.status,
                    "report_url": latest_result_obj.report_url,
                    "missed": latest_result_obj.missed,
                    "failed": latest_result_obj.failed,
                    "passed": latest_result_obj.passed,
                    "shielded": latest_result_obj.shielded,
                    "remapped": latest_result_obj.remapped,
                    "create_at": latest_result_obj.create_at.isoformat()
                    if latest_result_obj.create_at
                    else None,
                    "finish_at": latest_result_obj.finish_at.isoformat()
                    if latest_result_obj.finish_at
                    else None,
                }
            else:
                # 任务存在但没有结果
                return None
        else:
            # 该工具没有对应的任务
            return None

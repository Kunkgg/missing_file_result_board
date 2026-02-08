from ..models import MissingFileCheckTask


class TaskDetailService:
    """任务详情服务类

    负责处理单个任务详情获取的逻辑
    """

    def get_task_detail(self, task_id):
        """
        获取单个任务的详细信息

        Args:
            task_id: 任务ID

        Returns:
            dict: 任务详情数据

        Raises:
            MissingFileCheckTask.DoesNotExist: 当任务不存在时
        """
        task = MissingFileCheckTask.objects.prefetch_related("results__details").get(
            id=task_id
        )

        return self._build_task_detail_response(task)

    def _build_task_detail_response(self, task):
        """
        构建任务详情响应数据

        Args:
            task: MissingFileCheckTask实例

        Returns:
            dict: 任务详情响应数据
        """
        # 获取所有结果
        results = task.results.all().order_by("-create_at")

        # 构建响应
        response_data = {
            "task_id": task.id,
            "search_version": task.search_version,
            "product": task.product,
            "lan": task.lan,
            "source_type": task.source_type,
            "data_type": task.data_type,
            "group_name": task.group_name,
            "tool_type": task.tool_type,
            "is_active": task.is_active,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "results": [],
        }

        for result in results:
            result_data = self._format_result_data(result)
            response_data["results"].append(result_data)

        return response_data

    def _format_result_data(self, result):
        """
        格式化单个结果数据

        Args:
            result: MissingFileCheckResult实例

        Returns:
            dict: 格式化的结果数据
        """
        return {
            "id": result.id,
            "status": result.status,
            "report_url": result.report_url,
            "missed": result.missed,
            "failed": result.failed,
            "passed": result.passed,
            "shielded": result.shielded,
            "remapped": result.remapped,
            "create_at": result.create_at.isoformat() if result.create_at else None,
            "finish_at": result.finish_at.isoformat() if result.finish_at else None,
            "details": self._format_result_details(result.details.all()),
        }

    def _format_result_details(self, details):
        """
        格式化结果详情列表

        Args:
            details: 结果详情查询集

        Returns:
            list: 格式化的详情列表
        """
        return [
            {
                "id": detail.id,
                "file_path": detail.file_path,
                "status": detail.status,
                "reason": detail.reason,
                "shielded_by": detail.shielded_by,
                "shielded_remark": detail.shielded_remark,
                "remapped_by": detail.remapped_by,
                "remapped_to": detail.remapped_to,
                "remap_remark": detail.remap_remark,
                "first_detected_at": (
                    detail.first_detected_at.isoformat()
                    if detail.first_detected_at
                    else None
                ),
            }
            for detail in details
        ]

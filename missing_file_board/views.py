from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MissingFileCheckTask
from .serializers import TaskListSerializer
from .services.task_aggregation_service import TaskAggregationService
from .services.task_detail_service import TaskDetailService


class TaskViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    任务视图集
    实现按实体分组聚合多个工具结果的逻辑

    GET /api/tasks/ - 获取任务列表（按实体聚合）
    GET /api/tasks/{id}/ - 获取单个任务详情
    """

    serializer_class = TaskListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "search_version",
        "product",
        "lan",
        "source_type",
        "data_type",
        "group_name",
        "tool_type",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化服务层实例
        self.aggregation_service = TaskAggregationService()
        self.detail_service = TaskDetailService()

    def get_queryset(self):
        """返回基础查询集"""
        return MissingFileCheckTask.objects.all()

    def list(self, request, *args, **kwargs):
        """
        获取任务列表
        按实体 (search_version, product, lan, source_type, data_type,
        group_name) 分组
        聚合每个实体的所有工具结果到 latest_result 字典
        """
        # 1. 获取过滤后的查询集
        queryset = self.filter_queryset(self.get_queryset())

        # 2. 使用服务层处理业务逻辑
        results = self.aggregation_service.get_aggregated_tasks(queryset)

        # 3. 序列化并返回
        serializer = TaskListSerializer(results, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """获取单个任务详情"""
        task_id = kwargs.get("pk")

        try:
            # 使用服务层处理业务逻辑
            task_detail = self.detail_service.get_task_detail(task_id)
            return Response(task_detail)
        except MissingFileCheckTask.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

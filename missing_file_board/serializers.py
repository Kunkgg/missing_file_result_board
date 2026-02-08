from rest_framework import serializers
from .models import MissingFileCheckTask, MissingFileCheckResult, MissingFileDetail


class MissingFileDetailSerializer(serializers.ModelSerializer):
    """缺失文件详情序列化器"""

    class Meta:
        model = MissingFileDetail
        fields = [
            "id",
            "file_path",
            "status",
            "reason",
            "shielded_by",
            "shielded_remark",
            "remapped_by",
            "remapped_to",
            "remap_remark",
            "first_detected_at",
        ]


class MissingFileCheckResultSerializer(serializers.ModelSerializer):
    """检查结果序列化器（嵌套详情）"""

    details = MissingFileDetailSerializer(many=True, read_only=True)

    class Meta:
        model = MissingFileCheckResult
        fields = [
            "id",
            "status",
            "report_url",
            "missed",
            "failed",
            "passed",
            "shielded",
            "remapped",
            "create_at",
            "finish_at",
            "details",
        ]


class TaskLatestResultSerializer(serializers.Serializer):
    """
    单个工具的最新结果序列化器
    用于构造 latest_result 字典
    """

    status = serializers.CharField(allow_null=True)
    report_url = serializers.URLField(allow_null=True)
    missed = serializers.IntegerField(allow_null=True)
    failed = serializers.IntegerField(allow_null=True)
    passed = serializers.IntegerField(allow_null=True)
    shielded = serializers.IntegerField(allow_null=True)
    remapped = serializers.IntegerField(allow_null=True)
    create_at = serializers.DateTimeField(allow_null=True)
    finish_at = serializers.DateTimeField(allow_null=True)


class TaskListSerializer(serializers.Serializer):
    """
    任务列表序列化器
    按实体分组后，每个实体的聚合结果
    """

    task_id = serializers.IntegerField()
    search_version = serializers.CharField()
    product = serializers.CharField()
    lan = serializers.CharField()
    source_type = serializers.CharField()
    data_type = serializers.CharField()
    group_name = serializers.CharField()
    latest_result = serializers.DictField(child=serializers.DictField())


class MissingFileCheckTaskSerializer(serializers.ModelSerializer):
    """任务序列化器（查看单个任务详情时使用）"""

    results = MissingFileCheckResultSerializer(many=True, read_only=True)

    class Meta:
        model = MissingFileCheckTask
        fields = [
            "id",
            "search_version",
            "product",
            "lan",
            "source_type",
            "data_type",
            "group_name",
            "tool_type",
            "is_active",
            "created_at",
            "updated_at",
            "results",
        ]
        read_only_fields = ["created_at", "updated_at"]

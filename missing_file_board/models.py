from django.db import models


class MissingFileCheckTask(models.Model):
    """
    缺失文件检查任务
    每个任务对应一个工具对一个实体的检查配置
    实体由 (search_version, product, lan, source_type, data_type, group_name) 唯一定义
    同一个实体跑多个工具会创建多行任务（每行对应一个 tool_type）
    """

    search_version = models.CharField(max_length=100)
    product = models.CharField(max_length=100)
    lan = models.CharField(max_length=50)
    source_type = models.CharField(max_length=100)
    data_type = models.CharField(max_length=100)
    group_name = models.CharField(max_length=100)
    tool_type = models.CharField(
        max_length=50
    )  # 工具类型：tool_a, tool_b, tool_c, tool_d, tool_e, tool_f
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            "search_version",
            "product",
            "lan",
            "source_type",
            "data_type",
            "group_name",
            "tool_type",
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product}/{self.lan}/{self.source_type}/{self.data_type}/{self.group_name} - {self.tool_type}"


class MissingFileCheckResult(models.Model):
    """
    缺失文件检查结果
    每个任务可能有多次检查结果，记录每次检查的详细结果
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    task = models.ForeignKey(
        MissingFileCheckTask, on_delete=models.CASCADE, related_name="results"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    report_url = models.URLField(blank=True, null=True)
    missed = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    passed = models.IntegerField(default=0)
    shielded = models.IntegerField(default=0)
    remapped = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    finish_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-create_at"]

    def __str__(self):
        return f"{self.task.tool_type} - {self.status} at {self.create_at}"


class MissingFileDetail(models.Model):
    """
    缺失文件详情
    记录每个具体的缺失文件信息
    """

    STATUS_CHOICES = [
        ("missed", "Missed"),
        ("failed", "Failed"),
        ("shielded", "Shielded"),
        ("remapped", "Remapped"),
        ("passed", "Passed"),
    ]

    result = models.ForeignKey(
        MissingFileCheckResult, on_delete=models.CASCADE, related_name="details"
    )
    file_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.TextField(blank=True, null=True)
    shielded_by = models.IntegerField(blank=True, null=True)
    shielded_remark = models.TextField(blank=True, null=True)
    remapped_by = models.IntegerField(blank=True, null=True)
    remapped_to = models.CharField(max_length=500, blank=True, null=True)
    remap_remark = models.TextField(blank=True, null=True)
    first_detected_at = models.DateTimeField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.file_path} - {self.status}"

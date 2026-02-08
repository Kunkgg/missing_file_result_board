from collections import defaultdict
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MissingFileCheckTask, MissingFileCheckResult
from .serializers import TaskListSerializer


class TaskViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    任务视图集
    实现按实体分组聚合多个工具结果的逻辑
    
    GET /api/tasks/ - 获取任务列表（按实体聚合）
    GET /api/tasks/{id}/ - 获取单个任务详情
    """
    serializer_class = TaskListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'search_version', 'product', 'lan',
        'source_type', 'data_type', 'group_name', 'tool_type'
    ]
    
    # 固定工具类型列表
    TOOL_TYPES = ['tool_a', 'tool_b', 'tool_c', 'tool_d', 'tool_e', 'tool_f']
    
    def get_queryset(self):
        """返回基础查询集"""
        return MissingFileCheckTask.objects.all()
    
    def list(self, request, *args, **kwargs):
        """
        获取任务列表
        按实体 (search_version, product, lan, source_type, data_type, group_name) 分组
        聚合每个实体的所有工具结果到 latest_result 字典
        """
        # 1. 获取过滤后的查询集
        queryset = self.filter_queryset(self.get_queryset())
        
        # 2. 按实体属性分组
        entity_tasks = defaultdict(list)
        for task in queryset:
            key = (
                task.search_version,
                task.product,
                task.lan,
                task.source_type,
                task.data_type,
                task.group_name
            )
            entity_tasks[key].append(task)
        
        # 3. 对每个实体聚合结果
        results = []
        for (search_version, product, lan, source_type, data_type, group_name), tasks in entity_tasks.items():
            # 取第一个任务 ID 作为代表
            first_task = tasks[0]
            
            # 构建 latest_result 字典
            latest_result = {}
            for tool_type in self.TOOL_TYPES:
                # 查找对应工具的任务
                tool_task = next((t for t in tasks if t.tool_type == tool_type), None)
                
                if tool_task:
                    # 获取该任务的最新结果
                    latest_result_obj = tool_task.results.order_by('-create_at').first()
                    
                    if latest_result_obj:
                        # 有结果，填充数据
                        latest_result[tool_type] = {
                            'status': latest_result_obj.status,
                            'report_url': latest_result_obj.report_url,
                            'missed': latest_result_obj.missed,
                            'failed': latest_result_obj.failed,
                            'passed': latest_result_obj.passed,
                            'shielded': latest_result_obj.shielded,
                            'remapped': latest_result_obj.remapped,
                            'create_at': latest_result_obj.create_at.isoformat() if latest_result_obj.create_at else None,
                            'finish_at': latest_result_obj.finish_at.isoformat() if latest_result_obj.finish_at else None
                        }
                    else:
                        # 任务存在但没有结果
                        latest_result[tool_type] = None
                else:
                    # 该工具没有对应的任务
                    latest_result[tool_type] = None
            
            # 构建响应数据
            results.append({
                'task_id': first_task.id,
                'search_version': search_version,
                'product': product,
                'lan': lan,
                'source_type': source_type,
                'data_type': data_type,
                'group_name': group_name,
                'latest_result': latest_result
            })
        
        # 4. 序列化并返回
        serializer = TaskListSerializer(results, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个任务详情"""
        task_id = kwargs.get('pk')
        
        try:
            task = MissingFileCheckTask.objects.prefetch_related('results__details').get(id=task_id)
        except MissingFileCheckTask.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)
        
        # 获取所有结果
        results = task.results.all().order_by('-create_at')
        
        # 构建响应
        response_data = {
            'task_id': task.id,
            'search_version': task.search_version,
            'product': task.product,
            'lan': task.lan,
            'source_type': task.source_type,
            'data_type': task.data_type,
            'group_name': task.group_name,
            'tool_type': task.tool_type,
            'is_active': task.is_active,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None,
            'results': []
        }
        
        for result in results:
            response_data['results'].append({
                'id': result.id,
                'status': result.status,
                'report_url': result.report_url,
                'missed': result.missed,
                'failed': result.failed,
                'passed': result.passed,
                'shielded': result.shielded,
                'remapped': result.remapped,
                'create_at': result.create_at.isoformat() if result.create_at else None,
                'finish_at': result.finish_at.isoformat() if result.finish_at else None,
                'details': [
                    {
                        'id': detail.id,
                        'file_path': detail.file_path,
                        'status': detail.status,
                        'reason': detail.reason,
                        'shielded_by': detail.shielded_by,
                        'shielded_remark': detail.shielded_remark,
                        'remapped_by': detail.remapped_by,
                        'remapped_to': detail.remapped_to,
                        'remap_remark': detail.remap_remark,
                        'first_detected_at': detail.first_detected_at.isoformat() if detail.first_detected_at else None
                    }
                    for detail in result.details.all()
                ]
            })
        
        return Response(response_data)

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List
from .ping_monitor import PingMonitor
import uuid

class TaskManager:
    def __init__(self, max_concurrent_tasks=5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.active_tasks: Dict[str, PingMonitor] = {}
        self.completed_tasks: List[dict] = []
        self.task_history: Dict[str, dict] = {}
        self.lock = threading.Lock()
        
    def create_task(self, target_ip: str, duration_hours: int) -> str:
        """创建新的ping任务"""
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            raise Exception("达到最大并发任务数")
            
        # 生成唯一任务ID
        task_id = str(uuid.uuid4())[:8]
        
        # 创建ping监控器
        monitor = PingMonitor(target_ip, duration_hours, task_id)
        
        with self.lock:
            self.active_tasks[task_id] = monitor
            
            # 记录任务信息
            self.task_history[task_id] = {
                'id': task_id,
                'target_ip': target_ip,
                'duration_hours': duration_hours,
                'start_time': datetime.now().isoformat(),
                'status': 'running',
                'progress': 0
            }
        
        # 启动任务
        monitor.start()
        
        # 启动监控线程
        threading.Thread(
            target=self._monitor_task,
            args=(task_id, monitor, duration_hours),
            daemon=True
        ).start()
        
        return task_id
    
    def _monitor_task(self, task_id: str, monitor: PingMonitor, duration_hours: int):
        """监控任务进度"""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        while monitor.is_running:
            current_time = datetime.now()
            
            if current_time >= end_time:
                monitor.stop()
                break
                
            # 计算进度
            elapsed = current_time - start_time
            progress = min(100, (elapsed.total_seconds() / (duration_hours * 3600)) * 100)
            
            with self.lock:
                if task_id in self.task_history:
                    self.task_history[task_id]['progress'] = round(progress, 2)
                    self.task_history[task_id]['elapsed'] = str(elapsed).split('.')[0]
            
            time.sleep(5)  # 每5秒更新一次进度
        
        # 任务完成
        with self.lock:
            if task_id in self.active_tasks:
                monitor = self.active_tasks.pop(task_id)
                
            if task_id in self.task_history:
                self.task_history[task_id]['status'] = 'completed'
                self.task_history[task_id]['end_time'] = datetime.now().isoformat()
                self.task_history[task_id]['progress'] = 100
                
                self.completed_tasks.append(self.task_history[task_id])
    
    def stop_task(self, task_id: str):
        """停止任务"""
        with self.lock:
            if task_id in self.active_tasks:
                monitor = self.active_tasks[task_id]
                monitor.stop()
                
                self.task_history[task_id]['status'] = 'stopped'
                self.task_history[task_id]['end_time'] = datetime.now().isoformat()
                
                self.active_tasks.pop(task_id, None)
                return True
        return False
    
    def get_task_status(self, task_id: str) -> dict:
        """获取任务状态"""
        with self.lock:
            return self.task_history.get(task_id, {})
    
    def get_all_tasks(self) -> List[dict]:
        """获取所有任务"""
        with self.lock:
            all_tasks = []
            
            # 活跃任务
            for task_id, monitor in self.active_tasks.items():
                if task_id in self.task_history:
                    all_tasks.append(self.task_history[task_id])
            
            # 已完成任务
            all_tasks.extend(self.completed_tasks)
            
            return sorted(
                all_tasks, 
                key=lambda x: x.get('start_time', ''), 
                reverse=True
            )
    
    def cleanup_old_tasks(self, days_to_keep=7):
        """清理旧任务记录"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self.lock:
            self.completed_tasks = [
                task for task in self.completed_tasks
                if datetime.fromisoformat(task.get('end_time', task.get('start_time', ''))) > cutoff_date
            ]
            
            # 清理历史记录
            task_ids_to_remove = []
            for task_id, task_info in self.task_history.items():
                if task_info.get('status') == 'completed':
                    task_time = datetime.fromisoformat(task_info.get('end_time', task_info.get('start_time', '')))
                    if task_time < cutoff_date:
                        task_ids_to_remove.append(task_id)
            
            for task_id in task_ids_to_remove:
                self.task_history.pop(task_id, None)
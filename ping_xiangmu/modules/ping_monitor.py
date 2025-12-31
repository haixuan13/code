import time
import threading
import json
from datetime import datetime, timedelta
from ping3 import ping
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

class PingMonitor:
    def __init__(self, target_ip, duration_hours, task_id):
        self.target_ip = target_ip
        self.duration = timedelta(hours=duration_hours)
        self.task_id = task_id
        self.is_running = False
        self.start_time = None
        self.data_file = None
        self.thread = None
        
    def start(self):
        """开始ping监控"""
        self.is_running = True
        self.start_time = datetime.now()
        self.thread = threading.Thread(target=self._ping_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """停止ping监控"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
            
    def _ping_loop(self):
        """执行ping循环"""
        data_points = []
        end_time = self.start_time + self.duration
        
        # 创建数据文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.data_file = Path(f"data/raw/ping_{self.target_ip}_{timestamp}.csv")
        
        while self.is_running and datetime.now() < end_time:
            try:
                # 执行ping
                response_time = ping(self.target_ip, timeout=2, unit='ms')
                
                # 记录数据点
                data_point = {
                    'timestamp': datetime.now().isoformat(),
                    'target': self.target_ip,
                    'response_time': response_time if response_time else None,
                    'status': 'success' if response_time else 'timeout'
                }
                
                data_points.append(data_point)
                
                # 每10个数据点保存一次
                if len(data_points) >= 10:
                    self._save_data(data_points)
                    data_points = []
                    
            except Exception as e:
                error_point = {
                    'timestamp': datetime.now().isoformat(),
                    'target': self.target_ip,
                    'response_time': None,
                    'status': 'error',
                    'error': str(e)
                }
                data_points.append(error_point)
                
            time.sleep(1)  # 每秒ping一次
            
        # 保存剩余数据
        if data_points:
            self._save_data(data_points)
            
        # 生成报告
        self._generate_report()
        
    def _save_data(self, data_points):
        """保存数据到CSV"""
        df = pd.DataFrame(data_points)
        file_exists = self.data_file.exists()
        
        # 追加或新建文件
        df.to_csv(
            self.data_file, 
            mode='a', 
            header=not file_exists, 
            index=False
        )
        
    def _generate_report(self):
        """生成分析报告和图表"""
        if not self.data_file or not self.data_file.exists():
            return
            
        # 读取数据
        df = pd.read_csv(self.data_file)
        
        # 转换为时间格式
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 统计信息
        stats = {
            'total_pings': len(df),
            'successful_pings': len(df[df['status'] == 'success']),
            'timeout_pings': len(df[df['status'] == 'timeout']),
            'error_pings': len(df[df['status'] == 'error']),
            'avg_response_time': df['response_time'].mean(),
            'min_response_time': df['response_time'].min(),
            'max_response_time': df['response_time'].max(),
            'availability': len(df[df['status'] == 'success']) / len(df) * 100
        }
        
        # 生成图表
        self._create_charts(df, stats)
        
        # 保存统计信息
        report_file = Path(f"data/reports/report_{self.task_id}.json")
        with open(report_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
            
    def _create_charts(self, df, stats):
        """创建图表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 响应时间趋势图
        success_df = df[df['status'] == 'success'].copy()
        if not success_df.empty:
            axes[0, 0].plot(success_df['timestamp'], success_df['response_time'])
            axes[0, 0].set_title('Response Time Trend')
            axes[0, 0].set_xlabel('Time')
            axes[0, 0].set_ylabel('Response Time (ms)')
            axes[0, 0].grid(True, alpha=0.3)
            
        # 状态分布饼图
        status_counts = df['status'].value_counts()
        axes[0, 1].pie(
            status_counts.values, 
            labels=status_counts.index,
            autopct='%1.1f%%',
            startangle=90
        )
        axes[0, 1].set_title('Ping Status Distribution')
        
        # 响应时间分布直方图
        if not success_df.empty:
            axes[1, 0].hist(success_df['response_time'].dropna(), bins=50, alpha=0.7)
            axes[1, 0].set_title('Response Time Distribution')
            axes[1, 0].set_xlabel('Response Time (ms)')
            axes[1, 0].set_ylabel('Frequency')
            
        # 可用性趋势图
        df['success'] = df['status'] == 'success'
        df['rolling_availability'] = df['success'].rolling(window=60).mean() * 100
        axes[1, 1].plot(df['timestamp'], df['rolling_availability'])
        axes[1, 1].set_title('Availability Trend (5-min rolling)')
        axes[1, 1].set_xlabel('Time')
        axes[1, 1].set_ylabel('Availability (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        chart_file = Path(f"data/processed/chart_{self.task_id}.png")
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
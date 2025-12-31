import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import shutil
from typing import Dict, List, Optional
import numpy as np

class DataManager:
    def __init__(self, base_path="data"):
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.reports_path = self.base_path / "reports"
        
    def save_ping_data(self, task_id: str, data: dict):
        """保存ping数据"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ping_{task_id}_{timestamp}.json"
        
        filepath = self.raw_path / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        return filepath
    
    def load_task_data(self, task_id: str) -> Optional[pd.DataFrame]:
        """加载任务数据"""
        pattern = f"ping_{task_id}_*.csv"
        files = list(self.raw_path.glob(pattern))
        
        if not files:
            return None
            
        # 合并所有数据文件
        dfs = []
        for file in sorted(files):
            try:
                df = pd.read_csv(file)
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                
        if not dfs:
            return None
            
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    
    def get_task_report(self, task_id: str) -> Optional[dict]:
        """获取任务报告"""
        report_file = self.reports_path / f"report_{task_id}.json"
        
        if not report_file.exists():
            return None
            
        with open(report_file, 'r') as f:
            return json.load(f)
    
    def get_all_tasks(self) -> List[dict]:
        """获取所有任务列表"""
        tasks = []
        
        # 从原始数据文件获取任务信息
        raw_files = list(self.raw_path.glob("ping_*.csv"))
        
        for file in raw_files:
            parts = file.stem.split('_')
            if len(parts) >= 3:
                ip = parts[1]
                task_time = parts[2]
                
                try:
                    task_date = datetime.strptime(task_time[:8], '%Y%m%d')
                    
                    # 读取部分数据获取统计信息
                    df = pd.read_csv(file, nrows=100)
                    
                    task_info = {
                        'ip': ip,
                        'task_time': task_time,
                        'date': task_date.strftime('%Y-%m-%d'),
                        'data_points': len(pd.read_csv(file)) if file.stat().st_size > 0 else 0,
                        'file_size': file.stat().st_size
                    }
                    tasks.append(task_info)
                except:
                    continue
                    
        return sorted(tasks, key=lambda x: x['task_time'], reverse=True)
    
    def clean_old_data(self, days_to_keep: int = 30):
        """清理旧数据"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # 清理原始数据
        for file in self.raw_path.glob("*.csv"):
            if file.stat().st_mtime < cutoff_date.timestamp():
                file.unlink()
                
        # 清理报告
        for file in self.reports_path.glob("*.json"):
            if file.stat().st_mtime < cutoff_date.timestamp():
                file.unlink()
                
        # 清理图表
        for file in self.processed_path.glob("*.png"):
            if file.stat().st_mtime < cutoff_date.timestamp():
                file.unlink()
    
    def export_to_excel(self, task_id: str) -> Path:
        """导出数据到Excel"""
        df = self.load_task_data(task_id)
        if df is None:
            raise ValueError(f"No data found for task {task_id}")
            
        export_path = self.processed_path / f"export_{task_id}.xlsx"
        
        with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
            # 写入原始数据
            df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            # 写入统计信息
            stats_df = pd.DataFrame([{
                'Metric': 'Total Pings',
                'Value': len(df)
            }, {
                'Metric': 'Successful Pings',
                'Value': len(df[df['status'] == 'success'])
            }, {
                'Metric': 'Timeout Pings',
                'Value': len(df[df['status'] == 'timeout'])
            }, {
                'Metric': 'Availability',
                'Value': f"{len(df[df['status'] == 'success']) / len(df) * 100:.2f}%"
            }])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
        return export_path
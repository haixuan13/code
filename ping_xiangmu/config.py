import os
from datetime import timedelta

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 路径配置
PATHS = {
    'data_raw': os.path.join(BASE_DIR, 'data', 'raw'),
    'data_processed': os.path.join(BASE_DIR, 'data', 'processed'),
    'data_reports': os.path.join(BASE_DIR, 'data', 'reports'),
    'logs': os.path.join(BASE_DIR, 'logs'),
    'static': os.path.join(BASE_DIR, 'static'),
    'templates': os.path.join(BASE_DIR, 'templates'),
    'modules': os.path.join(BASE_DIR, 'modules'),
    'utils': os.path.join(BASE_DIR, 'utils')
}

# 应用配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MAX_PING_DURATION = timedelta(hours=24)  # 最长ping时间
    PING_INTERVAL = 1  # ping间隔（秒）
    MAX_CONCURRENT_TASKS = 5  # 最大并发任务数
    
    # 数据保留策略
    DATA_RETENTION_DAYS = 30  # 数据保留天数
    
    # 支持的最大历史数据点
    MAX_DATA_POINTS = 10000

# 创建必要的目录
def create_directories():
    for path in PATHS.values():
        os.makedirs(path, exist_ok=True)

if __name__ == '__main__':
    create_directories()
    print("目录结构创建完成")
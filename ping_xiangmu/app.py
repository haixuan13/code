from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
from modules.task_manager import TaskManager
from modules.data_manager import DataManager
from config import create_directories, Config, PATHS
import os

# 创建必要的目录
create_directories()

app = Flask(__name__)
app.config.from_object(Config)

# 初始化管理器
task_manager = TaskManager(max_concurrent_tasks=5)
data_manager = DataManager()

@app.route('/')
def index():
    """主页 - 显示任务列表和创建新任务表单"""
    tasks = task_manager.get_all_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/start_ping', methods=['POST'])
def start_ping():
    """开始新的ping任务"""
    try:
        target_ip = request.form.get('target_ip', '').strip()
        duration_hours = int(request.form.get('duration_hours', 24))
        
        if not target_ip:
            return jsonify({'error': '请输入目标IP地址'}), 400
            
        if duration_hours > 24:
            return jsonify({'error': '持续时间不能超过24小时'}), 400
            
        # 创建任务
        task_id = task_manager.create_task(target_ip, duration_hours)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': f'Ping任务已启动，将持续{duration_hours}小时'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/task/<task_id>')
def task_details(task_id):
    """任务详情页面"""
    task_info = task_manager.get_task_status(task_id)
    
    if not task_info:
        return "任务不存在", 404
        
    # 尝试加载数据
    data = data_manager.load_task_data(task_id)
    
    # 获取报告
    report = data_manager.get_task_report(task_id)
    
    return render_template(
        'results.html',
        task=task_info,
        data_preview=data.head(100).to_dict('records') if data is not None else [],
        report=report
    )

@app.route('/api/task/<task_id>/status')
def task_status(task_id):
    """获取任务状态API"""
    task_info = task_manager.get_task_status(task_id)
    return jsonify(task_info)

@app.route('/api/task/<task_id>/data')
def task_data(task_id):
    """获取任务数据API"""
    data = data_manager.load_task_data(task_id)
    
    if data is None:
        return jsonify({'error': '数据不存在'}), 404
        
    # 只返回最近的数据点（限制数量）
    limit = min(1000, len(data))
    recent_data = data.tail(limit)
    
    return jsonify({
        'timestamps': recent_data['timestamp'].tolist(),
        'response_times': recent_data['response_time'].tolist(),
        'statuses': recent_data['status'].tolist()
    })

@app.route('/stop_task/<task_id>', methods=['POST'])
def stop_task(task_id):
    """停止任务"""
    if task_manager.stop_task(task_id):
        return jsonify({'success': True, 'message': '任务已停止'})
    else:
        return jsonify({'error': '任务不存在或已经停止'}), 404

@app.route('/export/<task_id>')
def export_data(task_id):
    """导出数据为Excel"""
    try:
        export_path = data_manager.export_to_excel(task_id)
        return send_file(
            export_path,
            as_attachment=True,
            download_name=f"ping_data_{task_id}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return str(e), 404

@app.route('/chart/<task_id>')
def get_chart(task_id):
    """获取图表"""
    chart_path = Path(f"data/processed/chart_{task_id}.png")
    
    if chart_path.exists():
        return send_file(chart_path, mimetype='image/png')
    else:
        return "图表不存在", 404

@app.route('/tasks')
def list_tasks():
    """获取所有任务列表"""
    tasks = task_manager.get_all_tasks()
    return jsonify(tasks)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """清理旧数据"""
    try:
        data_manager.clean_old_data(days_to_keep=7)
        return jsonify({'success': True, 'message': '数据清理完成'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'active_tasks': len(task_manager.active_tasks),
        'timestamp': datetime.now().isoformat()
    })

# 启动时清理旧数据
@app.before_first_request
def startup_tasks():
    """应用启动时的初始化任务"""
    data_manager.clean_old_data(days_to_keep=30)
    
    # 启动定期清理任务
    def periodic_cleanup():
        while True:
            time.sleep(3600)  # 每小时检查一次
            data_manager.clean_old_data(days_to_keep=30)
    
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
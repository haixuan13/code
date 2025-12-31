#!/usr/bin/env python3
"""
Ping监控系统启动脚本 - 修复版本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header():
    """打印标题"""
    print("=" * 60)
    print("           Ping网络监控系统")
    print("=" * 60)
    print()

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    if sys.version_info < (3, 7):
        print(f"✗ Python版本过低: {sys.version_info.major}.{sys.version_info.minor}")
        print("  需要Python 3.7或更高版本")
        return False
    print(f"✓ Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖包...")
    
    required_packages = [
        'flask',
        'pandas',
        'matplotlib',
        'ping3',
        'python-dotenv',
        'APScheduler'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少 {len(missing_packages)} 个依赖包:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        return False
    
    print("✓ 所有依赖已安装")
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n正在安装依赖包...")
    
    try:
        # 使用清华镜像源加速安装
        requirements_file = Path(__file__).parent / "requirements.txt"
        
        if not requirements_file.exists():
            print("✗ 未找到 requirements.txt 文件")
            return False
        
        # 安装依赖
        print("正在安装，这可能需要几分钟...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("✓ 依赖安装成功")
            return True
        else:
            print("✗ 依赖安装失败:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ 安装超时，请检查网络连接")
        return False
    except Exception as e:
        print(f"✗ 安装过程中出现错误: {e}")
        return False

def setup_directories():
    """设置目录结构"""
    print("\n创建目录结构...")
    
    directories = [
        'data/raw',
        'data/processed',
        'data/reports',
        'logs',
        'static/css',
        'static/js',
        'templates',
        'modules',
        'utils'
    ]
    
    base_dir = Path(__file__).parent
    created_count = 0
    
    for dir_path in directories:
        full_path = base_dir / dir_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            if not (full_path / '.gitkeep').exists():
                (full_path / '.gitkeep').touch()
            created_count += 1
            print(f"  ✓ 创建目录: {dir_path}")
        except Exception as e:
            print(f"  ✗ 创建目录失败 {dir_path}: {e}")
    
    print(f"✓ 创建了 {created_count} 个目录")
    return True

def create_config_files():
    """创建必要的配置文件"""
    print("\n检查配置文件...")
    
    base_dir = Path(__file__).parent
    
    # 检查配置文件是否存在
    config_files = {
        'config.py': False,
        'requirements.txt': False
    }
    
    for filename in config_files.keys():
        file_path = base_dir / filename
        if file_path.exists():
            print(f"  ✓ {filename}")
            config_files[filename] = True
        else:
            print(f"  ✗ 未找到 {filename}")
    
    return all(config_files.values())

def create_env_file():
    """创建环境变量文件"""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# Ping监控系统环境变量\n")
            f.write("# 注意：在生产环境中修改SECRET_KEY\n")
            f.write("SECRET_KEY=your-secret-key-change-in-production\n")
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_DEBUG=True\n")
        
        print("  ✓ 创建了 .env 文件")
    else:
        print("  ✓ .env 文件已存在")
    
    return True

def create_requirements_file():
    """创建requirements.txt文件"""
    req_file = Path(__file__).parent / "requirements.txt"
    
    if not req_file.exists():
        requirements = """Flask==3.0.0
Flask-CORS==4.0.0
pandas==2.1.3
matplotlib==3.8.2
ping3==4.0.4
python-dotenv==1.0.0
APScheduler==3.10.4
Werkzeug==3.0.1"""
        
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        print("  ✓ 创建了 requirements.txt 文件")
    
    return True

def start_application():
    """启动应用"""
    print("\n" + "=" * 60)
    print("正在启动Ping监控系统...")
    print("=" * 60)
    
    try:
        # 导入并启动应用
        print("导入应用模块...")
        from app import app
        
        print("\n应用信息:")
        print(f"  名称: {app.name}")
        print(f"  调试模式: {app.debug}")
        print(f"  密钥设置: {'是' if app.config.get('SECRET_KEY') else '否'}")
        
        print("\n" + "-" * 60)
        print("应用启动成功!")
        print("-" * 60)
        print("请访问以下地址:")
        print("  http://localhost:5000")
        print("  http://127.0.0.1:5000")
        print("\n按 Ctrl+C 停止应用")
        print("-" * 60)
        
        # 启动Flask应用
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
        
    except ImportError as e:
        print(f"✗ 导入应用失败: {e}")
        print("请确保所有文件都存在且正确")
        return False
    except Exception as e:
        print(f"✗ 启动应用时出现错误: {e}")
        return False
    
    return True

def run_system_check():
    """运行系统检查"""
    print_header()
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 检查依赖
    if not check_dependencies():
        print("\n是否要自动安装依赖包? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 'y':
            if not install_dependencies():
                print("\n请手动安装依赖:")
                print("  pip install -r requirements.txt")
                return False
        else:
            print("\n请手动安装依赖:")
            print("  pip install -r requirements.txt")
            return False
    
    # 设置目录结构
    if not setup_directories():
        print("警告: 部分目录创建失败，继续启动...")
    
    # 创建配置文件
    create_config_files()
    create_env_file()
    create_requirements_file()
    
    return True

def main():
    """主函数"""
    try:
        # 运行系统检查
        if not run_system_check():
            print("\n系统检查失败，请解决上述问题后重试")
            print("\n按回车键退出...")
            input()
            return
        
        # 启动应用
        print("\n正在准备启动应用...")
        time.sleep(1)
        
        if not start_application():
            print("\n应用启动失败")
            print("\n按回车键退出...")
            input()
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nPing监控系统已停止")

if __name__ == "__main__":
    main()
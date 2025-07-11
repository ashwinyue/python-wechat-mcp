#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器进程管理器
用于启动、停止和管理所有MCP服务器进程
"""

import os
import sys
import time
import signal
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.logs_dir = self.project_root / "logs"
        self.venv_python = self.project_root / "venv" / "bin" / "python"
        self.servers_config = self.project_root / "servers_config.json"
        
        # 创建日志目录
        self.logs_dir.mkdir(exist_ok=True)
        
        # 服务器配置
        self.servers = {
            "weixin": {
                "script": "weixin_server.py",
                "description": "微信公众号爬取服务器",
                "env_required": False
            },
            "weather": {
                "script": "weather_server.py", 
                "description": "天气查询服务器",
                "env_required": True
            },
            "math": {
                "script": "math_server.py",
                "description": "数学计算服务器",
                "env_required": False
            },
            "write": {
                "script": "write_server.py",
                "description": "文件写入服务器",
                "env_required": False
            },
            "greeter": {
                "script": "greeter_server.py",
                "description": "问候服务器",
                "env_required": False
            }
        }
        
        # 加载环境变量
        self.env = self._load_env()
        
    def _load_env(self) -> Dict[str, str]:
        """加载环境变量"""
        env = os.environ.copy()
        env_file = self.project_root / ".env"
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env[key] = value
        
        return env
    
    def _get_pid_file(self, server_name: str) -> Path:
        """获取PID文件路径"""
        return self.logs_dir / f"{server_name}.pid"
    
    def _get_log_file(self, server_name: str) -> Path:
        """获取日志文件路径"""
        return self.logs_dir / f"{server_name}.log"
    
    def _is_process_running(self, pid: int) -> bool:
        """检查进程是否在运行"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def _get_running_servers(self) -> Dict[str, int]:
        """获取正在运行的服务器"""
        running = {}
        
        for server_name in self.servers:
            pid_file = self._get_pid_file(server_name)
            if pid_file.exists():
                try:
                    with open(pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    if self._is_process_running(pid):
                        running[server_name] = pid
                    else:
                        # 进程不存在，删除PID文件
                        pid_file.unlink()
                except (ValueError, IOError):
                    # PID文件损坏，删除
                    pid_file.unlink()
        
        return running
    
    def start_server(self, server_name: str) -> bool:
        """启动单个服务器"""
        if server_name not in self.servers:
            logger.error(f"未知服务器: {server_name}")
            return False
        
        # 检查是否已经在运行
        running_servers = self._get_running_servers()
        if server_name in running_servers:
            logger.info(f"服务器 {server_name} 已在运行 (PID: {running_servers[server_name]})")
            return True
        
        server_config = self.servers[server_name]
        script_path = self.project_root / server_config["script"]
        
        if not script_path.exists():
            logger.error(f"服务器脚本不存在: {script_path}")
            return False
        
        # 准备环境变量
        env = self.env.copy() if server_config["env_required"] else os.environ.copy()
        
        # 启动进程
        log_file = self._get_log_file(server_name)
        pid_file = self._get_pid_file(server_name)
        
        try:
            logger.info(f"启动 {server_config['description']}...")
            
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    [str(self.venv_python), str(script_path)],
                    stdin=subprocess.PIPE,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    env=env,
                    cwd=str(self.project_root)
                )
            
            # 保存PID
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # 等待一下确保进程启动
            time.sleep(1)
            
            if self._is_process_running(process.pid):
                logger.info(f"✓ {server_config['description']} 启动成功 (PID: {process.pid})")
                return True
            else:
                logger.error(f"✗ {server_config['description']} 启动失败")
                return False
                
        except Exception as e:
            logger.error(f"启动 {server_name} 时出错: {e}")
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """停止单个服务器"""
        if server_name not in self.servers:
            logger.error(f"未知服务器: {server_name}")
            return False
        
        pid_file = self._get_pid_file(server_name)
        
        if not pid_file.exists():
            logger.info(f"服务器 {server_name} 未在运行")
            return True
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if self._is_process_running(pid):
                logger.info(f"停止 {self.servers[server_name]['description']} (PID: {pid})...")
                os.kill(pid, signal.SIGTERM)
                
                # 等待进程结束
                for _ in range(10):  # 最多等待10秒
                    if not self._is_process_running(pid):
                        break
                    time.sleep(1)
                
                # 如果进程仍在运行，强制杀死
                if self._is_process_running(pid):
                    logger.warning(f"强制杀死进程 {pid}")
                    os.kill(pid, signal.SIGKILL)
                
                logger.info(f"✓ {self.servers[server_name]['description']} 已停止")
            
            # 删除PID文件
            pid_file.unlink()
            return True
            
        except (ValueError, IOError, OSError) as e:
            logger.error(f"停止 {server_name} 时出错: {e}")
            # 删除损坏的PID文件
            if pid_file.exists():
                pid_file.unlink()
            return False
    
    def start_all(self) -> bool:
        """启动所有服务器"""
        logger.info("启动所有MCP服务器...")
        
        success_count = 0
        for server_name in self.servers:
            if self.start_server(server_name):
                success_count += 1
                time.sleep(1)  # 给服务器一些启动时间
        
        total_servers = len(self.servers)
        logger.info(f"启动完成: {success_count}/{total_servers} 个服务器成功启动")
        
        return success_count == total_servers
    
    def stop_all(self) -> bool:
        """停止所有服务器"""
        logger.info("停止所有MCP服务器...")
        
        running_servers = self._get_running_servers()
        if not running_servers:
            logger.info("没有运行的服务器")
            return True
        
        success_count = 0
        for server_name in running_servers:
            if self.stop_server(server_name):
                success_count += 1
        
        total_servers = len(running_servers)
        logger.info(f"停止完成: {success_count}/{total_servers} 个服务器成功停止")
        
        return success_count == total_servers
    
    def status(self) -> Dict[str, Optional[int]]:
        """获取所有服务器状态"""
        running_servers = self._get_running_servers()
        status = {}
        
        for server_name in self.servers:
            status[server_name] = running_servers.get(server_name)
        
        return status
    
    def print_status(self):
        """打印服务器状态"""
        print("MCP服务器状态:")
        print("=" * 50)
        
        status = self.status()
        
        for server_name, pid in status.items():
            server_config = self.servers[server_name]
            if pid:
                print(f"  ✓ {server_config['description']} (PID: {pid})")
            else:
                print(f"  ✗ {server_config['description']} (未运行)")
        
        running_count = sum(1 for pid in status.values() if pid)
        total_count = len(status)
        print(f"\n运行状态: {running_count}/{total_count} 个服务器在运行")
    
    def print_logs(self):
        """打印日志文件信息"""
        print("服务器日志文件:")
        print("=" * 50)
        
        if not self.logs_dir.exists():
            print("没有日志目录")
            return
        
        log_files = list(self.logs_dir.glob("*.log"))
        if not log_files:
            print("没有日志文件")
            return
        
        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            print(f"  {log_file.name} ({size} bytes)")
        
        print("\n使用以下命令查看日志:")
        for server_name in self.servers:
            log_file = self._get_log_file(server_name)
            if log_file.exists():
                print(f"  tail -f {log_file}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python process_manager.py <command>")
        print("命令:")
        print("  start <server_name>  - 启动指定服务器")
        print("  stop <server_name>   - 停止指定服务器")
        print("  start-all           - 启动所有服务器")
        print("  stop-all            - 停止所有服务器")
        print("  status              - 查看服务器状态")
        print("  logs                - 查看日志文件信息")
        print("  restart-all         - 重启所有服务器")
        sys.exit(1)
    
    manager = ProcessManager()
    command = sys.argv[1]
    
    if command == "start" and len(sys.argv) > 2:
        server_name = sys.argv[2]
        success = manager.start_server(server_name)
        sys.exit(0 if success else 1)
    
    elif command == "stop" and len(sys.argv) > 2:
        server_name = sys.argv[2]
        success = manager.stop_server(server_name)
        sys.exit(0 if success else 1)
    
    elif command == "start-all":
        success = manager.start_all()
        sys.exit(0 if success else 1)
    
    elif command == "stop-all":
        success = manager.stop_all()
        sys.exit(0 if success else 1)
    
    elif command == "status":
        manager.print_status()
        sys.exit(0)
    
    elif command == "logs":
        manager.print_logs()
        sys.exit(0)
    
    elif command == "restart-all":
        print("重启所有服务器...")
        manager.stop_all()
        time.sleep(2)
        success = manager.start_all()
        sys.exit(0 if success else 1)
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
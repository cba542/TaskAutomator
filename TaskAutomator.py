import os
import time
import json
from datetime import datetime, timezone, timedelta
import logging
import pytz

class TaskMonitor:
    def __init__(self, tasks_config_path="tasks_config.json"):
        # 設置日誌
        logging.basicConfig(
            filename='task_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8'  # 明確指定日誌文件的編碼
        )
        
        self.tasks_config_path = tasks_config_path
        self.tz = pytz.timezone('Asia/Taipei')  # UTC+8 時區
        self.load_or_create_config()

    def load_or_create_config(self):
        """載入或創建任務配置文件"""
        if os.path.exists(self.tasks_config_path):
            with open(self.tasks_config_path, 'r', encoding='utf-8') as f:
                self.tasks = json.load(f)
        else:
            self.tasks = {}
            self.save_config()

    def save_config(self):
        """保存任務配置"""
        with open(self.tasks_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=4, ensure_ascii=False)

    def add_task(self, task_name, script_path):
        """添加新任務"""
        self.tasks[task_name] = {
            'script_path': script_path,
            'last_run': None
        }
        self.save_config()
        logging.info(f'添加新任務: {task_name}')

    def get_last_run_date(self, task_name):
        """從日誌文件中獲取最後執行日期"""
        if not os.path.exists('task_monitor.log'):
            return None
        
        last_run_date = None
        current_date = datetime.now(self.tz).date()
        
        # 嘗試不同的編碼方式讀取文件
        encodings = ['utf-8', 'cp950', 'big5', 'gbk']
        
        for encoding in encodings:
            try:
                with open('task_monitor.log', 'r', encoding=encoding) as f:
                    lines = list(f)
                    for line in reversed(lines):
                        if f'成功執行任務: {task_name}' in line:
                            try:
                                timestamp = line.split(' - ')[0].strip()
                                log_datetime = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                                log_datetime = self.tz.localize(log_datetime)
                                last_run_date = log_datetime.date()
                                return last_run_date
                            except Exception as e:
                                logging.error(f'解析日期時出錯: {str(e)}')
                                continue
                # 如果成功讀取文件，跳出編碼嘗試循環
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logging.error(f'讀取日誌文件時出錯 ({encoding}): {str(e)}')
                continue
        
        return last_run_date

    def should_run_task(self, task_name):
        """檢查任務是否需要在今天執行"""
        last_run_date = self.get_last_run_date(task_name)
        current_date = datetime.now(self.tz).date()
        
        # 如果從未執行過或最後執行日期不是今天，則需要執行
        return last_run_date is None or last_run_date < current_date

    def run_task(self, task_name):
        """執行任務，並在執行前切換到對應的工作目錄"""
        task = self.tasks.get(task_name)
        if not task:
            logging.error(f'任務不存在: {task_name}')
            return False

        try:
            # 保存當前工作目錄
            original_dir = os.getcwd()
            
            # 獲取腳本所在的目錄
            script_dir = os.path.dirname(task["script_path"])
            script_name = os.path.basename(task["script_path"])
            
            try:
                # 切換到腳本所在目錄
                if script_dir:
                    os.chdir(script_dir)
                    logging.info(f'切換到工作目錄: {script_dir}')
                
                # 執行腳本
                os.system(f'python "{script_name}"')
                
                # 記錄執行時間
                current_time = datetime.now(self.tz)
                self.tasks[task_name]['last_run'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
                self.save_config()
                logging.info(f'成功執行任務: {task_name}')
                return True
                
            finally:
                # 無論執行是否成功，都要切換回原始目錄
                os.chdir(original_dir)
                logging.info(f'切換回原始目錄: {original_dir}')
                
        except Exception as e:
            logging.error(f'執行任務失敗 {task_name}: {str(e)}')
            return False

    def check_and_run_all(self):
        """檢查並執行所有需要運行的任務"""
        current_time = datetime.now(self.tz)
        for task_name in self.tasks:
            if self.should_run_task(task_name):
                print(f'[{current_time.strftime("%Y-%m-%d %H:%M:%S")}] 執行任務: {task_name}')
                self.run_task(task_name)
            else:
                print(f'[{current_time.strftime("%Y-%m-%d %H:%M:%S")}] 任務 {task_name} 今天已執行過')

def main():
    monitor = TaskMonitor()
    
    try:
        # 優先使用本地配置
        from config_local import tasks
    except ImportError:
        # 如果本地配置不存在，使用默認配置
        from config import tasks
    
    # 示例：添加任務
    for taskName, taskPath in tasks.items():
        monitor.add_task(taskName, taskPath)

    while True:
        monitor.check_and_run_all()
        time.sleep(1800)  # 每30分鐘檢查一次

if __name__ == "__main__":
    main()
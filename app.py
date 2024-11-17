import pystray
from PIL import Image
import webbrowser
from flask import Flask, render_template
import mistune
import threading
import os
import yaml
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import hashlib
from datetime import datetime
import uuid

app = Flask(__name__)

# 存储链接和内容的字典
markdown_files = {}
file_id_mapping = {}  # 新增：存储文件ID和文件名的映射

class MarkdownFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            update_markdown_file(event.src_path)

def generate_file_id(filepath):
    """生成唯一的文件ID"""
    return hashlib.md5(filepath.encode()).hexdigest()[:8]

def parse_path_and_alias(path_config):
    # 如果是字典形式的配置
    if isinstance(path_config, dict):
        path = list(path_config.keys())[0]
        alias = list(path_config.values())[0]
        return path, alias
    # 如果是字符串形式（无别名）
    return path_config, None

def load_markdown_files():
    markdown_files.clear()
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    for folder_name, paths in config['folders'].items():
        for path_config in paths:
            # 获取路径和别名
            if isinstance(path_config, dict):
                path = path_config['path']
                alias = path_config.get('alias')  # 使用get方法，如果没有alias则返回None
            else:
                path = path_config
                alias = None
            
            # 移除可能的引号
            path = path.strip('"\'')
            
            if '*' in path:
                # 处理通配符情况
                dir_path = os.path.dirname(path)
                pattern = os.path.basename(path)
                for file in glob.glob(os.path.join(dir_path, pattern)):
                    update_markdown_file(file, folder_name)
            else:
                # 处理单个文件情况
                update_markdown_file(path, folder_name, alias)

def update_markdown_file(filepath, folder_name, alias=None):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_id = str(uuid.uuid4())
        filename = os.path.basename(filepath)
        file_stats = os.stat(filepath)
        
        markdown_files[file_id] = {
            'content': mistune.html(content),
            'path': filepath,
            'folder': folder_name,
            'filename': filename,
            'alias': alias,  # 添加别名字段
            'size': file_stats.st_size,
            'created_time': file_stats.st_ctime,
            'modified_time': file_stats.st_mtime
        }
    except Exception as e:
        print(f"Error processing file {filepath}: {str(e)}")

def read_markdown_files():
    markdown_files.clear()
    file_id_mapping.clear()

    """从配置文件读取并监控Markdown文件"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # observer = Observer()
    
    for folder_name, patterns in config['folders'].items():
        for pattern in patterns:
            # 获取路径和别名
            if isinstance(pattern, dict):
                path = pattern['path']
                alias = pattern.get('alias')
            else:
                path = pattern
                alias = None
                
            # 读取现有的markdown文件
            try:
                if '*' in path:
                    # 处理通配符情况
                    dir_path = os.path.dirname(path)
                    file_pattern = os.path.basename(path)
                    for filepath in glob.glob(os.path.join(dir_path, file_pattern)):
                        update_markdown_file(filepath, folder_name)
                else:
                    # 处理单个文件
                    update_markdown_file(path, folder_name, alias)
                print(f"已加载文件: {path}")
            except Exception as e:
                print(f"处理pattern {pattern}时出错: {str(e)}")
    
    # observer.start()

@app.route('/')
def index():
    # 刷新配置
    read_markdown_files()
    """显示目录页面"""
    grouped_files = {}
    for file_id, info in markdown_files.items():
        folder = info['folder']
        if folder not in grouped_files:
            grouped_files[folder] = []
        grouped_files[folder].append({
            'id': file_id,
            'filename': info['filename'],
            'alias': info['alias'],
            'folder': info['folder']
        })
    
    return render_template('index.html', grouped_files=grouped_files)

@app.route('/view/<file_id>')
def view_markdown(file_id):
    """显示Markdown渲染页面"""
    if file_id in markdown_files:
        file_info = markdown_files[file_id]
        size_kb = file_info['size'] / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{(size_kb/1024):.1f} MB"
        
        return render_template('view.html', 
                             filename=file_info['filename'],
                             folder_name=file_info['folder'],
                             content=file_info['content'],
                             file_info={
                                 'path': file_info['path'],
                                 'size': size_str,
                                 'created_time': datetime.fromtimestamp(file_info['created_time']).strftime('%Y-%m-%d %H:%M:%S'),
                                 'modified_time': datetime.fromtimestamp(file_info['modified_time']).strftime('%Y-%m-%d %H:%M:%S')
                             })
    return "文件不存在"

def create_tray_icon():
    """创建系统托盘图标"""
    # 使用更好看的图标（这里使用一个简单的示例，你可以替换为自己的图标文件）
    icon_path = "icon.png"  # 确保这个文件存在
    if os.path.exists(icon_path):
        image = Image.open(icon_path)
    else:
        # 创建一个渐变色图标作为后备方案
        image = Image.new('RGB', (32, 32))
        pixels = image.load()
        for i in range(image.size[0]):
            for j in range(image.size[1]):
                pixels[i, j] = (
                    int(255 * (i / 31)),
                    int(128 * (j / 31)),
                    255
                )
    
    def on_clicked(icon, item):
        webbrowser.open('http://localhost:5000')

    icon = pystray.Icon("markdown_reader", image, "Markdown阅读器", menu=pystray.Menu(
        pystray.MenuItem("打开", on_clicked),
        pystray.MenuItem("退出", lambda: icon.stop())
    ))
    return icon

def main():
    # 读取链接文件
    read_markdown_files()
    
    # 在新线程中启动Flask服务器
    threading.Thread(target=app.run, daemon=True).start()
    
    # 创建和运行系统托盘图标
    icon = create_tray_icon()
    icon.run()

if __name__ == '__main__':
    main() 
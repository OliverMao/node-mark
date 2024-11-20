import pystray
from PIL import Image
import webbrowser
from flask import Flask, render_template, request, send_file
import mistune
import threading
import os
import yaml
import glob
import hashlib
from datetime import datetime
import uuid

# 从.env文件中读取HOST
HOST = os.getenv('HOST', 'http://localhost:5000')
app = Flask(__name__)
# 存储链接和内容的字典
markdown_files = {}
file_id_mapping = {}  # 新增：存储文件ID和文件名的映射


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
    """从配置文件读取Markdown文件"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config_content = f.read().replace('\\', '/')
        config = yaml.safe_load(config_content)  
    
    for folder_name, patterns in config['folders'].items():
        for pattern in patterns:
            # 获取路径和别名
            if isinstance(pattern, dict):
                path = pattern['path']
                alias = pattern.get('alias')
            else:
                path = pattern
                alias = None
            # 将路径中的反斜杠替换为正斜杠
            path = path.replace('\\', '/')
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

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    """显示和保存配置页面"""
    if request.method == 'POST':
        try:
            # 获取提交的配置内容
            new_config = request.form.get('config')
            # 将路径中的反斜杠替换为正斜杠
            new_config = new_config.replace('\\', '/')
            # 验证YAML格式是否正确
            yaml.safe_load(new_config)
            
            # 写入配置文件
            with open('config.yaml', 'w', encoding='utf-8') as f:
                f.write(new_config)
            
            # 重新读取markdown文件
            read_markdown_files()
            
            return '配置已保存', 200
        except yaml.YAMLError as e:
            return f'YAML格式错误: {str(e)}', 400
        except Exception as e:
            return f'保存配置失败: {str(e)}', 500
    
    # GET请求处理
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = f.read()
        # 去除所有空白行
        config = '\n'.join([line for line in config.split('\n') if line.strip()])
    return render_template('config.html', config=config)

def create_tray_icon():
    """创建系统托盘图标"""
    # 使用更好看的图标（这里使用一个简单的示例，你可以替换为自己的图标文件）
    icon_path = "logo_100.png"  # 确保这个文件存在
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
    
    def on_clicked(path):
        def _handler():  # 创建一个内部处理函数
            if path:
                webbrowser.open(HOST + '/' + path)
            else:
                webbrowser.open(HOST)
        return _handler  # 返回处理函数而不是直接执行

    icon = pystray.Icon("markdown_reader", image, "Markdown阅读器", menu=pystray.Menu(
        pystray.MenuItem("打开", on_clicked('')),
        pystray.MenuItem("编辑", on_clicked('config')),
        pystray.MenuItem("退出", lambda: icon.stop())
    ))

    # 立即打开
    on_clicked('')()

    return icon

def main():
    # 读取链接文件
    read_markdown_files()
    
    # 生产模式
    # 在新线程中启动Flask服务器
    threading.Thread(target=app.run, daemon=True).start()
    
    # 创建和运行系统托盘图标
    icon = create_tray_icon()
    icon.run()

    # DEBUG模式
    # # 创建和运行系统托盘图标（在新线程中运行）
    # icon = create_tray_icon()
    # threading.Thread(target=icon.run, daemon=True).start()
    
    # # 在主线程中运行Flask应用
    # app.run(debug=True) 

    

def replace_image_paths(content, file_path):
    if not file_path:
        return content
        
    # 获取当前文件所在目录的路径
    current_file_dir = os.path.dirname(file_path)
    print('current_file_dir', current_file_dir)
    # 替换图片标签中的src属性
    def replace_path(match):
        img_path = match.group(1)
        print('img_path', img_path)
        if img_path.startswith('./'):
            img_path = img_path[2:]
            now_img_path = os.path.join(current_file_dir, img_path)
            # 创建用于访问图片的URL
            url = f'/api/image?path={now_img_path}'
            return f'<img src="{url}"'
        return f'<img src="{img_path}"'
    
    # 使用正则表达式替换图片路径
    import re
    pattern = r'<img src="([^"]+)"'
    result =  re.sub(pattern, replace_path, content)
    print('result', result)
    return result

# 注册自定义过滤器
app.jinja_env.filters['replace_image_paths'] = replace_image_paths

# 添加图片访问的路由
@app.route('/api/image')
def get_image():
    image_path = request.args.get('path')
    if os.path.exists(image_path):
        return send_file(image_path)
    return '图片不存在', 404

if __name__ == '__main__':
    main() 
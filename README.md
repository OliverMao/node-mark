

<div align="center"><a href="https://github.com/OliverMao/node-mark" ><img width="300" src="./logo.png" alt="logo.png" border="0" /></a>
<h1> 📦 node-mark - 散点Markdown文档阅读器</h1><div><a href="https://github.com/OliverMao/node-mark" ><img  src="https://img.shields.io/badge/license-MIT-License-blue.svg" alt="license" border="0" /></a>
  <img  src="https://img.shields.io/github/stars/OliverMao/node-mark.svg" alt="stars" border="0" />
  <img  src="https://img.shields.io/github/forks/OliverMao/node-mark.svg" alt="forks" border="0" />
  <img  src="https://img.shields.io/badge/version-0.1.6-686480r.svg" alt="forks" border="0" />
</div></div>



# Node Mark - 散点Markdown文档阅读器

Node Mark是一个轻量级的本地Markdown文档阅读器,支持分组管理和实时预览功能。

## 主要特性

- 🗂️ 文件夹分组管理
- 🔍 文件搜索功能
- 🌓 明暗主题切换
- 📱 响应式设计
- 🖼️ 图片预览支持
- 💻 系统托盘运行
- 🔄 实时刷新

## 安装

1. 确保已安装Python 3.8+
2. 克隆项目并安装依赖:

```bash
git clone https://github.com/yourusername/node-mark.git
cd node-mark
pip install -r requirements.txt
```

## 配置

在`config.yaml`中配置你的Markdown文件路径:

```yaml
folders:
  工作文档:
    - path: "D:/documents/work/*.md"
  个人笔记:
    - path: "D:/notes/*.md"
    - path: "D:/blog/posts/*.md"
      alias: "博客文章"
```

配置说明:
- 支持文件夹分组
- 支持通配符`*.md`
- 可以为文件设置别名

## 运行

### 方式一: 直接运行

```bash
python app.py
```

### 方式二: 后台运行(Windows)

双击`启动笔记.vbs`即可在后台运行。

## 使用说明

1. 启动后会在系统托盘显示图标
2. 点击托盘图标可以打开主界面
3. 在主界面可以:
   - 查看所有分组的Markdown文件
   - 搜索文件
   - 切换主题
   - 查看文件详细信息

## 技术栈

- 后端: Flask
- 前端: 原生HTML/CSS/JS
- UI: Remix Icon
- Markdown渲染: mistune
- 系统托盘: pystray

## 许可证

MIT License

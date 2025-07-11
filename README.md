# 微信公众号文章爬取 MCP 项目

这个项目展示了如何使用Model Context Protocol (MCP) 构建完整的AI应用生态系统，特别集成了微信公众号文章爬取功能。项目包含多个MCP服务器，提供天气查询、数学计算、文件操作和微信文章爬取等功能。



## ✨ 核心特性

- 🤖 **微信公众号爬取** - 使用Selenium自动化浏览器爬取微信公众号文章
- 🌤️ **天气查询** - 集成OpenWeather API提供实时天气信息
- 🧮 **数学计算** - 提供基础数学运算功能
- 📝 **文件操作** - 支持文件读写操作
- 🖼️ **图片处理** - 自动下载文章图片并转换为本地文件
- 🔧 **Makefile支持** - 简化项目管理和部署

## 🚀 快速开始

### 使用Makefile（推荐）

```bash
# 查看所有可用命令
make help

# 初始化项目（包含环境设置、依赖安装、配置等）
make init

# 查看项目状态
make status

# 🎯 一键启动所有服务器和客户端（推荐）
make run-all

# 🧪 运行服务器演示和测试
make demo          # 运行服务器演示，验证所有模块
make test          # 运行项目测试
make one-sentence-demo  # 演示一句话读书笔记功能

# 单独运行服务器
make run-weixin    # 运行微信公众号爬取服务器
make run-weather   # 运行天气查询服务器
```

### 手动安装

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env  # 然后编辑.env文件

# 运行服务器
python weixin_server.py
```

## 🛠️ 技术架构

### MCP服务器

1. **微信公众号爬取服务器** (`weixin_server.py`)
   - 提供 `crawl_weixin_article` 工具 - 爬取微信公众号文章
   - 提供 `analyze_article_content` 工具 - 分析文章内容
   - 提供 `get_article_statistics` 工具 - 获取文章统计信息
   - 提供 `save_article_to_file` 工具 - 保存文章到文件
   - 提供 `generate_one_sentence_summary` 工具 - 生成一句话读书笔记
   - 提供 `generate_reading_notes` 工具 - 生成多种风格的读书笔记
   - 提供 `create_and_save_reading_notes` 工具 - 生成并保存读书笔记
   - **⭐ 提供 `crawl_and_create_reading_notes` 工具 - 一句话完成全流程**
   - 支持图片下载和多格式文件保存

2. **天气服务器** (`weather_server.py`)
   - 提供 `query_weather` 工具
   - 集成OpenWeather API
   - 支持中英文城市名查询

3. **数学计算服务器** (`math_server.py`)
   - 提供基础数学运算功能
   - 支持复杂数学表达式计算

4. **文件操作服务器** (`write_server.py`)
   - 提供 `write_file` 工具
   - 支持自动文件命名
   - 包含安全路径检查

5. **问候服务器** (`greeter_server.py`)
   - 提供简单的问候功能
   - 演示MCP基本用法

### MCP客户端

- **多服务器管理**: 同时连接多个MCP服务器
- **LLM集成**: 支持通义千问和兼容API
- **智能工具调用**: 自动选择合适的工具
- **交互式聊天**: 命令行聊天界面

## 🔧 开发工具

### 🎯 一键启动功能

项目提供了便捷的一键启动功能，可以同时启动所有MCP服务器和客户端：

```bash
# 一键启动所有服务器和客户端
make run-all
```

这个命令会：
1. 启动MCP客户端
2. 客户端自动管理和连接所有配置的服务器
3. 提供统一的交互界面

### 🧪 服务器演示

运行服务器演示来验证所有模块的正确性：

```bash
# 运行服务器演示
make demo
```

这个命令会：
1. 测试所有5个MCP服务器模块的导入
2. 验证依赖包的正确安装
3. 显示详细的测试结果和使用说明
4. 提供MCP协议的基本说明

### 📊 进程管理器

项目包含一个智能进程管理器 `process_manager.py`，提供更精细的服务器控制：

```bash
# 查看服务器状态
make status-servers
# 或直接使用
venv/bin/python process_manager.py status

# 停止所有服务器
make stop-all
# 或直接使用
venv/bin/python process_manager.py stop-all

# 重启所有服务器
make restart-all
# 或直接使用
venv/bin/python process_manager.py restart-all

# 查看服务器日志
make logs
# 或直接使用
venv/bin/python process_manager.py logs

# 管理单个服务器
venv/bin/python process_manager.py start weixin   # 启动微信服务器
venv/bin/python process_manager.py stop weixin    # 停止微信服务器
```

### 📁 日志管理

所有服务器的日志都保存在 `logs/` 目录中：

```
logs/
├── weixin.log      # 微信服务器日志
├── weather.log     # 天气服务器日志
├── math.log        # 数学服务器日志
├── write.log       # 文件服务器日志
├── greeter.log     # 问候服务器日志
├── weixin.pid      # 进程ID文件
├── weather.pid
└── ...
```

查看实时日志：
```bash
# 查看所有日志文件
make logs

# 查看特定服务器的实时日志
tail -f logs/weixin.log
tail -f logs/weather.log
```

### Makefile命令

```bash
# 项目管理
make help          # 显示帮助信息
make init          # 初始化项目（推荐首次使用）
make status        # 查看项目状态
make config        # 配置环境变量
make clean         # 清理项目文件
make clean-all     # 深度清理（包括虚拟环境）

# 依赖管理
make setup         # 设置虚拟环境
make install       # 安装依赖
make update        # 更新依赖

# 运行服务器
make run-all       # 🚀 一键启动所有服务器和客户端（推荐）
make run-weixin    # 运行微信公众号爬取服务器
make run-weather   # 运行天气查询服务器
make run-math      # 运行数学计算服务器
make run-greeter   # 运行问候服务器
make run-write     # 运行文件写入服务器
make run-client    # 运行MCP客户端

# 服务器管理
make stop-all      # 停止所有服务器
make restart-all   # 重启所有服务器
make status-servers # 查看服务器状态
make logs          # 查看服务器日志

# 测试和检查
make test          # 运行测试
make demo          # 运行服务器演示
make check-chrome  # 检查Chrome和ChromeDriver

# 系统依赖（macOS）
make install-system-deps  # 安装Chrome和ChromeDriver

# 发布
make dist          # 创建发布包
```

### 配置文件

#### 服务器配置 (`servers_config.json`)

```json
{
  "mcpServers": {
    "weixin": {
      "command": "venv/bin/python",
      "args": ["weixin_server.py"],
      "env": {
        "ARTICLES_DIR": "articles",
        "DOWNLOAD_IMAGES": "true",
        "HEADLESS": "true",
        "WAIT_TIME": "10"
      }
    },
    "weather": {
      "command": "python3",
      "args": ["weather_server.py"]
    },
    "math": {
      "command": "python3",
      "args": ["math_server.py"]
    },
    "write": {
      "command": "python3",
      "args": ["write_server.py"]
    },
    "greeter": {
      "command": "python3",
      "args": ["greeter_server.py"]
    }
  }
}
```

#### 环境变量 (`.env`)

```env
# OpenWeather API Key
WEATHER_API_KEY=your_weather_api_key_here
OPENWEATHER_API_KEY=your_weather_api_key_here

# LLM Configuration (通义千问)
QWEN_API_KEY=your_qwen_api_key_here
LLM_API_KEY=your_qwen_api_key_here
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL=qwen-plus
```

## 📱 微信公众号爬取功能

### 功能特性

- **自动爬取**: 使用Selenium自动化浏览器爬取微信公众号文章
- **内容提取**: 智能提取文章标题、作者、发布时间、正文内容
- **图片下载**: 自动下载文章中的图片并保存到本地
- **多格式保存**: 支持JSON、TXT、HTML三种格式保存文章
- **内容分析**: 提供文章统计、关键词提取、图片分析等功能

### 使用方法

1. **启动微信爬取服务器**
   ```bash
   make run-weixin
   ```

2. **在MCP客户端中使用**
   ```python
   # 爬取文章
   result = await client.call_tool("crawl_weixin_article", {
       "url": "https://mp.weixin.qq.com/s/...",
       "download_images": True,
       "custom_filename": "my_article"
   })
   
   # 分析文章内容
   analysis = await client.call_tool("analyze_article_content", {
       "article_data": article_data,
       "analysis_type": "full"
   })
   ```

3. **文件输出结构**
   ```
   articles/
   └── 文章标题_20240101_120000/
       ├── 文章标题.json    # 完整文章数据
       ├── 文章标题.txt     # 纯文本内容
       ├── 文章标题.html    # HTML格式
       └── images/          # 图片文件夹
           ├── img_1.jpg
           ├── img_2.png
           └── ...
   ```

### 支持的工具

- `crawl_weixin_article` - 爬取微信公众号文章
- `analyze_article_content` - 分析文章内容
- `get_article_statistics` - 获取文章统计信息
- `save_article_to_file` - 保存文章到文件

## 📚 MCP协议说明

Model Context Protocol (MCP) 是一个开放协议，用于标准化AI应用程序如何提供上下文、数据源和工具给大型语言模型。

### 核心概念

1. **工具 (Tools)**: 服务器提供的可调用功能
2. **资源 (Resources)**: 服务器管理的数据资源
3. **提示 (Prompts)**: 预定义的提示模板
4. **传输 (Transport)**: 客户端和服务器之间的通信方式

### 优势

- **标准化**: 统一的协议规范
- **可扩展**: 支持自定义工具和资源
- **安全**: 明确的权限和访问控制
- **高效**: 基于JSON-RPC 2.0的高效通信

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 🔗 相关链接

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io/)
- [Go SDK 文档](https://github.com/modelcontextprotocol/go-sdk)
- [OpenWeather API](https://openweathermap.org/api)

## ❓ 常见问题

### Q: 如何获取OpenWeather API Key?
A: 访问 [OpenWeather](https://openweathermap.org/api) 注册账户并获取免费API密钥。

### Q: 如何获取通义千问API Key?
A: 访问 [阿里云百炼](https://bailian.console.aliyun.com/) 注册账户并获取API密钥。

### Q: 微信文章爬取失败怎么办?
A: 1) 检查Chrome和ChromeDriver是否正确安装 2) 确认微信文章URL格式正确 3) 检查网络连接 4) 运行 `make check-chrome` 检查环境

### Q: 如何安装Chrome和ChromeDriver?
A: 在macOS上运行 `make install-system-deps` 自动安装，或手动安装Chrome浏览器和ChromeDriver。

### Q: 支持哪些LLM提供商?
A: 支持通义千问和所有兼容OpenAI API格式的提供商。

### Q: 如何添加新的MCP服务器?
A: 1) 实现新的服务器程序 2) 在 `servers_config.json` 中添加配置 3) 重启客户端

### Q: 遇到连接错误怎么办?
A: 检查服务器是否正常运行，确认配置文件路径正确，验证环境变量设置。运行 `make status` 查看项目状态。

### Q: 如何清理项目文件?
A: 运行 `make clean` 清理临时文件，或 `make clean-all` 进行深度清理（包括虚拟环境）。 
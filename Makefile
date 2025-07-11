# 微信公众号文章爬取 MCP 项目 Makefile

# 变量定义
PYTHON = python3
VENV = venv
VENV_BIN = $(VENV)/bin
PIP = $(VENV_BIN)/pip
PYTHON_VENV = $(VENV_BIN)/python

# 项目配置
PROJECT_NAME = python-wechat-mcp
WEATHER_API_KEY = 99b871be442783333b082ee47bcba7f4
QWEN_API_KEY = sk-a6aaf8beba18425e9942c4a33ae58caf

# 颜色定义
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help setup install test demo example clean run-weixin run-weather run-math run-greeter run-write run-client run-all stop-all status-servers logs restart-all config status

# 默认目标
help:
	@echo "$(BLUE)微信公众号文章爬取 MCP 项目$(NC)"
	@echo "$(BLUE)================================$(NC)"
	@echo ""
	@echo "$(GREEN)可用命令:$(NC)"
	@echo "  $(YELLOW)setup$(NC)        - 设置虚拟环境并安装依赖"
	@echo "  $(YELLOW)install$(NC)      - 安装项目依赖"
	@echo "  $(YELLOW)test$(NC)         - 运行测试"
	@echo "  $(YELLOW)demo$(NC)         - 运行服务器演示"
	@echo "  $(YELLOW)example$(NC)      - 运行微信爬虫示例"
	@echo "  $(YELLOW)config$(NC)       - 配置环境变量"
	@echo "  $(YELLOW)status$(NC)       - 查看项目状态"
	@echo ""
	@echo "$(GREEN)运行服务器:$(NC)"
	@echo "  $(YELLOW)run-all$(NC)      - 🚀 启动所有服务器和客户端（推荐）"
	@echo "  $(YELLOW)run-weixin$(NC)   - 运行微信公众号爬取服务器"
	@echo "  $(YELLOW)run-weather$(NC)  - 运行天气查询服务器"
	@echo "  $(YELLOW)run-math$(NC)     - 运行数学计算服务器"
	@echo "  $(YELLOW)run-greeter$(NC)  - 运行问候服务器"
	@echo "  $(YELLOW)run-write$(NC)    - 运行文件写入服务器"
	@echo "  $(YELLOW)run-client$(NC)   - 运行MCP客户端"
	@echo ""
	@echo "$(GREEN)服务器管理:$(NC)"
	@echo "  $(YELLOW)stop-all$(NC)     - 停止所有服务器"
	@echo "  $(YELLOW)restart-all$(NC)  - 重启所有服务器"
	@echo "  $(YELLOW)status-servers$(NC) - 查看服务器状态"
	@echo "  $(YELLOW)logs$(NC)         - 查看服务器日志"
	@echo ""
	@echo "$(GREEN)其他:$(NC)"
	@echo "  $(YELLOW)clean$(NC)        - 清理项目文件"
	@echo "  $(YELLOW)help$(NC)         - 显示此帮助信息"

# 设置虚拟环境
setup:
	@echo "$(BLUE)设置虚拟环境...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)创建虚拟环境...$(NC)"; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "$(YELLOW)升级pip...$(NC)"
	@$(PIP) install --upgrade pip
	@echo "$(GREEN)虚拟环境设置完成!$(NC)"

# 安装依赖
install: setup
	@echo "$(BLUE)安装项目依赖...$(NC)"
	@$(PIP) install -r requirements.txt 2>/dev/null || $(PIP) install \
		selenium \
		beautifulsoup4 \
		requests \
		webdriver-manager \
		Pillow \
		lxml \
		mcp \
		openai
	@echo "$(GREEN)依赖安装完成!$(NC)"

# 创建requirements.txt
requirements.txt:
	@echo "$(YELLOW)创建requirements.txt...$(NC)"
	@echo "# 微信公众号文章爬取 MCP 项目依赖" > requirements.txt
	@echo "selenium>=4.0.0" >> requirements.txt
	@echo "beautifulsoup4>=4.12.0" >> requirements.txt
	@echo "requests>=2.31.0" >> requirements.txt
	@echo "webdriver-manager>=4.0.0" >> requirements.txt
	@echo "Pillow>=10.0.0" >> requirements.txt
	@echo "lxml>=4.9.0" >> requirements.txt
	@echo "mcp>=1.0.0" >> requirements.txt
	@echo "$(GREEN)requirements.txt 创建完成!$(NC)"

# 配置环境变量
config:
	@echo "$(BLUE)配置环境变量...$(NC)"
	@echo "# 微信公众号文章爬取 MCP 项目环境变量" > .env
	@echo "WEATHER_API_KEY=$(WEATHER_API_KEY)" >> .env
	@echo "QWEN_API_KEY=$(QWEN_API_KEY)" >> .env
	@echo "OPENWEATHER_API_KEY=$(WEATHER_API_KEY)" >> .env
	@echo "LLM_API_KEY=$(QWEN_API_KEY)" >> .env
	@echo "BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1" >> .env
	@echo "MODEL=qwen-plus" >> .env
	@echo "$(GREEN)环境变量配置完成!$(NC)"

# 查看项目状态
status:
	@echo "$(BLUE)项目状态检查$(NC)"
	@echo "$(BLUE)===============$(NC)"
	@echo ""
	@echo "$(YELLOW)虚拟环境:$(NC)"
	@if [ -d "$(VENV)" ]; then \
		echo "  $(GREEN)✓ 虚拟环境已创建$(NC)"; \
	else \
		echo "  $(RED)✗ 虚拟环境未创建$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Python版本:$(NC)"
	@if [ -f "$(PYTHON_VENV)" ]; then \
		echo "  $(GREEN)✓ $(shell $(PYTHON_VENV) --version)$(NC)"; \
	else \
		echo "  $(RED)✗ Python未安装$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)依赖检查:$(NC)"
	@if [ -f "$(PYTHON_VENV)" ]; then \
		$(PYTHON_VENV) -c "import selenium; print('  $(GREEN)✓ selenium$(NC)')" 2>/dev/null || echo "  $(RED)✗ selenium$(NC)"; \
		$(PYTHON_VENV) -c "import bs4; print('  $(GREEN)✓ beautifulsoup4$(NC)')" 2>/dev/null || echo "  $(RED)✗ beautifulsoup4$(NC)"; \
		$(PYTHON_VENV) -c "import requests; print('  $(GREEN)✓ requests$(NC)')" 2>/dev/null || echo "  $(RED)✗ requests$(NC)"; \
		$(PYTHON_VENV) -c "import mcp; print('  $(GREEN)✓ mcp$(NC)')" 2>/dev/null || echo "  $(RED)✗ mcp$(NC)"; \
		$(PYTHON_VENV) -c "import openai; print('  $(GREEN)✓ openai$(NC)')" 2>/dev/null || echo "  $(RED)✗ openai$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)项目文件:$(NC)"
	@if [ -f "weixin_server.py" ]; then \
		echo "  $(GREEN)✓ 微信服务器$(NC)"; \
	else \
		echo "  $(RED)✗ 微信服务器$(NC)"; \
	fi
	@if [ -f "weixin_spider.py" ]; then \
		echo "  $(GREEN)✓ 微信爬虫$(NC)"; \
	else \
		echo "  $(RED)✗ 微信爬虫$(NC)"; \
	fi
	@if [ -f "servers_config.json" ]; then \
		echo "  $(GREEN)✓ 服务器配置$(NC)"; \
	else \
		echo "  $(RED)✗ 服务器配置$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)环境变量:$(NC)"
	@if [ -f ".env" ]; then \
		echo "  $(GREEN)✓ 环境变量文件存在$(NC)"; \
	else \
		echo "  $(RED)✗ 环境变量文件不存在$(NC)"; \
	fi

# 测试项目
test: install
	@echo "$(BLUE)运行项目测试...$(NC)"
	@$(PYTHON) test_weixin_server.py

# 运行服务器演示
demo: install
	@echo "$(BLUE)运行MCP服务器演示...$(NC)"
	@$(PYTHON_VENV) demo_servers.py

# 运行微信爬虫示例
example: install
	@echo "$(BLUE)运行微信爬虫示例...$(NC)"
	@$(PYTHON_VENV) weixin_example.py

# 演示一句话读书笔记功能
one-sentence-demo: install
	@echo "$(BLUE)演示一句话读书笔记功能...$(NC)"
	@$(PYTHON_VENV) demo_one_sentence_notes.py

# 演示一句话完成全流程功能
one-command-demo: install
	@echo "$(BLUE)演示一句话完成全流程功能...$(NC)"
	@$(PYTHON_VENV) demo_one_command.py

# 运行微信服务器
run-weixin: install
	@echo "$(BLUE)启动微信公众号文章爬取服务器...$(NC)"
	@echo "$(YELLOW)按 Ctrl+C 停止服务器$(NC)"
	@$(PYTHON_VENV) weixin_server.py

# 运行天气服务器
run-weather: install config
	@echo "$(BLUE)启动天气查询服务器...$(NC)"
	@echo "$(YELLOW)按 Ctrl+C 停止服务器$(NC)"
	@export $(shell cat .env | grep -v '^#' | xargs) && $(PYTHON_VENV) weather_server.py

# 运行数学服务器
run-math: install
	@echo "$(BLUE)启动数学计算服务器...$(NC)"
	@echo "$(YELLOW)按 Ctrl+C 停止服务器$(NC)"
	@$(PYTHON_VENV) math_server.py

# 运行问候服务器
run-greeter: install
	@echo "$(BLUE)启动问候服务器...$(NC)"
	@echo "$(YELLOW)按 Ctrl+C 停止服务器$(NC)"
	@$(PYTHON_VENV) greeter_server.py

# 运行文件写入服务器
run-write: install
	@echo "$(BLUE)启动文件写入服务器...$(NC)"
	@echo "$(YELLOW)按 Ctrl+C 停止服务器$(NC)"
	@$(PYTHON_VENV) write_server.py

# 运行MCP客户端
run-client: install config
	@echo "$(BLUE)启动MCP客户端...$(NC)"
	@export $(shell cat .env | grep -v '^#' | xargs) && $(PYTHON_VENV) qwen3_mcp.py

# 启动所有服务器和客户端
run-all: install config
	@echo "$(BLUE)启动MCP客户端（自动管理所有服务器）...$(NC)"
	@echo "$(YELLOW)MCP客户端将自动启动和管理所有配置的服务器$(NC)"
	@echo "$(YELLOW)按 Ctrl+C 停止客户端和所有服务器$(NC)"
	@echo ""
	@export $(shell cat .env | grep -v '^#' | xargs) && $(PYTHON_VENV) qwen3_mcp.py

# 停止所有服务器
stop-all:
	@echo "$(BLUE)停止所有MCP服务器...$(NC)"
	@$(PYTHON_VENV) process_manager.py stop-all

# 查看所有服务器状态
status-servers:
	@$(PYTHON_VENV) process_manager.py status

# 查看服务器日志
logs:
	@$(PYTHON_VENV) process_manager.py logs

# 重启所有服务器
restart-all:
	@echo "$(BLUE)重启所有MCP服务器...$(NC)"
	@$(PYTHON_VENV) process_manager.py restart-all

# 清理项目
clean:
	@echo "$(BLUE)清理项目文件...$(NC)"
	@echo "$(YELLOW)停止所有服务器...$(NC)"
	@$(MAKE) --no-print-directory stop-all 2>/dev/null || true
	@echo "$(YELLOW)清理Python缓存...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(YELLOW)清理日志文件...$(NC)"
	@rm -rf logs
	@find . -name "*.log" -delete 2>/dev/null || true
	@echo "$(YELLOW)清理临时文件...$(NC)"
	@find . -name "*.tmp" -delete 2>/dev/null || true
	@echo "$(GREEN)清理完成!$(NC)"

# 深度清理（包括虚拟环境）
clean-all: clean
	@echo "$(BLUE)深度清理项目...$(NC)"
	@echo "$(YELLOW)删除虚拟环境...$(NC)"
	@rm -rf $(VENV)
	@echo "$(YELLOW)删除下载的文章...$(NC)"
	@rm -rf articles
	@echo "$(YELLOW)删除环境变量文件...$(NC)"
	@rm -f .env
	@echo "$(GREEN)深度清理完成!$(NC)"

# 初始化项目（完整设置）
init: clean-all setup install requirements.txt config
	@echo "$(GREEN)项目初始化完成!$(NC)"
	@echo ""
	@echo "$(BLUE)接下来可以:$(NC)"
	@echo "  $(YELLOW)make test$(NC)         - 运行测试"
	@echo "  $(YELLOW)make run-weixin$(NC)   - 启动微信服务器"
	@echo "  $(YELLOW)make status$(NC)       - 查看项目状态"

# 更新项目
update: setup
	@echo "$(BLUE)更新项目依赖...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install --upgrade \
		selenium \
		beautifulsoup4 \
		requests \
		webdriver-manager \
		Pillow \
		lxml \
		mcp
	@echo "$(GREEN)更新完成!$(NC)"

# 创建发布包
dist: clean
	@echo "$(BLUE)创建发布包...$(NC)"
	@mkdir -p dist
	@tar -czf dist/$(PROJECT_NAME)-$(shell date +%Y%m%d).tar.gz \
		--exclude=venv \
		--exclude=.git \
		--exclude=dist \
		--exclude=articles \
		--exclude=.env \
		--exclude=__pycache__ \
		--exclude=*.pyc \
		.
	@echo "$(GREEN)发布包创建完成: dist/$(PROJECT_NAME)-$(shell date +%Y%m%d).tar.gz$(NC)"

# 安装系统依赖（macOS）
install-system-deps:
	@echo "$(BLUE)安装系统依赖...$(NC)"
	@if command -v brew >/dev/null 2>&1; then \
		echo "$(YELLOW)安装Chrome和ChromeDriver...$(NC)"; \
		brew install --cask google-chrome; \
		brew install chromedriver; \
		echo "$(GREEN)系统依赖安装完成!$(NC)"; \
	else \
		echo "$(RED)请先安装Homebrew: https://brew.sh/$(NC)"; \
	fi

# 检查Chrome和ChromeDriver
check-chrome:
	@echo "$(BLUE)检查Chrome和ChromeDriver...$(NC)"
	@if command -v google-chrome >/dev/null 2>&1 || command -v chrome >/dev/null 2>&1; then \
		echo "  $(GREEN)✓ Chrome已安装$(NC)"; \
	else \
		echo "  $(RED)✗ Chrome未安装$(NC)"; \
	fi
	@if command -v chromedriver >/dev/null 2>&1; then \
		echo "  $(GREEN)✓ ChromeDriver已安装$(NC)"; \
		echo "  $(YELLOW)版本: $(shell chromedriver --version)$(NC)"; \
	else \
		echo "  $(RED)✗ ChromeDriver未安装$(NC)"; \
	fi 
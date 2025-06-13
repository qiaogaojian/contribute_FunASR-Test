# Git MCP Server 配置指南

## 概述

Git MCP Server 是一个 Model Context Protocol 服务器，它使大型语言模型能够与 Git 仓库交互，提供仓库管理、代码差异比较、提交更改等工具。

## 安装方法

### 使用 UV (推荐)

使用 uv 时无需特定安装，可以直接使用 uvx 运行服务器：

```bash
uvx mcp-server-git --repository path/to/git/repo
```

### 使用 PIP

通过 pip 安装：

```bash
pip install mcp-server-git
```

安装后运行：

```bash
python -m mcp_server_git
```

## 配置方法

### Claude Desktop 配置

在 `claude_desktop_config.json` 中添加以下配置：

#### UV 安装方式：
```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "path/to/git/repo"]
    }
  }
}
```

#### PIP 安装方式：
```json
{
  "mcpServers": {
    "git": {
      "command": "python",
      "args": ["-m", "mcp_server_git", "--repository", "path/to/git/repo"]
    }
  }
}
```

#### Docker 方式：
```json
{
  "mcpServers": {
    "git": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", 
        "--mount", "type=bind,src=/Users/username,dst=/Users/username", 
        "mcp/git"
      ]
    }
  }
}
```

### VS Code 配置

#### 用户设置 (JSON)：
```json
{
  "mcp": {
    "servers": {
      "git": {
        "command": "uvx",
        "args": ["mcp-server-git"]
      }
    }
  }
}
```

#### 工作区配置 (.vscode/mcp.json)：
```json
{
  "servers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    }
  }
}
```

#### Docker 在 VS Code 中的配置：
```json
{
  "mcp": {
    "servers": {
      "git": {
        "command": "docker",
        "args": [
          "run", "--rm", "-i",
          "--mount", "type=bind,src=${workspaceFolder},dst=/workspace",
          "mcp/git"
        ]
      }
    }
  }
}
```

### Zed 编辑器配置

在 `settings.json` 中添加：

#### UV 方式：
```json
{
  "context_servers": {
    "mcp-server-git": {
      "command": {
        "path": "uvx",
        "args": ["mcp-server-git"]
      }
    }
  }
}
```

#### PIP 安装方式：
```json
{
  "context_servers": {
    "mcp-server-git": {
      "command": {
        "path": "python",
        "args": ["-m", "mcp_server_git"]
      }
    }
  }
}
```

### Cursor 编辑器配置

#### 全局配置 (~/.cursor/mcp.json)：
```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    }
  }
}
```

#### 项目配置 (.cursor/mcp.json)：
```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    }
  }
}
```

## 可用的 Git 工具

Git MCP Server 提供以下 Git 操作工具：

### 基本操作
- `git_status`: 显示工作树状态
- `git_diff_unstaged`: 显示未暂存的更改
- `git_diff_staged`: 显示已暂存的更改
- `git_diff`: 显示分支/提交之间的差异
- `git_add`: 暂存文件内容
- `git_reset`: 取消暂存所有更改
- `git_commit`: 记录更改到仓库
- `git_init`: 初始化 Git 仓库

### 仓库导航
- `git_log`: 显示提交日志
- `git_show`: 显示提交的内容
- `git_create_branch`: 创建新分支
- `git_checkout`: 切换分支

## 调试方法

### 使用 MCP 检查器调试服务器：
```bash
npx @modelcontextprotocol/inspector uvx mcp-server-git
```

### 开发安装的调试：
```bash
cd path/to/servers/src/git
npx @modelcontextprotocol/inspector uv run mcp-server-git
```

### 检查日志：
```bash
# macOS/Linux
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log

# Windows
# 检查 Claude 应用数据目录中的日志文件
```

## 使用示例

一旦服务器安装完成，AI 助手将能够：

1. **查看仓库状态**：检查当前工作目录的 Git 状态
2. **比较代码差异**：查看文件的更改内容
3. **提交更改**：暂存和提交代码更改
4. **分支管理**：创建、切换和管理 Git 分支
5. **查看历史**：浏览提交历史和特定提交的详细信息

## 注意事项

1. **安全性**：MCP 服务器可以在您的机器上运行任意代码，只添加来自可信来源的服务器
2. **权限**：确保 AI 助手有适当的权限访问您的 Git 仓库
3. **路径配置**：正确配置仓库路径，确保服务器能够访问目标 Git 仓库
4. **环境变量**：某些配置可能需要设置适当的环境变量

## 故障排除

1. **服务器无法启动**：检查 uv/uvx 是否正确安装并在 PATH 中
2. **权限错误**：确保对 Git 仓库有读写权限
3. **路径问题**：验证仓库路径是否正确且存在
4. **依赖问题**：确保所有必需的依赖项都已安装

通过正确配置 Git MCP Server，您可以让 AI 助手直接与您的 Git 仓库交互，大大提高开发效率和代码管理能力。
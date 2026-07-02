# Node.js / npm 使用与排查指南（中文）

本文档整理了 Node.js / npm 的常用安装、配置、镜像切换、缓存清理与常见问题排查方法，适用于本地开发和 CI 环境。

## 目录
- 概览
- 前置要求
- Node.js 与 nvm
- npm 常用配置与镜像
- 常见问题与排查
- CI 集成建议
- 参考链接

## 概览

本文档包含：Node 版本管理建议、npm 镜像与缓存操作、常见安装与使用问题的定位与解决步骤。

## 前置要求

- 已安装 Git 与基本 shell（PowerShell / Bash）
- 已安装 Node.js（建议使用 nvm 管理多个版本）
- npm 可用且在 PATH 中

## Node.js 与 nvm

推荐使用 nvm 安装与切换 Node 版本：

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# 重启 shell 或运行 source ~/.nvm/nvm.sh
nvm install stable
nvm use stable
```

## npm 常用配置与镜像

- 切换 registry（中国大陆建议）：

```bash
npm config set registry https://registry.npmmirror.com
npm config get registry
```

- 查看与清理缓存：

```bash
npm config get cache
npm cache clean --force
```

- 查看全局安装路径：

```bash
npm root -g
```

- 安装依赖：

```bash
npm install
```

- 仅安装生产依赖：

```bash
npm install --omit=dev
```

## 常见问题与排查步骤

- 命令不可用：检查 Node.js 和 npm 是否已正确安装：

```bash
node --version
npm --version
```

- 检查全局安装路径是否在 PATH 中（Windows）：

```powershell
where.exe npm
```

- registry 与网络问题：

```bash
npm config get registry
npm ping
```

- 权限问题（Unix）：避免使用 sudo 安装全局包，推荐修复 npm 全局目录权限或使用 nvm。

- 依赖安装失败：
  - 清理缓存后重试：

```bash
npm cache clean --force
npm install
```

  - 删除 node_modules 和 package-lock.json 后重装：

```bash
rm -rf node_modules package-lock.json
npm install
```

## CI 集成建议

- 在 CI 中使用 npm 安装依赖：

```yaml
name: Node.js CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 'lts/*'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
```

## 参考链接

- nvm: https://github.com/nvm-sh/nvm
- npm 镜像（国内）: https://registry.npmmirror.com
- npm 官方文档: https://docs.npmjs.com/

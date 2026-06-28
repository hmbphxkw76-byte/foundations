# Node.js 与 npm 配置说明

## 文档说明

本文件整合了原有的 npm 安装与配置说明内容，方便直接查看与传播。

## 1. 安装 nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

安装完成后，重新打开终端，再执行：

```bash
nvm install stable
```

## 2. 配置 npm 镜像源

```bash
npm config set registry https://registry.npmmirror.com
```

查看当前镜像源：

```bash
npm config get registry
```

查看缓存路径：

```bash
npm config get cache
```

清理缓存：

```bash
npm cache clean --force
```

## 3. 使用 Promptfoo 示例

```bash
mkdir promptfoo-demo && cd promptfoo-demo
npm init -y
npm install promptfoo --save-dev
npm approve-scripts promptfoo
```

## 4. 注意事项

- 若遇到权限问题，请确认当前用户具备安装和修改全局配置的权限。
- 建议先确认 Node.js 版本与项目兼容性后再安装依赖。
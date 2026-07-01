# Promptfoo 使用说明

## 1.全局安装

```bash
npm install -g promptfoo --allow-scripts
```

## 2.验证安装

运行以下命令检查是否安装成功：

```bash
promptfoo --version
```

## 3.初始化

在项目根目录执行初始化命令，会生成配置示例文件并引导下一步：

```bash
promptfoo init

# 或使用 npx 保证初始化脚本为最新版本：
npx promptfoo@latest init
```

## 4.红队测试基础命令

- 用于初始化基本的红队配置：

  ```bash
  promptfoo redteam init
  ```

- 生成对抗性测试用例以及对目标进行测试：

  ```bash
  promptfoo redteam run
  ```

- 查看结果：

  ```bash
  promptfoo redteam report
  ```

## 4.1分步执行步骤

- 从模板生成测试用例（生成 redteam.yaml）：

  ```bash
  promptfoo redteam generate --config promptfoo-redteam-config.yaml
  ```

- 执行评估（读取 redteam.yaml）：

  ```bash
  promptfoo redteam eval --config redteam.yaml
  ```

## 4.2合并 generate + eval 两步

```bash
promptfoo redteam run --config promptfoo-redteam-config.yaml
```
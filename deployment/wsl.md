# WSL 配置说明

## 文档说明

本文件整合了原有的 WSL 安装、管理与迁移命令内容，便于直接阅读与使用。

## 1. 启用 WSL 相关功能

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

## 2. 安装 WSL

```powershell
wsl --install
```

## 3. 设置默认版本

```powershell
wsl --set-default-version 2
```

## 4. 管理发行版

查看发行版：

```powershell
wsl --list --verbose
```

启动指定发行版：

```powershell
wsl -d Ubuntu
```

停止指定发行版：

```powershell
wsl -t Ubuntu
```

关闭所有实例：

```powershell
wsl --shutdown
```

## 5. 备份与导入

```powershell
wsl --export Ubuntu-22.04 D:\path\ubuntu.tar
wsl --import Ubuntu24 D:\path\WSL D:\path\Ubuntu24.tar --version 2
```

## 6. 注意事项

- 建议使用 WSL 2 以获得更好的兼容性和性能。
- 若启用功能失败，请检查系统版本和管理员权限。
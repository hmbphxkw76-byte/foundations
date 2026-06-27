
# 首先， 启用或关闭 Windows 功能 中选择 适用于 Linux 的 Windows 子系统 和 虚拟机平台

#相关命令：
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart


安装WSL 命令：wsl --install

设置默认WSL版本 wsl --set-default-version 2

查看发行版名称 wsl --list --verbose

启动指定版本 wsl -d Ubuntu

停止指定版本 wsl -t Ubuntu

关闭所有实例：wsl --shutdown

彻底删除 wsl --unregister Ubuntu-26.04

文件备份 wsl --export Ubuntu-22.04 D:\path\ubuntu.tar

文件导入 wsl --import Ubuntu24 D:\path\WSL D:\path\Ubuntu24.tar --version 2

设备默认版本 wsl --set-default ubuntu24


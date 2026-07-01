# Ubuntu 环境下 Ollama 服务配置说明

## 文档说明

本文件整合了原有的 Ollama 服务配置内容，便于在 Ubuntu 系统中快速部署和维护服务。

## 1. 服务配置内容

```ini
/etc/systemd/system/ollama.service

[Unit]
Description=Ollama Service
After=network-online.target
[Service]
ExecStart=/usr/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
Environment="PATH=$PATH"

[Install]
WantedBy=multi-user.target
```

## 2. 使用方法

将上述配置写入服务文件后，执行：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl restart ollama
```

查看状态：

```bash
sudo systemctl status ollama
```

## 3. 注意事项

- 配置前请确认 Ollama 已正确安装。
- 若服务启动失败，请检查日志与执行路径。
- 生产环境下建议根据需要限制访问来源。
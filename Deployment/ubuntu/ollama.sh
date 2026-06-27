#Ubuntu系统中开启侦听服务

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


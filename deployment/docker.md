# Docker 部署与配置说明

## 文档说明

本文件已将原有的 Docker 安装脚本、镜像加速配置示例与说明文档整合为一个统一文档，便于直接阅读和分享。

## 1. Ubuntu安装脚本内容

文件来源：docker_install.sh

```bash
#! /bin/bash

sudo apt-get update

sudo apt-get upgrade -y

sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo systemctl start docker

sudo systemctl enable docker

sudo usermod -aG docker $(whoami)

sudo mkdir -p /etc/docker

sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://docker.m.daocloud.io",
    "https://docker.imgdb.de"
  ]
}
EOF

sudo systemctl daemon-reload

sudo systemctl restart docker

docker info | grep "Registry Mirrors"
```

## 2. Windows Docker Desktop 镜像加速配置

文件来源：windows_docker_mirror.json

```json
{
  "registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io"
  ],
  "builder.gc.defaultKeepStorage": 20,
  "experimental": false
}
```

 

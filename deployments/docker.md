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
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io"
  ]
}

```

## 3. Docker 空间清理命令

以下命令可用于清理 Docker 的磁盘占用，适合在本地环境中定期维护：

```bash
# 1. 查看当前 Docker 空间占用
docker system df

# 2. 清理悬空镜像
docker image prune -f

# 3. 清理已停止的容器
docker rm $(docker ps -aq -f status=exited) 2>/dev/null || true

# 4. 清理未使用的卷（注意：卷中可能包含重要数据，请确认不再需要）
docker volume prune -f

# 5. 清理构建缓存
docker builder prune -f

# 6. 再次查看清理后的空间占用
docker system df
```

> 说明：第 4 步会清理未使用的 Docker 卷，若卷中存放了重要数据，请先确认后再执行。

### 终极清理（慎用）

如果你想一次性清理 Docker 中几乎所有未使用的数据，包括停止的容器、悬空镜像、未使用的网络和构建缓存，可以执行：

```bash
docker system prune -a
```

> 说明：这个命令会删除大量不再使用的 Docker 数据，执行前请确认当前环境中没有需要保留的容器、镜像或缓存。 


## 4. Kali Linux 安装 Docker 的补充配置

如果你是在 Kali Linux 上安装 Docker，除了常规的 Docker 仓库配置外，还可以手动补充 apt 源配置。下面给出一个可直接使用的示例：

```bash
sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

创建 Docker 源文件：

```bash
sudo tee /etc/apt/sources.list.d/docker.list <<'EOF'
#deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian kali-rolling stable

deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable
EOF
```

然后执行：

```bash
sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

> 说明：Kali 系统下，推荐优先使用 Debian 的 `bookworm` 源；若使用 `kali-rolling` 源，可能会遇到兼容性问题。
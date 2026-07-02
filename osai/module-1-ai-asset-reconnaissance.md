# AI-300 模块一：AI 资产探测与指纹识别攻击代码

> OffSec AI-300 (OSAI) 红队备考武器库 - 第一阶段：侦察

---

## 目录

1. [AI API 服务扫描器](#1-ai-api-服务扫描器)
2. [端口扫描与服务发现](#2-端口扫描与服务发现)
3. [模型指纹识别](#3-模型指纹识别)
4. [上下文长度与嵌入模型探测](#4-上下文长度与嵌入模型探测)

---

## 1. AI API 服务扫描器

**功能**：自动化扫描未授权、暴露的 AI 服务端点，如 Ollama、vLLM、OpenAI 兼容 API。

```python
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

class AIAPIScanner:
    def __init__(self, timeout: int = 5, max_workers: int = 10):
        self.timeout = timeout
        self.max_workers = max_workers
        self.ai_endpoints = [
            "/v1/models", "/v1/chat/completions", "/v1/completions",
            "/v1/embeddings", "/api/v1/models", "/api/generate",
            "/generate", "/chat", "/completions", "/health", "/status"
        ]
        self.ai_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-placeholder"
        }

    def scan_single_target(self, target: str) -> Dict[str, Any]:
        results = {
            "target": target,
            "status": "unknown",
            "services": [],
            "headers": {},
            "model_info": None
        }
        
        try:
            for endpoint in self.ai_endpoints:
                url = f"{target}{endpoint}"
                try:
                    response = requests.get(url, headers=self.ai_headers, timeout=self.timeout)
                    
                    if response.status_code != 404:
                        service_info = {
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "content_type": response.headers.get("Content-Type", ""),
                            "server": response.headers.get("Server", ""),
                            "x_model": response.headers.get("X-Model", ""),
                            "x_server": response.headers.get("X-Server", "")
                        }
                        
                        if response.status_code == 200:
                            try:
                                json_data = response.json()
                                if "data" in json_data or "models" in json_data:
                                    service_info["model_info"] = json_data
                            except:
                                pass
                        
                        results["services"].append(service_info)
                        results["status"] = "vulnerable" if response.status_code == 200 else "partial"
                        
                        if not results["headers"]:
                            results["headers"] = dict(response.headers)
                            
                except requests.exceptions.RequestException:
                    continue
                    
        except Exception as e:
            results["error"] = str(e)
            
        return results

    def scan_multiple_targets(self, targets: List[str]) -> List[Dict[str, Any]]:
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_target = {
                executor.submit(self.scan_single_target, target): target
                for target in targets
            }
            
            for future in as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    result = future.result()
                    all_results.append(result)
                except Exception as e:
                    all_results.append({"target": target, "status": "error", "error": str(e)})
                    
        return all_results

    def test_unauthenticated_access(self, target: str) -> Dict[str, Any]:
        test_payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        results = {
            "target": target,
            "unauthenticated": False,
            "response": None,
            "error": None
        }
        
        try:
            response = requests.post(
                f"{target}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json=test_payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                results["unauthenticated"] = True
                results["response"] = response.json()
            elif response.status_code == 401:
                results["unauthenticated"] = False
            else:
                results["unauthenticated"] = "unknown"
                
        except Exception as e:
            results["error"] = str(e)
            
        return results

def main():
    scanner = AIAPIScanner(timeout=3, max_workers=15)
    
    targets = [
        "http://localhost:11434",
        "http://localhost:8000",
        "http://localhost:5000",
        "http://localhost:5001"
    ]
    
    print("[+] Starting AI API Service Scan...")
    print("=" * 60)
    
    scan_results = scanner.scan_multiple_targets(targets)
    
    for result in scan_results:
        print(f"\n[*] Target: {result['target']}")
        print(f"    Status: {result['status']}")
        
        if result["services"]:
            print("    Services Found:")
            for service in result["services"]:
                print(f"      - {service['endpoint']} ({service['status_code']})")
                if "model_info" in service and service["model_info"]:
                    print(f"        Models: {[m.get('id', '') for m in service['model_info'].get('data', [])[:3]]}")
        
        auth_test = scanner.test_unauthenticated_access(result["target"])
        print(f"    Unauthenticated Access: {auth_test['unauthenticated']}")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-5 | 导入依赖 | `requests` 用于HTTP请求，`concurrent.futures` 用于并发扫描 |
| 7-15 | `AIAPIScanner` 类初始化 | 设置超时时间、并发数、常见AI端点列表 |
| 17-19 | AI端点列表 | 包含OpenAI兼容API、Ollama、vLLM等常见端点 |
| 21-25 | 请求头配置 | 模拟浏览器请求，携带占位符API密钥 |
| 27-58 | `scan_single_target` | 扫描单个目标的所有AI端点，记录状态码和响应头 |
| 31-33 | 服务信息结构 | 包含端点、状态码、内容类型、服务器信息 |
| 35-41 | 解析JSON响应 | 如果返回200，尝试提取模型列表信息 |
| 60-80 | `scan_multiple_targets` | 并发扫描多个目标，使用线程池提高效率 |
| 82-103 | `test_unauthenticated_access` | 测试是否存在未授权访问漏洞 |
| 86-88 | 测试Payload | 构造最小化的聊天请求测试API |
| 105-132 | `main` | 主函数：初始化扫描器、定义目标、执行扫描、输出结果 |

---

## 2. 端口扫描与服务发现

**功能**：扫描常见AI服务默认端口，识别Ollama、vLLM、Triton、MLflow等服务。

```python
import socket
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any

class AIPortScanner:
    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
        self.ai_port_map = {
            11434: {"name": "Ollama", "protocol": "HTTP", "endpoint": "/v1/models"},
            8000: {"name": "vLLM/TGI", "protocol": "HTTP", "endpoint": "/v1/models"},
            5001: {"name": "Triton Inference Server", "protocol": "HTTP", "endpoint": "/v2/health/ready"},
            5000: {"name": "MLflow", "protocol": "HTTP", "endpoint": "/api/2.0/mlflow/experiments/list"},
            8080: {"name": "Ray/Dash", "protocol": "HTTP", "endpoint": "/"},
            9200: {"name": "Elasticsearch (Vector DB)", "protocol": "HTTP", "endpoint": "/_cluster/health"},
            8081: {"name": "ChromaDB", "protocol": "HTTP", "endpoint": "/api/v1/collections"},
            6333: {"name": "Qdrant", "protocol": "HTTP", "endpoint": "/collections"},
            19530: {"name": "Milvus", "protocol": "HTTP", "endpoint": "/api/v1/health"},
            4000: {"name": "Pinecone", "protocol": "HTTP", "endpoint": "/v1/projects"},
            8091: {"name": "Couchbase", "protocol": "HTTP", "endpoint": "/pools"},
            27017: {"name": "MongoDB", "protocol": "TCP", "endpoint": None},
            5432: {"name": "PostgreSQL (pgvector)", "protocol": "TCP", "endpoint": None},
            6379: {"name": "Redis (RediSearch)", "protocol": "TCP", "endpoint": None},
            8891: {"name": "Weaviate", "protocol": "HTTP", "endpoint": "/v1/objects"},
            9001: {"name": "DeepEval", "protocol": "HTTP", "endpoint": "/health"}
        }

    def check_port(self, host: str, port: int) -> Dict[str, Any]:
        result = {
            "host": host,
            "port": port,
            "service": self.ai_port_map.get(port, {"name": "Unknown"}),
            "open": False,
            "banner": None,
            "http_response": None
        }
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                if sock.connect_ex((host, port)) == 0:
                    result["open"] = True
                    
                    try:
                        sock.send(b"HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n")
                        banner = sock.recv(1024).decode("utf-8", errors="ignore")
                        result["banner"] = banner[:200]
                    except:
                        pass
                        
        except Exception as e:
            result["error"] = str(e)
            
        return result

    def check_http_service(self, host: str, port: int) -> Dict[str, Any]:
        service_info = self.ai_port_map.get(port, {})
        endpoint = service_info.get("endpoint", "/")
        
        result = {
            "host": host,
            "port": port,
            "service_name": service_info.get("name", "Unknown"),
            "http_accessible": False,
            "status_code": None,
            "content": None,
            "headers": {}
        }
        
        try:
            url = f"http://{host}:{port}{endpoint}"
            response = requests.get(url, timeout=self.timeout)
            
            result["http_accessible"] = True
            result["status_code"] = response.status_code
            result["headers"] = dict(response.headers)
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    result["content"] = json_data
                except:
                    result["content"] = response.text[:500]
                    
        except Exception as e:
            try:
                url = f"https://{host}:{port}{endpoint}"
                response = requests.get(url, timeout=self.timeout, verify=False)
                result["http_accessible"] = True
                result["status_code"] = response.status_code
                result["headers"] = dict(response.headers)
            except:
                result["error"] = str(e)
                
        return result

    def scan_ports(self, host: str, ports: List[int] = None) -> List[Dict[str, Any]]:
        if ports is None:
            ports = list(self.ai_port_map.keys())
            
        results = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self.check_port, host, port) for port in ports]
            
            for future in futures:
                result = future.result()
                if result["open"]:
                    results.append(result)
                    
        http_results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self.check_http_service, host, r["port"])
                for r in results
            ]
            
            for future in futures:
                http_results.append(future.result())
                
        return http_results

def main():
    scanner = AIPortScanner(timeout=1.5)
    
    targets = ["127.0.0.1", "localhost"]
    
    for target in targets:
        print(f"\n[+] Scanning AI services on {target}")
        print("=" * 60)
        
        results = scanner.scan_ports(target)
        
        for result in results:
            print(f"\n[*] Port {result['port']} - {result['service_name']}")
            print(f"    HTTP Accessible: {result['http_accessible']}")
            print(f"    Status Code: {result['status_code']}")
            
            if result["headers"]:
                server = result["headers"].get("server", "")
                x_model = result["headers"].get("x-model", "")
                print(f"    Server: {server}")
                print(f"    X-Model: {x_model}")
                
            if result["content"]:
                if isinstance(result["content"], dict):
                    keys = list(result["content"].keys())[:5]
                    print(f"    Response Keys: {keys}")
                else:
                    print(f"    Response: {result['content'][:100]}...")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-4 | 导入依赖 | `socket` 用于端口扫描，`requests` 用于HTTP探测 |
| 6-7 | `AIPortScanner` 初始化 | 设置超时时间 |
| 9-30 | AI端口映射表 | 包含16个常见AI服务的默认端口和探测端点 |
| 32-56 | `check_port` | 使用socket检查端口是否开放，尝试获取banner |
| 38-40 | socket连接测试 | 连接成功返回0表示端口开放 |
| 42-46 | 获取banner | 发送HTTP HEAD请求获取服务标识 |
| 58-87 | `check_http_service` | 测试开放端口上的HTTP服务，获取响应信息 |
| 69-76 | 解析HTTP响应 | 尝试解析JSON响应或获取文本内容 |
| 78-84 | HTTPS回退 | 如果HTTP失败，尝试HTTPS连接 |
| 89-107 | `scan_ports` | 并发扫描所有AI端口，先检查端口开放再探测HTTP服务 |
| 109-137 | `main` | 主函数：扫描本地主机的AI服务端口 |

---

## 3. 模型指纹识别

**功能**：通过空白Prompt的HTTP响应头和响应特征进行模型指纹识别。

```python
import requests
import json
from typing import Dict, Any, Optional

class ModelFingerprinter:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.model_signatures = {
            "ollama": {
                "headers": {"server": "ollama"},
                "endpoints": ["/v1/models"],
                "response_patterns": ["model", "modified_at", "size"]
            },
            "vllm": {
                "headers": {"server": "vllm"},
                "endpoints": ["/v1/models"],
                "response_patterns": ["id", "object", "owned_by"]
            },
            "text-generation-inference": {
                "headers": {"x-acceleration": "true"},
                "endpoints": ["/v1/models"],
                "response_patterns": ["sha256", "pruned"]
            },
            "openai": {
                "headers": {"openai-model": None},
                "endpoints": ["/v1/models"],
                "response_patterns": ["gpt-", "text-", "embedding-"]
            },
            "ray": {
                "headers": {"x-ray-service": None},
                "endpoints": ["/api/version"],
                "response_patterns": ["ray_version", "python_version"]
            },
            "mlflow": {
                "headers": {"server": "gunicorn"},
                "endpoints": ["/api/2.0/mlflow/experiments/list"],
                "response_patterns": ["experiments", "experiment_id"]
            },
            "chromadb": {
                "headers": {"content-type": "application/json"},
                "endpoints": ["/api/v1/collections"],
                "response_patterns": ["collections", "name", "id"]
            },
            "qdrant": {
                "headers": {"access-control-allow-origin": "*"},
                "endpoints": ["/collections"],
                "response_patterns": ["collections", "result"]
            },
            "milvus": {
                "headers": {"server": "milvus"},
                "endpoints": ["/api/v1/health"],
                "response_patterns": ["status", "version"]
            },
            "weaviate": {
                "headers": {"x-weaviate-version": None},
                "endpoints": ["/v1/objects"],
                "response_patterns": ["objects", "class", "properties"]
            }
        }

    def fingerprint_by_headers(self, headers: Dict[str, str]) -> Optional[str]:
        for model, sig in self.model_signatures.items():
            for header, value in sig["headers"].items():
                header_lower = header.lower()
                if header_lower in headers:
                    header_value = headers[header_lower].lower()
                    if value is None or value.lower() in header_value:
                        return model
        return None

    def fingerprint_by_response(self, response: Dict[str, Any]) -> Optional[str]:
        response_str = json.dumps(response).lower()
        for model, sig in self.model_signatures.items():
            for pattern in sig["response_patterns"]:
                if pattern.lower() in response_str:
                    return model
        return None

    def fingerprint_model(self, base_url: str) -> Dict[str, Any]:
        result = {
            "base_url": base_url,
            "detected_model": None,
            "headers": {},
            "response_sample": None,
            "confidence": 0,
            "evidence": []
        }
        
        test_payloads = [
            {
                "url": f"{base_url}/v1/models",
                "method": "GET",
                "headers": {"Authorization": "Bearer sk-test"}
            },
            {
                "url": f"{base_url}/v1/chat/completions",
                "method": "POST",
                "headers": {"Content-Type": "application/json", "Authorization": "Bearer sk-test"},
                "data": json.dumps({
                    "model": "test",
                    "messages": [{"role": "user", "content": "Hello"}]
                })
            },
            {
                "url": f"{base_url}/api/v1/collections",
                "method": "GET"
            },
            {
                "url": f"{base_url}/health",
                "method": "GET"
            }
        ]
        
        for payload in test_payloads:
            try:
                if payload["method"] == "GET":
                    response = requests.get(
                        payload["url"],
                        headers=payload.get("headers", {}),
                        timeout=self.timeout
                    )
                else:
                    response = requests.post(
                        payload["url"],
                        headers=payload.get("headers", {}),
                        data=payload.get("data"),
                        timeout=self.timeout
                    )
                    
                if response.status_code == 200:
                    result["headers"] = dict(response.headers)
                    try:
                        result["response_sample"] = response.json()
                    except:
                        result["response_sample"] = response.text[:500]
                        
                    detected_by_headers = self.fingerprint_by_headers(dict(response.headers))
                    detected_by_response = None
                    
                    if isinstance(result["response_sample"], dict):
                        detected_by_response = self.fingerprint_by_response(result["response_sample"])
                        
                    if detected_by_headers:
                        result["detected_model"] = detected_by_headers
                        result["evidence"].append(f"Headers match: {detected_by_headers}")
                        result["confidence"] += 50
                        
                    if detected_by_response:
                        result["detected_model"] = detected_by_response
                        result["evidence"].append(f"Response pattern match: {detected_by_response}")
                        result["confidence"] += 50
                        
                    if result["confidence"] >= 50:
                        break
                        
            except Exception:
                continue
                
        return result

def main():
    fingerprinter = ModelFingerprinter(timeout=5)
    
    targets = [
        "http://localhost:11434",
        "http://localhost:8000",
        "http://localhost:5000",
        "http://localhost:8081"
    ]
    
    print("[+] Starting Model Fingerprinting...")
    print("=" * 60)
    
    for target in targets:
        print(f"\n[*] Target: {target}")
        
        result = fingerprinter.fingerprint_model(target)
        
        if result["detected_model"]:
            print(f"    Detected Model: {result['detected_model']}")
            print(f"    Confidence: {result['confidence']}%")
            print(f"    Evidence:")
            for evidence in result["evidence"]:
                print(f"      - {evidence}")
                
            if result["headers"]:
                print(f"    Key Headers:")
                for key, value in list(result["headers"].items())[:5]:
                    print(f"      - {key}: {value}")
        else:
            print(f"    Model not detected or service unavailable")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-4 | 导入依赖 | `requests` 和 `json` 用于HTTP请求和响应解析 |
| 6-7 | `ModelFingerprinter` 初始化 | 设置超时时间 |
| 9-42 | 模型签名数据库 | 包含10种AI服务的特征：响应头、端点、响应模式 |
| 44-53 | `fingerprint_by_headers` | 通过HTTP响应头识别模型类型 |
| 55-62 | `fingerprint_by_response` | 通过响应内容的特征模式识别模型 |
| 64-127 | `fingerprint_model` | 综合指纹识别：尝试多个端点，结合头信息和响应模式 |
| 71-89 | 测试Payload列表 | 包含模型列表、聊天完成、向量数据库集合、健康检查等端点 |
| 91-123 | 执行探测 | 依次尝试各端点，收集头信息和响应数据 |
| 101-117 | 综合判断 | 结合头信息和响应模式给出识别结果和置信度 |
| 129-156 | `main` | 主函数：对多个目标进行模型指纹识别 |

---

## 4. 上下文长度与嵌入模型探测

**功能**：通过少量探测探针测试目标API的上下文长度、嵌入模型类型等物理限制。

```python
import requests
import json
import numpy as np
from typing import Dict, Any, Optional

class ModelProber:
    def __init__(self, base_url: str, api_key: str = "", timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def get_model_list(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=self.headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    def probe_context_length(self) -> Dict[str, Any]:
        result = {
            "max_context_length": None,
            "estimated_length": None,
            "method": "binary_search"
        }
        
        test_messages = [{"role": "user", "content": ""}]
        min_length = 100
        max_length = 100000
        found_length = None
        
        while min_length <= max_length:
            mid_length = (min_length + max_length) // 2
            test_content = "A" * mid_length
            test_messages[0]["content"] = test_content
            
            payload = {
                "model": "gpt-4o",
                "messages": test_messages,
                "max_tokens": 10
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    found_length = mid_length
                    min_length = mid_length + 1
                elif response.status_code == 400:
                    error = response.json().get("error", {}).get("message", "")
                    if "context" in error.lower() or "token" in error.lower():
                        max_length = mid_length - 1
                    else:
                        break
                else:
                    break
                    
            except Exception:
                break
                
        result["estimated_length"] = found_length
        result["max_context_length"] = found_length if found_length else "unknown"
        
        return result

    def probe_embedding_model(self) -> Dict[str, Any]:
        result = {
            "embedding_dimension": None,
            "model_name": None,
            "max_input_length": None,
            "supported_encodings": []
        }
        
        test_texts = ["Hello", "Hello world", "Test"]
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/embeddings",
                headers=self.headers,
                json={
                    "model": "text-embedding-3-small",
                    "input": test_texts,
                    "encoding_format": "float"
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    embedding = data["data"][0]["embedding"]
                    result["embedding_dimension"] = len(embedding)
                    result["model_name"] = data.get("model", "")
                    
                    if result["embedding_dimension"] == 1536:
                        result["model_name"] = result["model_name"] or "text-embedding-ada-002"
                    elif result["embedding_dimension"] == 3072:
                        result["model_name"] = result["model_name"] or "text-embedding-3-large"
                    elif result["embedding_dimension"] == 768:
                        result["model_name"] = result["model_name"] or "BERT/Sentence-BERT"
                    elif result["embedding_dimension"] == 1024:
                        result["model_name"] = result["model_name"] or "all-MiniLM-L6-v2"
                        
                    result["supported_encodings"] = ["float"]
                    
        except Exception as e:
            result["error"] = str(e)
            
        return result

    def probe_token_limit(self) -> Dict[str, Any]:
        result = {
            "max_tokens": None,
            "tested_values": []
        }
        
        token_values = [100, 500, 1000, 2000, 4000, 8000, 16000]
        
        for tokens in token_values:
            payload = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": "Generate a long response."}],
                "max_tokens": tokens
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result["tested_values"].append({"requested": tokens, "success": True})
                    result["max_tokens"] = tokens
                else:
                    result["tested_values"].append({"requested": tokens, "success": False})
                    break
                    
            except Exception:
                result["tested_values"].append({"requested": tokens, "success": False})
                break
                
        return result

    def comprehensive_probe(self) -> Dict[str, Any]:
        print("[+] Starting Comprehensive Model Probing...")
        print("=" * 60)
        
        results = {
            "base_url": self.base_url,
            "models": self.get_model_list(),
            "context_length": self.probe_context_length(),
            "embedding": self.probe_embedding_model(),
            "token_limit": self.probe_token_limit()
        }
        
        return results

def main():
    prober = ModelProber(
        base_url="http://localhost:11434",
        api_key="",
        timeout=15
    )
    
    results = prober.comprehensive_probe()
    
    print(f"\n[*] Target: {results['base_url']}")
    
    if results["models"]:
        model_list = results["models"].get("data", [])[:3]
        print(f"\n[*] Available Models:")
        for model in model_list:
            print(f"    - {model.get('id', '')}")
    
    print(f"\n[*] Context Length:")
    print(f"    Estimated: {results['context_length']['estimated_length']} tokens")
    
    print(f"\n[*] Embedding Model:")
    print(f"    Dimension: {results['embedding']['embedding_dimension']}")
    print(f"    Model Name: {results['embedding']['model_name']}")
    
    print(f"\n[*] Token Limit:")
    print(f"    Maximum Supported: {results['token_limit']['max_tokens']}")
    
    if results["token_limit"]["tested_values"]:
        print(f"    Tested Values:")
        for test in results["token_limit"]["tested_values"]:
            status = "✅" if test["success"] else "❌"
            print(f"      - {status} {test['requested']} tokens")

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-5 | 导入依赖 | `requests`、`json`、`numpy` 用于HTTP请求和数据处理 |
| 7-16 | `ModelProber` 初始化 | 设置基础URL、API密钥、请求头 |
| 18-26 | `get_model_list` | 获取可用模型列表 |
| 28-72 | `probe_context_length` | 二分搜索法探测上下文长度限制 |
| 36-40 | 二分搜索初始化 | 设置搜索范围100-100000 tokens |
| 42-69 | 搜索循环 | 发送不同长度的请求，根据响应判断是否超出限制 |
| 74-111 | `probe_embedding_model` | 探测嵌入模型维度和类型 |
| 87-102 | 解析嵌入响应 | 根据维度推断模型类型（1536=ada-002, 768=BERT等） |
| 113-145 | `probe_token_limit` | 递增测试最大token输出限制 |
| 121-142 | token测试循环 | 测试100到16000的token限制 |
| 147-157 | `comprehensive_probe` | 综合探测所有参数 |
| 159-189 | `main` | 主函数：执行综合探测并输出结果 |

---

## 5. 考试策略与工具安装

### 5.1 考试工具矩阵

**工具能力对比**：

| 工具 | 提示注入 | Jailbreak | RAG攻击 | 多代理 | 嵌入攻击 | 基础设施 | 多轮攻击 |
|------|---------|----------|---------|--------|---------|---------|---------|
| **promptfoo** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **PyRIT** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Garak** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **DeepTeam** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Burp Suite** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Python** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**工具定位**：

| 工具 | 定位 | 适用场景 |
|------|------|---------|
| **promptfoo** | 安全扫描器 | CI/CD 集成、快速安全扫描、合规报告 |
| **PyRIT** | 攻击框架 | 复杂多轮攻击、自定义攻击研究、AI对抗AI |
| **Garak** | LLM漏洞扫描器 | 快速侦察和漏洞扫描、OWASP LLM Top 10 |
| **DeepTeam** | AI红队框架 | 应用层安全测试、入门学习 |
| **Burp Suite** | Web渗透测试工具 | API测试、基础设施攻击、流量分析 |
| **Python** | 通用编程工具 | 自定义脚本、自动化任务、复杂攻击 |

---

### 5.2 考试四阶段策略

```
考试工具链：
┌─────────────────────────────────────────────────────┐
│  Phase 1: 侦察阶段                                  │
│  ├── Nmap / curl / Burp Suite                      │
│  └── promptfoo redteam discover                    │
├─────────────────────────────────────────────────────┤
│  Phase 2: 广度扫描                                  │
│  └── promptfoo redteam run (OWASP/ATLAS预设)        │
├─────────────────────────────────────────────────────┤
│  Phase 3: 深度利用                                  │
│  ├── PyRIT（多轮攻击、自定义策略）                   │
│  └── 手动测试（发现新颖漏洞）                        │
├─────────────────────────────────────────────────────┤
│  Phase 4: 报告撰写                                  │
│  └── 手动撰写专业报告                               │
└─────────────────────────────────────────────────────┘
```

#### Phase 1: 侦察（第 1-4 小时）

```bash
# 使用 Nmap 发现目标
nmap -sV exam-env -p-

# 使用 curl 测试 API 端点
curl http://exam-env/api/v1/health

# 使用 promptfoo 发现目标信息
promptfoo redteam discover --target http://exam-env/api/v1

# 使用本模块脚本扫描AI资产
python module-1-ai-asset-reconnaissance.py
```

#### Phase 2: 广度扫描（第 4-12 小时）

```bash
# 使用 promptfoo 进行全面扫描
promptfoo redteam run --config exam-config.yaml

# 使用 Garak 进行快速漏洞扫描
garak --model openai:chat:target-model --probes all

# 使用 Burp Suite 手动测试 API
```

#### Phase 3: 深度利用（第 12-20 小时）

```bash
# 使用 PyRIT 进行多轮攻击
python -c "from pyrit.orchestrator import CrescendoOrchestrator; ..."

# 使用各模块自定义脚本进行深度利用
python module-2-llm-vulnerability-exploitation.py
python module-3-rag-pipeline-exploitation.py
python module-4-multi-agent-mcp-exploitation.py
```

#### Phase 4: 报告撰写（第 20-24 小时 + 额外 24 小时）

```
报告内容：
├── 执行摘要
├── 攻击面分析
├── 漏洞发现（按严重程度排序）
├── 漏洞详情（每个漏洞包含：描述、影响、复现步骤、证据、修复建议）
├── 攻击链分析
├── 结论与建议
└── 附录
```

---

### 5.3 工具安装命令

```bash
# promptfoo
npm install -g promptfoo

# PyRIT
pip install pyrit

# Garak
pip install garak

# DeepTeam
pip install deepteam

# Burp Suite
# 官网下载：https://portswigger.net/burp

# Python 依赖
pip install requests numpy urllib3 concurrent-futures
```

---

### 5.4 核心攻击链闭环演练

```
1. 利用 garak 扫出漏洞
2. 触发 AI 工具调用执行代码
3. 拿到 K8s 内部低权限 Pod
4. 使用 TruffleHog / CDK 收集凭证
5. 发现未授权 Ray 集群
6. 提交恶意 Job 拿下 GPU 宿主机最高权限（RCE）
```

---

## 考试使用说明

### 修改要点

1. **目标地址**：修改 `main()` 函数中的 `targets` 列表为考试环境的IP地址
2. **端口范围**：根据考试环境调整 `ai_port_map` 中的端口列表
3. **API密钥**：如果目标需要认证，在扫描器初始化时提供有效的API密钥
4. **超时设置**：根据网络延迟调整 `timeout` 参数（建议3-5秒）

### 典型工作流

```bash
# 1. 扫描内网AI服务
python module-1-ai-asset-reconnaissance.py

# 2. 根据扫描结果，对发现的服务进行指纹识别
# 3. 探测上下文长度和嵌入模型类型
# 4. 记录所有发现的AI资产到攻击笔记
```

### 关键发现指标

- **未授权访问**：HTTP状态码200且无需有效API密钥
- **模型暴露**：`/v1/models` 端点返回模型列表
- **向量数据库**：`/api/v1/collections` 或 `/collections` 端点可访问
- **上下文长度**：决定攻击payload的最大长度
- **嵌入维度**：决定RAG投毒攻击的向量格式

---

> **文档版本**: v1.0  
> **适用模块**: AI-300 模块一：AI 资产探测与指纹识别  
> **考试重要性**: ⭐⭐⭐⭐⭐
"""BIG-IP 工具函数模块"""
import os
import re

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "bigip.conf")


def get_virtual_info(virtual_name: str = "") -> str:
    """读取 BIG-IP Virtual Server 的信息。"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    virtual_pattern = r'ltm virtual /Common/([^\s]+)\s*\{([^}]+)\}'
    virtuals = re.findall(virtual_pattern, content, re.DOTALL)
    
    results = []
    for name, config in virtuals:
        if virtual_name and virtual_name not in name:
            continue
        
        info = {"name": name}
        
        destination_match = re.search(r'destination /Common/([^\s]+)', config)
        if destination_match:
            info["destination"] = destination_match.group(1)
        
        pool_match = re.search(r'pool /Common/([^\s]+)', config)
        if pool_match:
            info["pool"] = pool_match.group(1)
        
        profiles_match = re.search(r'profiles \{\s*([^}]+)\s*\}', config, re.DOTALL)
        if profiles_match:
            profiles = re.findall(r'/Common/([^\s]+)', profiles_match.group(1))
            info["profiles"] = profiles
        
        snat_match = re.search(r'source-address-translation \{\s*([^}]+)\s*\}', config, re.DOTALL)
        if snat_match:
            snat_type = re.search(r'type (\w+)', snat_match.group(1))
            snat_pool = re.search(r'pool /Common/([^\s]+)', snat_match.group(1))
            info["source-address-translation"] = {
                "type": snat_type.group(1) if snat_type else None,
                "pool": snat_pool.group(1) if snat_pool else None,
            }
        
        results.append(info)
    
    if not results:
        return f"未找到 Virtual Server: {virtual_name}" if virtual_name else "未找到任何 Virtual Server"
    
    return _format_results(results)


def get_pool_info(pool_name: str = "") -> str:
    """读取 BIG-IP Pool 的信息。"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pool_pattern = r'ltm pool /Common/([^\s]+)\s*\{([^}]+)\}'
    pools = re.findall(pool_pattern, content, re.DOTALL)
    
    results = []
    for name, config in pools:
        if pool_name and pool_name not in name:
            continue
        
        info = {"name": name}
        
        monitor_match = re.search(r'monitor /Common/([^\s]+)', config)
        if monitor_match:
            info["monitor"] = monitor_match.group(1)
        
        members_match = re.search(r'members \{\s*([^}]+)\s*\}', config, re.DOTALL)
        if members_match:
            member_pattern = r'/Common/([^\s]+):(\d+)'
            members = re.findall(member_pattern, members_match.group(1))
            info["members"] = [{"address": m[0], "port": m[1]} for m in members]
        
        results.append(info)
    
    if not results:
        return f"未找到 Pool: {pool_name}" if pool_name else "未找到任何 Pool"
    
    return _format_results(results)


def get_snatpool_info(snatpool_name: str = "") -> str:
    """读取 BIG-IP SNAT Pool 的信息。"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    snatpool_pattern = r'ltm snatpool /Common/([^\s]+)\s*\{([^}]+)\}'
    snatpools = re.findall(snatpool_pattern, content, re.DOTALL)
    
    results = []
    for name, config in snatpools:
        if snatpool_name and snatpool_name not in name:
            continue
        
        info = {"name": name}
        
        members_match = re.search(r'members \{\s*([^}]+)\s*\}', config, re.DOTALL)
        if members_match:
            members = re.findall(r'/Common/([^\s]+)', members_match.group(1))
            info["members"] = members
        
        results.append(info)
    
    if not results:
        return f"未找到 SNAT Pool: {snatpool_name}" if snatpool_name else "未找到任何 SNAT Pool"
    
    return _format_results(results)


def get_profile_info(profile_name: str = "") -> str:
    """读取 BIG-IP Profile 的信息。"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    profile_pattern = r'ltm profile (\w+) /Common/([^\s]+)\s*\{([^}]+)\}'
    profiles = re.findall(profile_pattern, content, re.DOTALL)
    
    results = []
    for profile_type, name, config in profiles:
        if profile_name and profile_name not in name:
            continue
        
        info = {"name": name, "type": profile_type}
        
        defaults_match = re.search(r'defaults-from /Common/([^\s]+)', config)
        if defaults_match:
            info["defaults-from"] = defaults_match.group(1)
        
        # 解析 cert-key-chain (支持嵌套结构)
        cert_key_chain_match = re.search(r'cert-key-chain \{\s*([\s\S]*?)\s*\}', config)
        if cert_key_chain_match:
            cert_chain_content = cert_key_chain_match.group(1)
            
            # 提取每个证书链块
            chain_blocks = re.findall(r'(\w+)\s*\{([^}]+)\}', cert_chain_content)
            cert_chains = []
            for chain_name, chain_config in chain_blocks:
                cert_info = {"name": chain_name}
                
                cert_match = re.search(r'cert /Common/([^\s]+)', chain_config)
                key_match = re.search(r'key /Common/([^\s]+)', chain_config)
                chain_match = re.search(r'chain /Common/([^\s]+)', chain_config)
                
                if cert_match:
                    cert_info["cert"] = cert_match.group(1)
                if key_match:
                    cert_info["key"] = key_match.group(1)
                if chain_match:
                    cert_info["chain"] = chain_match.group(1)
                
                cert_chains.append(cert_info)
            
            if cert_chains:
                info["cert-key-chain"] = cert_chains
        
        results.append(info)
    
    if not results:
        return f"未找到 Profile: {profile_name}" if profile_name else "未找到任何 Profile"
    
    return _format_results(results)


def _format_results(results: list) -> str:
    """格式化输出结果，每个 name 一行，其他属性缩进显示。"""
    lines = []
    for item in results:
        name = item.pop("name", "")
        lines.append(f"- {name}")
        for key, value in item.items():
            lines.append(f"  {key}: {_format_value(value)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _format_value(value) -> str:
    """递归格式化值，处理列表和字典。"""
    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            items.append(f"{k}={v}")
        return "{" + ", ".join(items) + "}"
    elif isinstance(value, list):
        if value and isinstance(value[0], dict):
            # 处理 cert-key-chain 等嵌套列表
            lines = []
            for item in value:
                inner = ", ".join(f"{k}={v}" for k, v in item.items())
                lines.append(f"{{ {inner} }}")
            return "\n    ".join(lines)
        return ", ".join(str(v) for v in value)
    else:
        return str(value)

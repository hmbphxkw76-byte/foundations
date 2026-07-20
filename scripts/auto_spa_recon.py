#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-300 通用 SPA 聊天侦察脚本（v2.0）

基于国开 syxy 实战经验提炼的通用诊断工具，适配任何「SPA + SSO/OIDC + 浮动聊天入口」目标。

支持三种使用方式：
  1. 命令行参数：   python scripts/auto_spa_recon.py --url https://xxx.com --user admin --pass pwd
  2. YAML 配置：    python scripts/auto_spa_recon.py --config config/targets/sso_login.yaml
  3. 交互式：       python scripts/auto_spa_recon.py （依次提示输入）

10 步全自动流程：
  1. 启动 Chromium（非 headless）
  2. 导航到目标 → 自动跳转 SSO 登录页
  3. 自动填入用户名/密码 → 自动点击登录
  4. 弹出验证码 → 等待用户手动完成（180s 超时）
  5. 登录成功后自动检测落地（排除 OIDC 回调中间页）
  6. 检查 localStorage / Cookie（OIDC token 识别）
  7. 全屏扫描页面，找 AI 聊天入口（浮动按钮/侧边栏/菜单项）
  8. 点击聊天入口 → 等待聊天面板渲染
  9. 找输入框 → 输入"你好" → 三级降级发送（Enter/按钮/父容器点击）
  10. 抓取 API 请求（LLM 端点）+ AI 响应文本 + storage_state + 诊断报告

实战验证目标（2026-07-19）：
  - 国开 syxy: deepseek-r1-250120 (volcengine) + RAG 知识库
  - LLM 端点: POST https://appsharing-ai.ouchn.edu.cn/v0/chat/completions/with-knowledge

用法示例:
    cd d:\\我的文档\\GitHub\\osai\\pyrit

    # 方式 1: 命令行参数
    python scripts/auto_spa_recon.py --url https://student.syxy.ouchn.cn/#/home \\
        --user 2680201200754 --pass PASSWORD

    # 方式 2: YAML 配置（推荐，复用 sso_login.yaml）
    python scripts/auto_spa_recon.py --config config/targets/sso_login.yaml

    # 方式 3: 交互式（不带参数时依次提示）
    python scripts/auto_spa_recon.py
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from urllib.parse import urlparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "results", "recon", "screenshots")
STATE_DIR = os.path.join(PROJECT_ROOT, "results", "recon", "storage_states")
REPORT_DIR = os.path.join(PROJECT_ROOT, "results", "recon")

# ═══ 通用选择器池（从 adapter DEFAULT_CHAT_ENTRY_SELECTORS 提炼） ═══
# 按优先级排列：精确 class > 模糊 class > placeholder > 通用
CHAT_INPUT_SELECTORS = [
    "textarea.send-box-default-text",
    "textarea[class*='send-box']",
    "[placeholder='请输入文字或语音']",
    "textarea[class*='chat-input']",
    "textarea[class*='message']",
    "textarea[class*='prompt']",
    "[contenteditable='true'][class*='chat']",
    "textarea",
]

# 聊天入口候选关键词（用于评分）
CHAT_ENTRY_KEYWORDS = [
    'chat', 'ai', '助手', '智能', '聊天', '对话', '问答', '客服',
    'robot', 'bot', 'assistant', 'copilot', 'genie', 'sparkle',
]

# 聊天入口选择器（当评分扫描未命中时的兜底）
CHAT_ENTRY_FALLBACK_SELECTORS = [
    ".show-chat-button", ".show-chat", ".show-chat-btn",
    ".open-chat", ".open-chat-button", ".toggle-chat",
    ".chat-fab", ".chat-widget", ".chat-trigger", ".chat-launcher",
    ".ai-assistant", ".ai-chat-btn", ".ai-trigger",
    ".floating-btn", ".fab", ".fab-btn",
    "[class*='show-chat']", "[class*='open-chat']",
    "[class*='chat-fab']", "[class*='ai-fab']",
    "[aria-label*='助手']", "[aria-label*='聊天']",
    "[aria-label*='AI']", "[aria-label*='Chat']",
    "[title*='助手']", "[title*='聊天']",
]

# LLM API 路径关键词（用于过滤网络请求）
LLM_API_KEYWORDS = [
    "/api/", "/v0/", "/v1/", "/v2/",
    "chat", "completion", "llm", "stream", "message",
    "ask", "query", "generate", "infer",
    "with-knowledge", "rag", "knowledge",
]

# 静态资源后缀（过滤）
STATIC_EXTS = (
    ".js", ".css", ".png", ".jpg", ".svg", ".woff", ".woff2",
    ".ico", ".gif", ".ttf", ".map", ".mp4", ".webp",
)

# OIDC 回调特征（用于排除登录中间页）
OIDC_CALLBACK_PATTERNS = [
    "signin-oidc", "redirect_uri", "callback",
    "code=", "id_token=", "access_token=",
]


def load_config_from_yaml(yaml_path: str) -> dict:
    """从 sso_login.yaml 读取配置"""
    try:
        import yaml
    except ImportError:
        print("⚠️ 需要 PyYAML：pip install pyyaml")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    target = cfg.get("target", {})
    conn = target.get("connection", {})
    login = target.get("login", {})

    url = conn.get("url", "")
    parsed = urlparse(url)
    target_domain = parsed.hostname or ""

    # 尝试从 credentials 文件读取凭据
    cred_file = login.get("credential_file", "")
    if cred_file and os.path.isabs(cred_file):
        cred_path = cred_file
    else:
        cred_path = os.path.join(PROJECT_ROOT, cred_file) if cred_file else ""

    username, password = "", ""
    if cred_path and os.path.exists(cred_path):
        with open(cred_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if ":" in line and not line.startswith("http"):
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        username, password = parts[0].strip(), parts[1].strip()
                        break

    # SSO 域名（从 login 配置推断）
    sso_domain = ""
    sso_cfg = login.get("sso", {})
    if sso_cfg:
        sso_url = sso_cfg.get("login_url", "")
        if sso_url:
            sso_domain = urlparse(sso_url).hostname or ""

    return {
        "url": url,
        "username": username,
        "password": password,
        "target_domain": target_domain,
        "sso_domain": sso_domain,
    }


def prompt_input(prompt: str, default: str = "") -> str:
    """交互式输入（带默认值）"""
    if default:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    return input(f"{prompt}: ").strip()


async def main():
    parser = argparse.ArgumentParser(
        description="AI-300 通用 SPA 聊天侦察脚本 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--url", help="目标 URL（如 https://xxx.com/#/home）")
    parser.add_argument("--user", help="登录用户名/学号")
    parser.add_argument("--pass", dest="password", help="登录密码")
    parser.add_argument("--config", help="YAML 配置文件路径（如 config/targets/sso_login.yaml）")
    parser.add_argument("--headless", action="store_true", help="无头模式（不推荐，验证码需人工）")
    parser.add_argument("--message", default="你好", help="探测消息内容（默认: 你好）")
    args = parser.parse_args()

    # ── 加载配置 ──
    if args.config:
        cfg = load_config_from_yaml(args.config)
        target_url = args.url or cfg["url"]
        username = args.user or cfg["username"]
        password = args.password or cfg["password"]
        target_domain = cfg["target_domain"]
        sso_domain = cfg["sso_domain"]
    elif args.url:
        target_url = args.url
        username = args.user or ""
        password = args.password or ""
        parsed = urlparse(target_url)
        target_domain = parsed.hostname or ""
        sso_domain = ""
    else:
        # 交互式
        print("=" * 60)
        print("  AI-300 通用 SPA 聊天侦察（交互模式）")
        print("=" * 60)
        target_url = prompt_input("目标 URL")
        username = prompt_input("用户名/学号")
        password = prompt_input("密码")
        parsed = urlparse(target_url)
        target_domain = parsed.hostname or ""
        sso_domain = ""

    if not target_url:
        print("❌ 必须提供目标 URL")
        sys.exit(1)

    if not target_domain:
        print(f"❌ 无法从 URL 解析域名: {target_url}")
        sys.exit(1)

    # 如果未提供 sso_domain，用通用关键词匹配
    if not sso_domain:
        sso_domain = "passport"  # 通用 SSO 子域名关键词

    for d in [SCREENSHOT_DIR, STATE_DIR, REPORT_DIR]:
        os.makedirs(d, exist_ok=True)

    ts = str(int(time.time()))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 60)
    print("  AI-300 通用 SPA 聊天侦察 v2.0")
    print("=" * 60)
    print(f"  目标: {target_url}")
    print(f"  域名: {target_domain}")
    print(f"  SSO:  {sso_domain}")
    print(f"  账号: {username or '(未提供，需手动登录)'}")
    print(f"  时间: {now}")
    print()

    # API 请求记录
    api_calls = []
    llm_api_calls = []

    async def on_response(response):
        url = response.url
        if url.split("?")[0].endswith(STATIC_EXTS):
            return

        try:
            status = response.status
            method = response.request.method
            content_type = response.headers.get("content-type", "")

            is_api = any(k in url.lower() for k in LLM_API_KEYWORDS)
            if is_api or "json" in content_type or "event-stream" in content_type:
                body_preview = ""
                if "json" in content_type or "text" in content_type or "event-stream" in content_type:
                    try:
                        body_preview = (await response.text())[:500]
                    except Exception:
                        pass

                call = {
                    "url": url[:200],
                    "method": method,
                    "status": status,
                    "content_type": content_type,
                    "body_preview": body_preview,
                    "timestamp": time.time(),
                }
                api_calls.append(call)

                if is_api:
                    llm_api_calls.append(call)
                    print(f"    🔑 [LLM API] {method} {status} {url[:80]}")
                    if body_preview:
                        print(f"       body: {body_preview[:120]}")
        except Exception:
            pass

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        # ── 1. 启动浏览器 ──
        print("[1/10] 启动 Chromium ...")
        browser = await p.chromium.launch(headless=args.headless)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            ignore_https_errors=True,
        )
        page = await context.new_page()
        page.on("response", on_response)

        # ── 2. 导航到目标页面 ──
        print(f"\n[2/10] 导航到 {target_url} ...")
        try:
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
        except Exception:
            pass  # SSO 重定向会导致超时，正常

        await page.wait_for_timeout(3000)
        current_url = page.url
        print(f"  当前 URL: {current_url[:100]}")

        # ── 3. SSO 登录页自动填表 ──
        url_lower = current_url.lower()
        is_login_page = any(k in url_lower for k in [
            "passport", "login", "signin", "account/login", "auth",
        ]) and not any(p in url_lower for p in OIDC_CALLBACK_PATTERNS)

        if is_login_page and username:
            print("\n[3/10] 检测到 SSO 登录页，自动填写表单 ...")
            print(f"  URL: {current_url[:100]}")

            username_selectors = [
                "input[name='username']", "input[name='account']",
                "input[name='userName']", "#username", "#account",
                "input[type='text'][placeholder*='账号']",
                "input[type='text'][placeholder*='用户']",
                "input[type='text'][placeholder*='学号']",
                "input[type='text'][placeholder*='手机']",
                "input[type='text']",
            ]
            password_selectors = [
                "input[name='password']", "input[name='passwd']",
                "#password", "input[type='password']",
            ]
            submit_selectors = [
                "button[type='submit']", "input[type='submit']",
                "button.login-btn", ".submit-btn",
                "button:has-text('登录')", "button:has-text('Login')",
                "a:has-text('登录')", "button:has-text('Sign')",
            ]

            # 填用户名
            for sel in username_selectors:
                try:
                    el = await page.wait_for_selector(sel, state="visible", timeout=3000)
                    if el:
                        await el.click()
                        await el.fill("")
                        await page.type(sel, username, delay=30)
                        print(f"  ✅ 用户名已填入 ({sel})")
                        break
                except Exception:
                    continue
            else:
                print("  ⚠️ 未找到用户名输入框，请手动填写")

            # 填密码
            for sel in password_selectors:
                try:
                    el = await page.wait_for_selector(sel, state="visible", timeout=3000)
                    if el:
                        await el.click()
                        await el.fill("")
                        await page.type(sel, password, delay=30)
                        print(f"  ✅ 密码已填入 ({sel})")
                        break
                except Exception:
                    continue
            else:
                print("  ⚠️ 未找到密码输入框，请手动填写")

            # 点击登录
            await page.wait_for_timeout(1000)
            for sel in submit_selectors:
                try:
                    el = await page.wait_for_selector(sel, state="visible", timeout=2000)
                    if el:
                        await el.click()
                        print(f"  ✅ 已点击登录按钮 ({sel})")
                        break
                except Exception:
                    continue
            else:
                print("  ⚠️ 未找到登录按钮，请手动点击登录")

            # ── 4. 等待验证码（人工完成）──
            print("\n[4/10] 等待人工完成验证码 ...")
            print("  " + "=" * 56)
            print("  🔐 如果弹出滑窗/图形验证码，请在浏览器中手动完成")
            print("  完成后页面会自动跳转，脚本检测到落地后继续")
            print("  " + "=" * 56)

            landed = False
            for i in range(180):
                await page.wait_for_timeout(1000)
                cur = page.url.lower()

                is_oidc_callback = any(p in cur for p in OIDC_CALLBACK_PATTERNS)

                if target_domain in cur and not is_oidc_callback:
                    print(f"\n  ✅ 已落地到目标域名: {page.url[:80]}")
                    landed = True
                    break

                if i % 10 == 0 and i > 0:
                    print(f"  ⏳ 等待中 ({i}s)... 当前: {page.url[:60]}")

            if not landed:
                print(f"\n  ⚠️ 180 秒未检测到落地，当前 URL: {page.url[:80]}")
                print("  请确认登录是否完成，按 Enter 继续...")
                input()

            await page.wait_for_timeout(3000)
        elif is_login_page and not username:
            print("\n[3/10] 检测到登录页但未提供凭据，请手动登录 ...")
            print("  登录完成后按 Enter 继续 ...")
            input()
            await page.wait_for_timeout(3000)
        else:
            print("\n[3/10] 未检测到登录页，可能已登录")

        # 截图（登录后）
        screenshot_login = os.path.join(SCREENSHOT_DIR, f"auto_login_{ts}.png")
        await page.screenshot(path=screenshot_login, full_page=True)
        print(f"\n  📸 登录后截图: {screenshot_login}")

        # ── 5. 检查 localStorage（OIDC token）──
        print("\n[5/10] 检查认证状态 ...")
        local_storage = await page.evaluate("""() => {
            const items = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                items[key] = localStorage.getItem(key);
            }
            return items;
        }""")

        has_token = False
        if local_storage:
            print(f"  localStorage ({len(local_storage)} 项):")
            for key, value in local_storage.items():
                preview = value[:100]
                is_token = any(t in key.lower() for t in [
                    "token", "access", "id_token", "bearer", "auth", "user",
                ])
                if is_token:
                    has_token = True
                    print(f"    🔑 {key}: {preview}")
                else:
                    print(f"    {key}: {preview}")
        else:
            print("  ⚠️ localStorage 为空")

        cookies = await context.cookies()
        print(f"  Cookie: {len(cookies)} 个")

        if not has_token:
            print("  ⚠️ 未发现 OIDC token，认证可能未完成")

        # ── 6. 全屏扫描页面，找 AI 聊天入口 ──
        print("\n[6/10] 扫描页面，查找 AI 聊天入口 ...")
        current_url = page.url
        print(f"  当前 URL: {current_url[:80]}")
        print(f"  页面标题: {await page.title()}")

        # 先检查当前页面是否已有聊天元素
        chat_check = await page.evaluate("""() => {
            const sels = [
                'textarea.send-box-default-text', 'textarea[class*="send-box"]',
                'textarea[class*="chat-input"]', 'textarea[class*="message"]',
                '[placeholder*="请输入"]', '[placeholder*="输入"]',
                'textarea[class*="chat"]', 'textarea[class*="prompt"]'
            ];
            for (const sel of sels) {
                const el = document.querySelector(sel);
                if (el) return { hasChatInput: true, selector: sel, class: el.className };
            }
            return { hasChatInput: false };
        }""")

        if chat_check["hasChatInput"]:
            print(f"  ✅ 当前页面已有聊天输入框: {chat_check.get('class', '')}")
        else:
            print("  当前页面无聊天输入框，扫描聊天入口按钮 ...")

            # 扫描可能的聊天入口
            entry_candidates = await page.evaluate("""(keywords) => {
                const candidates = [];
                const elements = document.querySelectorAll(
                    'button, a, [role="button"], [onclick], img[class*="action"], ' +
                    '[class*="chat"], [class*="ai"], [class*="assistant"], ' +
                    '[class*="robot"], [class*="help"], [class*="show-chat"], ' +
                    '[class*="open-chat"], [class*="toggle-chat"]'
                );

                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;

                    const text = (el.innerText || '').trim();
                    const className = el.className || '';
                    const ariaLabel = el.getAttribute('aria-label') || '';
                    const title = el.getAttribute('title') || '';
                    const alt = el.getAttribute('alt') || '';

                    const combined = (className + ' ' + text + ' ' + ariaLabel + ' ' + title + ' ' + alt).toLowerCase();

                    let score = 0;
                    const signals = [];
                    for (const kw of keywords) {
                        if (combined.includes(kw)) {
                            score += 10;
                            signals.push(kw);
                        }
                    }

                    // 浮动按钮加分（位置在右下角且尺寸小）
                    if (rect.x > window.innerWidth * 0.7 && rect.y > window.innerHeight * 0.5
                        && rect.width < 100 && rect.height < 100) {
                        score += 5;
                        signals.push('fab-position');
                    }

                    if (score > 0) {
                        let selector = '';
                        if (el.id) selector = '#' + el.id;
                        else if (el.getAttribute('data-testid')) selector = '[data-testid="' + el.getAttribute('data-testid') + '"]';
                        else if (ariaLabel) selector = '[aria-label="' + ariaLabel + '"]';
                        else if (className && typeof className === 'string') {
                            const cls = className.split(' ')[0];
                            selector = el.tagName.toLowerCase() + '.' + cls;
                        } else {
                            selector = el.tagName.toLowerCase();
                        }

                        candidates.push({
                            tag: el.tagName.toLowerCase(),
                            selector: selector,
                            class: (typeof className === 'string' ? className : '').substring(0, 80),
                            text: text.substring(0, 30),
                            ariaLabel: ariaLabel,
                            alt: alt,
                            score: score,
                            signals: signals,
                            rect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) },
                        });
                    }
                }

                candidates.sort((a, b) => b.score - a.score);
                return candidates.slice(0, 15);
            }""", CHAT_ENTRY_KEYWORDS)

            if entry_candidates:
                print(f"\n  发现 {len(entry_candidates)} 个聊天入口候选:")
                for i, c in enumerate(entry_candidates):
                    print(f"    [{i}] score:{c['score']} {c['selector']} signals:[{','.join(c['signals'])}]"
                          f" text:'{c['text']}' pos({c['rect']['x']},{c['rect']['y']})")

                # 尝试点击最高分的入口
                print("\n  尝试点击聊天入口 ...")
                for candidate in entry_candidates[:5]:
                    try:
                        sel = candidate["selector"]
                        print(f"  → 尝试点击: {sel}")
                        await page.click(sel, timeout=5000)
                        await page.wait_for_timeout(3000)

                        post_click = await page.evaluate("""() => {
                            const sels = [
                                'textarea.send-box-default-text', 'textarea[class*="send-box"]',
                                'textarea[class*="chat-input"]', 'textarea[class*="chat"]',
                                '[placeholder*="请输入"]'
                            ];
                            for (const sel of sels) {
                                const el = document.querySelector(sel);
                                if (el) return el.className;
                            }
                            return null;
                        }""")

                        if post_click:
                            print(f"  ✅ 点击成功！聊天输入框出现: {post_click}")
                            chat_check["hasChatInput"] = True
                            break
                        else:
                            print(f"  ℹ️ 点击后未出现聊天输入框，尝试下一个")
                    except Exception as e:
                        print(f"  ⚠️ 点击失败: {str(e)[:60]}")
                        continue

                # 如果评分扫描未命中，尝试兜底选择器
                if not chat_check["hasChatInput"]:
                    print("\n  评分扫描未命中，尝试兜底选择器 ...")
                    for sel in CHAT_ENTRY_FALLBACK_SELECTORS:
                        try:
                            el = await page.query_selector(sel)
                            if el:
                                await el.click()
                                await page.wait_for_timeout(3000)
                                post = await page.evaluate("""() => {
                                    const sels = ['textarea.send-box-default-text', 'textarea[class*="send-box"]', 'textarea[class*="chat"]'];
                                    for (const s of sels) { const e = document.querySelector(s); if (e) return e.className; }
                                    return null;
                                }""")
                                if post:
                                    print(f"  ✅ 兜底选择器命中: {sel} → {post}")
                                    chat_check["hasChatInput"] = True
                                    break
                        except Exception:
                            continue

                screenshot_entry = os.path.join(SCREENSHOT_DIR, f"auto_entry_{ts}.png")
                await page.screenshot(path=screenshot_entry, full_page=True)
                print(f"\n  📸 入口点击后截图: {screenshot_entry}")
            else:
                print("  ❌ 未找到任何聊天入口候选")
                print("  可能原因：")
                print("    1. 聊天入口需要从特定菜单进入")
                print("    2. 聊天入口图标用 Canvas/SVG 渲染（无文本）")
                print("    3. 需要先点击某个导航项才显示聊天入口")

        # ── 7. 找输入框并输入消息 ──
        print("\n[7/10] 查找聊天输入框并输入消息 ...")

        input_found = False
        input_sel_used = ""
        for sel in CHAT_INPUT_SELECTORS:
            try:
                el = await page.wait_for_selector(sel, state="visible", timeout=5000)
                if el:
                    print(f"  ✅ 找到输入框: {sel}")
                    input_found = True
                    input_sel_used = sel
                    break
            except Exception:
                continue

        if not input_found:
            print("  ❌ 未找到聊天输入框")
            print("  请在浏览器中手动打开聊天界面，然后按 Enter ...")
            input()
            for sel in CHAT_INPUT_SELECTORS:
                try:
                    el = await page.wait_for_selector(sel, state="visible", timeout=5000)
                    if el:
                        print(f"  ✅ 找到输入框: {sel}")
                        input_found = True
                        input_sel_used = sel
                        break
                except Exception:
                    continue

        if input_found:
            test_message = args.message
            await page.click(input_sel_used)
            await page.fill(input_sel_used, "")
            await page.type(input_sel_used, test_message, delay=50)
            print(f"  ✅ 已输入: '{test_message}'")

            screenshot_input = os.path.join(SCREENSHOT_DIR, f"auto_input_{ts}.png")
            await page.screenshot(path=screenshot_input)
            print(f"  📸 输入后截图: {screenshot_input}")

            # ── 8. 发送消息（三级降级）──
            print(f"\n[8/10] 发送消息 ...")
            api_count_before = len(llm_api_calls)

            # 策略 1: Enter 键
            print("  → 尝试 Enter 键发送 ...")
            await page.press(input_sel_used, "Enter")
            await page.wait_for_timeout(5000)

            new_api = len(llm_api_calls) - api_count_before
            if new_api == 0:
                # 策略 2: 查找发送按钮
                print("  → Enter 未触发 API，尝试查找发送按钮 ...")
                send_btn_selectors = [
                    "button[class*='send']", "button[class*='submit']",
                    "[class*='send-btn']", "[class*='submit-btn']",
                    "button[aria-label*='发送']", "button[aria-label*='Send']",
                    "button:has-text('发送')", "button:has-text('Send')",
                ]
                for sel in send_btn_selectors:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            await el.click()
                            print(f"  → 点击发送按钮: {sel}")
                            await page.wait_for_timeout(5000)
                            new_api = len(llm_api_calls) - api_count_before
                            if new_api > 0:
                                break
                    except Exception:
                        continue

            if new_api == 0:
                # 策略 3: 点击父容器
                print("  → 尝试点击父容器 ...")
                await page.evaluate("""(inputSel) => {
                    const input = document.querySelector(inputSel);
                    if (input) {
                        let node = input;
                        for (let i = 0; i < 5 && node.parentElement; i++) {
                            node = node.parentElement;
                            if (getComputedStyle(node).cursor === 'pointer') {
                                node.click();
                                return true;
                            }
                        }
                    }
                    return false;
                }""", input_sel_used)
                await page.wait_for_timeout(5000)
                new_api = len(llm_api_calls) - api_count_before

            if new_api > 0:
                print(f"\n  ✅ 发送成功！新增 {new_api} 个 LLM API 请求:")
                for call in llm_api_calls[api_count_before:]:
                    print(f"     {call['method']} {call['status']} {call['url'][:100]}")
                    if call['body_preview']:
                        print(f"       响应: {call['body_preview'][:150]}")
            else:
                print("  ❌ 发送后未检测到 API 请求")

            screenshot_send = os.path.join(SCREENSHOT_DIR, f"auto_send_{ts}.png")
            await page.screenshot(path=screenshot_send)
            print(f"  📸 发送后截图: {screenshot_send}")

            # ── 9. 获取 AI 响应 ──
            print(f"\n[9/10] 等待 AI 响应 ...")
            await page.wait_for_timeout(5000)

            response_info = await page.evaluate("""() => {
                const selectors = [
                    '[class*="answer"]', '[class*="response"]',
                    '[class*="message"]', '[class*="markdown"]',
                    '[class*="prose"]', '[class*="chat-content"]',
                    '[class*="ai-msg"]', '[class*="assistant"]',
                    '[class*="reply"]', '[class*="bot-msg"]'
                ];
                const results = [];
                for (const sel of selectors) {
                    const els = document.querySelectorAll(sel);
                    for (const el of els) {
                        const text = (el.innerText || '').trim();
                        if (text.length > 10) {
                            results.push({
                                selector: sel,
                                class: el.className.substring(0, 80),
                                text: text.substring(0, 300),
                            });
                        }
                    }
                }
                return results;
            }""")

            if response_info:
                print(f"  ✅ 发现 {len(response_info)} 个响应容器:")
                for r in response_info[:3]:
                    print(f"     {r['selector']} → class='{r['class'][:40]}'")
                    print(f"     内容: {r['text'][:100]}...")
            else:
                print("  ❌ 未找到响应文本")

            # ── 10. 保存结果 ──
            print(f"\n[10/10] 保存结果 ...")

            state_path = os.path.join(STATE_DIR, f"auto_state_{ts}.json")
            await context.storage_state(path=state_path)
            print(f"  💾 storage_state: {state_path}")

            report = {
                "timestamp": now,
                "target": target_url,
                "target_domain": target_domain,
                "username": username,
                "current_url": page.url,
                "local_storage": local_storage,
                "cookies_count": len(cookies),
                "has_oidc_token": has_token,
                "chat_input_found": input_found,
                "input_selector": input_sel_used,
                "llm_api_calls": llm_api_calls,
                "all_api_calls_count": len(api_calls),
                "response_containers": response_info,
                "screenshots": {
                    "login": screenshot_login,
                    "entry": screenshot_entry if 'screenshot_entry' in dir() else "",
                    "input": screenshot_input,
                    "send": screenshot_send,
                },
            }
            report_path = os.path.join(REPORT_DIR, f"auto_report_{ts}.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"  📋 诊断报告: {report_path}")

            # 总结
            print("\n" + "=" * 60)
            print("  📊 侦察总结")
            print("=" * 60)
            print(f"  认证状态: {'✅ 有 OIDC token' if has_token else '⚠️ 无 token'}")
            print(f"  聊天输入框: {'✅ 找到' if input_found else '❌ 未找到'}")
            print(f"  LLM API 请求: {len(llm_api_calls)} 个")
            print(f"  AI 响应: {'✅ 获取到' if response_info else '❌ 未获取'}")
            if llm_api_calls:
                print(f"\n  🔑 LLM 端点:")
                for call in llm_api_calls:
                    print(f"     {call['method']} {call['url'][:100]}")
            print()
        else:
            print("\n  ❌ 仍未找到聊天输入框，无法继续")
            state_path = os.path.join(STATE_DIR, f"auto_state_{ts}.json")
            await context.storage_state(path=state_path)
            print(f"  💾 storage_state 已保存: {state_path}")

        print("\n  浏览器保持打开，可手动检查。")
        print("  按 Enter 关闭浏览器 ...")
        input()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

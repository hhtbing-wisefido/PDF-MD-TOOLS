# pip install Rules

Rule Type: MANDATORY
Enforcement Level: STRICT

---

## Core Rules

When pip install is slow or no response:

MUST execute immediately (do not wait more than 30 seconds):

1. Use SOCKS5 proxy first:
   pip install --proxy socks5://127.0.0.1:4000 PACKAGE_NAME

2. Fallback: Use Tsinghua mirror:
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple PACKAGE_NAME

---

## China Mirror List

Tsinghua: https://pypi.tuna.tsinghua.edu.cn/simple
Aliyun: https://mirrors.aliyun.com/pypi/simple
Tencent: https://mirrors.cloud.tencent.com/pypi/simple
Huawei: https://repo.huaweicloud.com/repository/pypi/simple

---

## AI Requirements

1. If pip hangs more than 30s, switch to proxy/mirror immediately
2. Do NOT wait, do NOT ask user, just switch
3. Priority: SOCKS5 proxy > Tsinghua mirror > Others

---

## AI Self-Check Before Running pip install

BEFORE executing pip install, AI must check:
- Did I use --proxy socks5://127.0.0.1:4000 ?
- Or did I use -i https://pypi.tuna.tsinghua.edu.cn/simple ?
- If NEITHER, STOP and fix the command NOW!

FORBIDDEN:
- Direct pip install PACKAGE without proxy/mirror
- Wait more than 30 seconds without switching
- Ask user whether to switch source

---

AI must execute proactively, do not wait for user instruction!

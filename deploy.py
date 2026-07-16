#!/usr/bin/env python3
"""
摄影资料库 — GitHub Pages 一键部署脚本

用法:
  GITHUB_TOKEN=xxx python3 deploy.py                    # 部署所有文件
  GITHUB_TOKEN=xxx python3 deploy.py photography.html   # 只部署主页面
"""
import json, base64, urllib.request, urllib.error, sys, os

TOKEN = os.environ.get('GITHUB_TOKEN', '')
if not TOKEN:
    print('❌ 请设置环境变量: export GITHUB_TOKEN=你的token')
    sys.exit(1)

OWNER = 'poetzhangruoshi-lgtm'
REPO  = 'photography-ref'
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Python',
}

FILE_MAP = {
    'photography.html': 'index.html',
    'transition-techniques.html': 'transition-techniques.html',
    'data.js': 'data.js',
}

def deploy_file(local_name, remote_name):
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), local_name)
    if not os.path.exists(local_path):
        print(f'  ✗ 文件不存在: {local_path}')
        return False

    api_url = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{remote_name}'
    sha = None
    try:
        req = urllib.request.Request(api_url, headers=HEADERS)
        resp = urllib.request.urlopen(req)
        sha = json.loads(resp.read())['sha']
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f'  ✗ 获取SHA失败: {e.code}')
            return False

    with open(local_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode()

    payload = {'message': f'更新 {remote_name}', 'content': content}
    if sha:
        payload['sha'] = sha

    req = urllib.request.Request(
        api_url, data=json.dumps(payload).encode(), method='PUT',
        headers={**HEADERS, 'Content-Type': 'application/json'})
    try:
        resp = urllib.request.urlopen(req)
        commit = json.loads(resp.read())['commit']['sha'][:12]
        print(f'  ✓ {local_name} → {remote_name}  (commit: {commit})')
        return True
    except urllib.error.HTTPError as e:
        print(f'  ✗ 部署失败: {e.code} {e.read().decode()[:200]}')
        return False

if __name__ == '__main__':
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(FILE_MAP.keys())
    print(f'📦 部署到 https://{OWNER}.github.io/{REPO}/\n')
    ok = 0
    for local_name in targets:
        remote_name = FILE_MAP.get(local_name, local_name)
        if deploy_file(local_name, remote_name):
            ok += 1
    print(f'\n✅ 完成 ({ok}/{len(targets)})')
    print('⏳ 等待 1-2 分钟后刷新页面（Ctrl+Shift+R）')

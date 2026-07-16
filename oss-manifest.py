#!/usr/bin/env python3
"""
摄影资料库 — OSS Manifest 操作工具

用法:
  python3 oss-manifest.py download              # 下载当前 manifest 到本地
  python3 oss-manifest.py upload <ak> <sk>       # 上传本地 manifest 到 OSS
  python3 oss-manifest.py stats                  # 查看统计信息
"""
import json, hmac, hashlib, base64, urllib.request, sys, os
from datetime import datetime, timezone

BUCKET = 'dancer'
HOST = f'{BUCKET}.oss-cn-beijing.aliyuncs.com'
KEY = 'photography/manifest.json'
PUBLIC_URL = f'https://{HOST}/{KEY}'
LOCAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifest.json')

def download():
    print(f'⬇ 下载 {PUBLIC_URL}')
    data = urllib.request.urlopen(PUBLIC_URL).read()
    with open(LOCAL_FILE, 'wb') as f:
        f.write(data)
    m = json.loads(data)
    print(f'✓ 已保存到 manifest.json ({len(m["images"])} 张图片, {len(data)} bytes)')

def upload(ak, sk):
    if not os.path.exists(LOCAL_FILE):
        print('✗ manifest.json 不存在，先执行 download')
        return
    data = open(LOCAL_FILE, 'rb').read()
    ct = 'application/json'
    date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    sts = f'PUT\n\n{ct}\n{date}\nx-oss-object-acl:public-read\n/{BUCKET}/{KEY}'
    sig = base64.b64encode(hmac.new(sk.encode(), sts.encode(), hashlib.sha1).digest()).decode()

    req = urllib.request.Request(f'https://{HOST}/{KEY}', data=data, method='PUT')
    req.add_header('Date', date)
    req.add_header('Content-Type', ct)
    req.add_header('Authorization', f'OSS {ak}:{sig}')
    req.add_header('x-oss-object-acl', 'public-read')
    resp = urllib.request.urlopen(req)
    print(f'✓ 上传成功 (status: {resp.status}, {len(data)} bytes)')

def stats():
    data = json.loads(urllib.request.urlopen(PUBLIC_URL).read())
    imgs = data['images']
    libs = {}
    with_analysis = 0
    for img in imgs:
        lib = img.get('library', 'portrait')
        libs[lib] = libs.get(lib, 0) + 1
        if 'analysis' in img:
            with_analysis += 1
    all_tags = set()
    for img in imgs:
        all_tags.update(img.get('tags', []))

    print(f'📊 Manifest 统计')
    print(f'   总图片: {len(imgs)}')
    print(f'   已分析: {with_analysis}')
    print(f'   标签数: {len(all_tags)}')
    print(f'   各库:')
    for lib, count in sorted(libs.items(), key=lambda x: -x[1]):
        print(f'     {lib}: {count}')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'stats'
    if cmd == 'download':
        download()
    elif cmd == 'upload':
        if len(sys.argv) < 4:
            print('用法: python3 oss-manifest.py upload <AccessKeyId> <AccessKeySecret>')
        else:
            upload(sys.argv[2], sys.argv[3])
    elif cmd == 'stats':
        stats()
    else:
        print(__doc__)

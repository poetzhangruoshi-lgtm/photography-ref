# 摄影资料库 — 项目说明

## 一、项目概述

一个纯前端的摄影参考资料库，用于收集、分类、分析摄影样片。

- **线上地址**: https://poetzhangruoshi-lgtm.github.io/photography-ref/
- **GitHub 仓库**: https://github.com/poetzhangruoshi-lgtm/photography-ref
- **技术栈**: 单 HTML 文件（内联 CSS + JS），无构建工具，无框架
- **图片存储**: 阿里云 OSS（bucket: `dancer`, endpoint: `oss-cn-beijing.aliyuncs.com`, 前缀: `photography/`）
- **数据存储**: OSS 上的 `photography/manifest.json`（所有图片元数据的唯一数据源）

## 二、核心文件

| 文件 | 说明 |
|------|------|
| `photography.html` | **主文件**，~1125 行，包含全部 HTML/CSS/JS |
| `photography-site/index.html` | 部署副本，内容与 photography.html 相同 |
| `transition-techniques.html` | 镜头语言图鉴（独立页面，依赖 `data.js`） |
| `data.js` | 镜头语言数据文件 |
| `.tmp/analysis/manifest.json` | manifest 本地备份（含 139 张 AI 分析结果） |

## 三、架构设计

### 3.1 数据流

```
浏览器加载 → fetch manifest.json（公开读） → 渲染图片网格
                                                    ↓
                                         点击图片 → modal 展示
                                         （含 AI 分析、配色、描述）

管理员上传 → ossPut 图片到 OSS → ossSetAcl 设公开读
           → 更新本地 manifest → saveManifest 写回 OSS
```

### 3.2 多库架构

5 个资料库，每个库有独立的标签体系：

| 库 | ID | 标签分组 |
|----|------|----------|
| 人像 | `portrait` | 人数/场景/景别/镜头/风格/参考/色调/流派 |
| 景物 | `landscape` | 类型/时段/色调 |
| 绘画 | `painting` | 流派/媒介/色调 |
| 家居 | `interior` | 风格/空间/色调 |
| 服饰 | `fashion` | 品类/风格/季节/色调 |

标签定义在 `LIBRARY_TAG_GROUPS` 对象中。用户通过标签管理器新增的自定义标签存储在 `localStorage` 的 `custom_tags` 键中，按 `{库ID}:{分组名}` 归类。

### 3.3 权限模型

- **只读模式（默认）**: 任何人可浏览、筛选、查看分析
- **管理员模式**: 在页面点击"⚙ 管理" → 输入 OSS AccessKey ID/Secret → 存入 `localStorage`（`oss_credentials`）
- 管理员可：上传/删除图片、编辑标签、编辑描述、拖拽分组、管理标签

### 3.4 manifest.json 结构

```json
{
  "images": [
    {
      "id": "1783496041978_gicrxj",
      "ossKey": "photography/images/1783496041978_gicrxj.jpg",
      "library": "portrait",
      "tags": ["上半身", "日系透亮", "类滨田英明"],
      "group": "组 1",
      "name": "IMG_1234.jpg",
      "type": "image/jpeg",
      "size": 245760,
      "ts": 1783496041978,
      "colors": ["#2a1f1a", "#8b6b52", "#c4a882", "#e8d5c0", "#f5ede4"],
      "analysis": {
        "tone": "日系透亮",
        "school": "类滨田英明",
        "wb": {
          "kelvin": 5600,
          "tint": "G+2",
          "inCamera": "A7C2: 自定义白平衡 5600K, 色调偏绿+2",
          "postTips": "Lightroom: 高光-30, 阴影+20, 曝光+0.5"
        },
        "styleNote": "高调透亮，肤色干净通透，背景过曝柔化"
      },
      "desc": "用户手动添加的描述"
    }
  ]
}
```

### 3.5 localStorage 键

| 键 | 内容 |
|----|------|
| `oss_credentials` | `{ak, sk}` OSS 凭证 |
| `photo_tags` | 用户可见标签列表（合并默认+自定义） |
| `custom_tags` | 按库+分组存储的自定义标签，如 `{"portrait:风格":["赛博朋克"]}` |

## 四、⚠ 安全注意事项

**绝对不能把 OSS AK/SK 写入源代码或提交到 Git！** 凭证只存在用户浏览器的 localStorage 中。

- OSS AK/SK: 用户通过页面上的"⚙ 管理"按钮手动输入
- GitHub Token: `你的GitHub_Token`（classic token，repo scope）
- OSS bucket `dancer` 已配置 CORS（AllowedOrigin: *）

## 五、OSS 配置

- **Bucket**: `dancer`
- **Region**: `cn-beijing`
- **Endpoint**: `oss-cn-beijing.aliyuncs.com`
- **前缀**: `photography/`
- **图片路径**: `photography/images/{id}.{ext}`
- **清单路径**: `photography/manifest.json`
- **ACL**: 每个对象单独设置 `public-read`（通过 `ossSetAcl` 函数）
- **CORS**: 已配置 `AllowedOrigin: *`，允许 GET/PUT/DELETE/HEAD

## 六、开发与测试

### 6.1 本地开发

```bash
# 直接浏览器打开即可
open photography.html

# 或用简单 HTTP 服务器（推荐，避免 CORS 问题）
python3 -m http.server 8080
# 然后访问 http://localhost:8080/photography.html
```

### 6.2 修改代码

所有代码在 `photography.html` 一个文件中，结构：

```
第 1-204 行    CSS 样式
第 205-240 行  HTML 结构
第 241-1125 行 JavaScript

JS 分区：
  241-340   OSS 配置与操作（签名、上传、ACL、删除）
  341-380   Manifest 加载/保存
  381-430   标签系统（LIBRARY_TAG_GROUPS、自定义标签）
  431-455   库定义（LIBRARIES）
  456-510   Picker 弹窗（上传/编辑标签选择）
  511-530   render() 主渲染 + switchLibrary()
  531-700   renderLibrary()（筛选栏、分组展示、网格渲染）
  700-830   组图展示、标签管理器
  830-870   上传逻辑（uploadWithPicker）
  870-970   色彩提取（Median Cut 算法）
  970-1090  图片 Modal（展示、导航、AI 分析、描述编辑）
  1090-1125 初始化 + backfillColors
```

### 6.3 语法验证

```bash
# 用 Node.js 检查 JS 语法
node -e "
const fs=require('fs');
const html=fs.readFileSync('photography.html','utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
try{new Function(script);console.log('OK')}
catch(e){console.log('Error:',e.message)}
"
```

## 七、部署到 GitHub Pages

### 7.1 部署命令（Python 脚本）

```bash
python3 << 'PYEOF'
import json, base64, urllib.request

token = '你的GitHub_Token'
owner = 'poetzhangruoshi-lgtm'
repo = 'photography-ref'
path = 'index.html'
api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Python'
}

# 获取当前文件 SHA
req = urllib.request.Request(api_url, headers=headers)
resp = urllib.request.urlopen(req)
sha = json.loads(resp.read())['sha']

# 读取本地文件
with open('photography.html', 'rb') as f:
    content = base64.b64encode(f.read()).decode()

# 上传更新
payload = json.dumps({
    'message': '你的提交信息',
    'content': content,
    'sha': sha
}).encode()
req = urllib.request.Request(api_url, data=payload, method='PUT',
    headers={**headers, 'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
print(f'Deployed: {result["commit"]["sha"][:12]}')
PYEOF
```

### 7.2 部署注意

- 本地文件是 `photography.html`，部署到 GitHub 时文件名是 `index.html`
- GitHub Pages 配置：source branch = `main`，path = `/`
- repo 里有 `.nojekyll` 文件，跳过 Jekyll 构建
- 部署后等 1-2 分钟 CDN 生效，强制刷新用 Ctrl+Shift+R

### 7.3 部署其他页面

同样方法，只是 `path` 改为对应文件名，如 `transition-techniques.html`。

## 八、OSS Manifest 操作

### 8.1 上传 manifest（需要 AK/SK）

```bash
python3 << 'PYEOF'
import json, hmac, hashlib, base64, urllib.request
from datetime import datetime, timezone

ak = '你的AccessKeyId'
sk = '你的AccessKeySecret'
data = open('manifest.json', 'rb').read()

bucket = 'dancer'
host = f'{bucket}.oss-cn-beijing.aliyuncs.com'
key = 'photography/manifest.json'
ct = 'application/json'
date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
sts = f'PUT\n\n{ct}\n{date}\nx-oss-object-acl:public-read\n/{bucket}/{key}'
sig = base64.b64encode(hmac.new(sk.encode(), sts.encode(), hashlib.sha1).digest()).decode()

req = urllib.request.Request(f'https://{host}/{key}', data=data, method='PUT')
req.add_header('Date', date)
req.add_header('Content-Type', ct)
req.add_header('Authorization', f'OSS {ak}:{sig}')
req.add_header('x-oss-object-acl', 'public-read')
print(urllib.request.urlopen(req).status)
PYEOF
```

### 8.2 下载当前 manifest

```bash
curl -o manifest.json 'https://dancer.oss-cn-beijing.aliyuncs.com/photography/manifest.json'
```

## 九、AI 分析

### 9.1 已完成

- 139 张人像图片已完成 AI 分析（tone/school/wb/styleNote）
- 分析结果存储在 manifest.json 每张图的 `analysis` 字段中
- 分析数据同时同步到图片的 `tags` 数组（tone 和 school 值），用于筛选

### 9.2 新增图片分析

当前不支持浏览器端自动分析。新增图片的分析流程：

1. 从 OSS 下载图片到本地
2. 使用 Claude 视觉能力分析每张图片
3. 生成 analysis JSON（tone/school/wb/styleNote）
4. 更新 manifest.json 并上传回 OSS

分析数据格式：
```json
{
  "tone": "莫兰迪|日系透亮|欧美浓郁|胶片质感|黑白|高饱和|冷调|暖调",
  "school": "类滨田英明|类川内伦子|类蜷川实花|文艺复兴|印象派|...",
  "wb": {
    "kelvin": 5200,
    "tint": "M+3",
    "inCamera": "A7C2: 自定义白平衡 5200K, 色调偏洋红+3",
    "postTips": "Lightroom: 降饱和-25, 阴影+15, 高光-20"
  },
  "styleNote": "低饱和柔光，灰调混入所有色相，画面克制和谐"
}
```

### 9.3 批量分析方法

上次分析使用了并行 agent 方式：
1. 下载图片到本地 `.tmp/analysis/batch{N}/` 目录（每批 10 张）
2. 每批启动一个 agent 进行视觉分析
3. 结果写入 `batch{N}_results.json`
4. 用 `.tmp/analysis/merge_results.py` 合并到 manifest
5. 上传更新后的 manifest 到 OSS

## 十、已知问题与待办

### 已知问题
- 组图编号在创建时自动递增（组 1, 组 2...），但手动删除中间的组后编号不会重排
- `backfillColors()` 在管理员模式下会自动为没有配色数据的图片提取颜色，大量图片时可能较慢

### 待优化方向
- 移动端体验优化（响应式布局已有基础，但操作交互可改进）
- 图片懒加载（当前一次性加载所有图片 URL）
- 批量操作（多选删除、批量改标签等）
- 搜索功能（按描述、标签搜索）

## 十一、项目历史

| 阶段 | 内容 |
|------|------|
| 初始 | 知识型资料库（构图/光线/色彩/风格教程卡片 + 图片库） |
| 简化 | 删除知识区，简化为纯图片资料库 |
| 多库 | 添加景物/绘画/家居/服饰库，标签体系按库隔离 |
| AI 分析 | 139 张人像图片完成色调/流派/白平衡/风格分析 |
| 迁移 | OSS 从旧 bucket(sora-data) 迁移到新 bucket(dancer) |
| 部署 | GitHub Pages 部署，`.nojekyll` 跳过 Jekyll |

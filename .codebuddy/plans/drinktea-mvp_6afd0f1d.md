---
name: drinktea-mvp
overview: 从0搭建“来喝茶”MVP：用户端(H5+PC)Vue3+TS+Vant卡片流+反馈+PWA离线缓存；后台管理(单管理员登录)Vue3+TS；后端FastAPI+SQLite实现内容管理、Excel导入、推荐排序与数据看板，并将PRD/设计文档写入docs/。
design:
  architecture:
    framework: vue
  styleKeywords:
    - Glassmorphism
    - 卡片流
    - 沉浸式滑动
    - 管理台清晰层级
    - 微动效与骨架屏
  fontSystem:
    fontFamily: PingFang SC
    heading:
      size: 28px
      weight: 600
    subheading:
      size: 18px
      weight: 600
    body:
      size: 15px
      weight: 400
  colorSystem:
    primary:
      - "#16A34A"
      - "#22C55E"
      - "#0EA5A4"
    background:
      - "#0B1220"
      - "#0F172A"
      - "#FFFFFF"
    text:
      - "#0F172A"
      - "#E5E7EB"
      - "#FFFFFF"
    functional:
      - "#2563EB"
      - "#F59E0B"
      - "#EF4444"
      - "#10B981"
todos:
  - id: write-docs
    content: 用[subagent:code-explorer]确认空目录并生成docs设计与接口文档
    status: completed
  - id: user-card-feed
    content: 实现用户端卡片流首页、加载态、离线提示与详情跳转
    status: completed
    dependencies:
      - write-docs
  - id: user-detail-feedback
    content: 实现详情页轻交互与反馈提交页（成功/失败/重试）
    status: completed
    dependencies:
      - user-card-feed
  - id: admin-login
    content: 实现后台单管理员登录、路由拦截、退出与错误提示
    status: completed
    dependencies:
      - write-docs
  - id: admin-content-manage
    content: 实现内容列表检索、创建编辑、上下架与推荐权重配置
    status: completed
    dependencies:
      - admin-login
  - id: excel-import
    content: 实现Excel导入向导、字段校验、导入报告与失败明细导出
    status: completed
    dependencies:
      - admin-content-manage
  - id: dashboard
    content: 实现数据看板指标卡与趋势图，支持时间范围切换
    status: completed
    dependencies:
      - admin-content-manage
---

## Product Overview

“来喝茶”MVP包含用户端（H5+PC）与后台管理：用户通过卡片流浏览内容并提交反馈；管理员维护内容、批量导入、调整推荐排序并查看数据看板；支持离线浏览与基础缓存体验；项目内置文档中心，所有PRD/设计/接口说明以文件形式沉淀在`docs/`。

## Core Features

- **用户端卡片流浏览**：首屏卡片瀑布/滑动流，支持上拉加载、卡片动效、快速进入详情；PC为居中内容区+侧栏信息，H5为全屏沉浸式滑动。
- **内容详情与轻交互**：详情页展示封面、标题、正文与标签；提供“喜欢/不喜欢/已读”类轻量交互，按钮有按压反馈与状态切换。
- **反馈收集**：在内容页或独立反馈页提交问题/建议（文本+可选联系方式）；提交过程有加载态、成功提示与失败重试。
- **离线可用体验**：弱网/断网时可打开应用、查看已缓存列表与最近浏览详情；离线状态有明显提示条与重连提示。
- **后台单管理员登录**：账号密码登录后进入管理台；未登录访问会被拦截并跳转登录页，界面呈现清晰的权限边界与退出入口。
- **内容管理与推荐排序**：后台提供内容列表检索、创建/编辑/上下架、标签管理；可配置推荐权重/排序规则并即时预览排序结果。
- **Excel批量导入**：上传Excel后进行字段映射与校验提示，导入完成展示成功/失败条目统计与可下载失败原因。
- **数据看板**：展示浏览量、喜欢/不喜欢、反馈量、导入成功率等关键指标；图表支持时间范围切换与卡片式指标概览。

## Tech Stack

- 用户端：Vue 3 + TypeScript（PWA离线缓存）
- 后台管理：Vue 3 + TypeScript
- 后端：Python FastAPI
- 数据库：SQLite
- 数据导入：Excel解析（后端）
- 文档：Markdown写入`docs/`

## Architecture Design

### System Architecture

```mermaid
flowchart LR
  U[用户端(H5/PC)] -->|HTTPS JSON| API[FastAPI]
  A[后台管理] -->|HTTPS JSON| API
  API --> DB[(SQLite)]
  U --> SW[PWA Service Worker]
  SW --> C[(Cache Storage)]
  API --> FS[(docs/ 文件系统)]
```

### Module Division

- **User Web App**：卡片流、详情、反馈入口、离线提示与缓存读取
- **Admin Web App**：登录、内容CRUD、Excel导入、排序配置、数据看板
- **Backend API**：鉴权、内容管理、反馈收集、导入处理、推荐排序、统计聚合
- **Data Layer**：SQLite表结构与索引、基础迁移脚本
- **Docs Module**：PRD/设计/接口/数据字典以Markdown存放与版本化

### Data Flow

- **内容浏览**：用户请求列表 → API返回分页数据+排序结果 → 前端渲染卡片 → 进入详情记录浏览事件 → 更新统计
- **反馈提交**：前端表单校验 → API写入反馈表 → 返回结果 → 前端展示成功/失败态（失败可重试）
- **Excel导入**：后台上传文件 → API解析并校验 → 批量写入SQLite（事务）→ 返回导入报告（成功/失败原因）
- **排序更新**：管理员修改权重/规则 → API保存配置 → 列表接口按配置计算排序 → 后台预览与用户端生效
- **看板统计**：事件写入（浏览/点赞/反馈）→ 定时/按需聚合查询 → API返回指标与趋势序列

## Implementation Details

### Core Directory Structure (New Project)

```
drinkTea/
├── apps/
│   ├── user-web/                 # 用户端
│   └── admin-web/                # 后台管理端
├── backend/
│   ├── app/
│   │   ├── api/                  # 路由
│   │   ├── core/                 # 配置/鉴权/依赖
│   │   ├── models/               # ORM/表模型
│   │   ├── services/             # 业务服务：导入/排序/统计
│   │   └── schemas/              # Pydantic Schema
│   └── tests/
├── docs/
│   ├── prd.md
│   ├── design.md
│   ├── api.md
│   └── data-dict.md
└── README.md
```

### Key Data Structures (Backend)

- Content：id、title、cover、body、tags、status、weight、created_at、updated_at
- Feedback：id、content_id(可空)、message、contact(可空)、created_at
- Event：id、content_id、type(view/like/dislike)、created_at
- Admin：username、password_hash（单账号）

### Technical Implementation Plan (High-level)

1. **鉴权与单管理员**

- Approach：用户名+密码登录获取会话/令牌；管理端路由守卫；后端依赖注入校验
- Testing：登录成功/失败、未授权访问拦截、退出与令牌失效

2. **内容管理与排序**

- Approach：CRUD接口+列表分页；排序由weight+状态+更新时间等组成；后台提供权重编辑
- Testing：分页一致性、排序可预测性、上下架立即生效

3. **Excel导入**

- Approach：上传→解析→字段校验→事务批量写入→返回错误明细
- Testing：空表/缺列/类型错误/重复数据/大文件性能

4. **数据看板**

- Approach：事件采集→聚合查询（按天/按范围）→返回指标卡+折线/柱状数据
- Testing：统计准确性、时间范围边界、空数据展示

5. **PWA离线缓存**

- Approach：缓存壳资源+列表/详情最近访问数据；断网回退到缓存；在线更新策略
- Testing：断网打开、缓存命中率、版本更新与缓存清理

## Design Style

- 用户端：沉浸式卡片流（大圆角卡片、阴影分层、轻微视差与滑动动效），H5强调全屏滑动与手势反馈；PC为居中主列+右侧信息栏，滚动更顺滑。
- 后台：清晰的管理台信息层级（左侧导航/顶部工具条/主内容表格与表单），表单与表格强调可读性与批量操作效率。

## Page Planning (≤5)

1. 用户端-卡片流首页：瀑布/滑动列表、筛选/搜索入口、离线提示条、加载骨架屏
2. 用户端-内容详情：封面头图、正文排版、标签、喜欢/不喜欢/反馈入口、返回与分享
3. 用户端-反馈页：问题类型/文本输入、可选联系方式、提交状态与历史提示
4. 后台-登录页：居中卡片登录、错误提示、加载态与退出
5. 后台-管理台（内容+导入+看板）：导航切换；内容表格+编辑抽屉；导入向导；指标卡+趋势图表

## Visual Effects

- 卡片悬浮与按压微动效、骨架屏渐隐、空状态插画、离线/弱网顶部提示条、操作成功Toast与失败重试按钮。

## Agent Extensions

- **SubAgent: code-explorer**
- Purpose: 扫描工作区结构、定位/创建关键模块文件与docs文档落点，持续核对实现与目录一致性
- Expected outcome: 输出可验证的目录与文件清单，确保前后端与文档按计划落地且可被后续任务准确引用
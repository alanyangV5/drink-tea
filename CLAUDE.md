# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**来喝茶** 是一个基于卡片流滑动的茶叶发现平台。用户以类似 Tinder 的方式浏览茶叶卡片并进行喜欢/不喜欢的反馈。平台包含两个 Vue 3 前端（用户端和管理端）以及一个 FastAPI + SQLite 后端。

- **用户端 Web**: H5/PC 界面，支持 PWA，用于浏览茶叶卡片
- **管理端 Web**: 仪表板，用于茶叶管理、Excel 导入和数据分析
- **后端**: FastAPI + SQLite，提供内容和用户反馈追踪

## 开发命令

### 后端 (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 配置 ADMIN_PASSWORD 和 JWT_SECRET
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档：`http://localhost:8000/docs`（自动生成的 Swagger UI）

### 用户端前端

```bash
cd apps/user-web
npm install
npm run dev      # 开发服务器（端口 5173）
npm run build    # 生产构建（运行 vue-tsc + vite build）
npm run preview  # 预览生产构建
```

### 管理端前端

```bash
cd apps/admin-web
npm install
npm run dev      # 开发服务器（端口 5174）
npm run build    # 生产构建
npm run preview  # 预览生产构建
```

## 架构

### 后端结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用工厂
│   ├── models.py            # SQLAlchemy ORM 模型
│   ├── schemas.py           # Pydantic 验证模型
│   ├── db.py                # 数据库连接
│   ├── core/
│   │   ├── config.py        # 环境变量配置
│   │   └── security.py      # JWT 认证
│   ├── services/
│   │   └── reco.py          # 推荐算法
│   └── api/
│       ├── deps.py          # 依赖注入（认证检查）
│       ├── public.py        # 公开端点（teas, events, feedback）
│       └── admin.py         # 管理端点（auth, CRUD, dashboard）
└── data/uploads/            # 静态文件服务（茶叶图片）
```

**核心数据表**：
- `tea`: 茶叶信息（name, category, year, origin, price, cover_url, status, weight）
- `tea_events`: 用户交互（impression, detail_open）
- `feedback`: 用户喜欢/不喜欢（anon_user_id, tea_id, action）
- `messages`: 联系表单提交
- `users`: 管理员账号

**API 路由**：
- 公开：`/api/teas`, `/api/events`, `/api/feedback`, `/api/feedback/message`
- 管理：`/api/admin/login`, `/api/admin/teas`, `/api/admin/upload`, `/api/admin/import/*`, `/api/admin/dashboard/*`

### 前端架构

两个前端都使用 **Vue 3 Composition API** + TypeScript + Vite + Tailwind CSS。

**用户端** (`apps/user-web/`）：
- 使用 **Vant 4**（移动端优先的 UI 组件库）
- 在 `App.vue` 中实现自定义拖拽/滑动卡片交互
- 通过 `vite-plugin-pwa` 实现 PWA 缓存（离线缓存最近 20 张卡片）
- 通过 localStorage UUID 追踪匿名用户
- 核心组件：`TeaCard`, `FeedHeader`（分类筛选器）

**管理端** (`apps/admin-web/`）：
- 使用 **Pinia** 进行状态管理
- 使用 **ECharts** 进行数据可视化
- JWT 认证，Bearer token 存储在 localStorage
- 管理路由的路由守卫

### 推荐系统

后端使用可解释的评分算法（非 ML）：

```
score = weight + 100*likeRate + personal_boost + recency_boost
```

- `likeRate = (likes + 1) / (pv + 2)`（平滑喜好率）
- `personal_boost`：基于用户历史对同分类/年份段茶叶的喜欢/不喜欢
- `recency_boost`：最近 7 天上架的茶叶小幅加成
- `weight`：管理员可配置的手动权重

前端通过 localStorage (`YYYY-MM-DD -> { teaId: action }`) 过滤已查看的茶叶，后端通过 `exclude_ids` 查询参数进行排除。

## 重要设计原则

1. **极简主义美学**：宣纸白主题 (#FFFDF9)，充足留白，衬线字体展示茶名
2. **移动端优先交互**：
   - 右滑 = 喜欢，左滑 = 不喜欢（30% 宽度阈值）
   - PC 端：方向键（→/←）喜欢/不喜欢，滚轮切换
3. **每日反馈防重**：用户每天对同一茶叶只能提交一次反馈
4. **匿名追踪**：无用户注册；localStorage UUID + 可选联系方式
5. **分类标签**：普洱 (pu_er), 白茶 (white), 岩茶 (yancha), 红茶 (black)

## 数据管理

**Excel 导入**：管理员可通过 Excel 批量导入茶叶。模板在 `docs/import-template.csv`。后端使用 pandas + openpyxl 解析。导入流程：
1. POST `/api/admin/import/excel` - 上传并解析，返回校验预览
2. POST `/api/admin/import/commit` - 确认并写入数据库

**图片上传**：POST `/api/admin/upload` (multipart/form-data)，返回从 `/uploads/*` 提供的 URL

## 环境变量（后端）

`backend/.env` 中必需：
- `ADMIN_PASSWORD` 或 `ADMIN_PASSWORD_HASH`：管理员凭据
- `JWT_SECRET`：Token 签名密钥

可选：
- `CORS_ORIGINS`：逗号分隔列表（如 `http://localhost:5173,http://localhost:5174`）

## 文档

查看 `/docs/` 获取详细规格：
- `prd.md`：产品需求文档（中文）
- `design.md`：系统设计和数据模型
- `api.md`：API 端点文档
- `data-dict.md`：数据字典
- `import-template.csv`：Excel 导入模板

## 常用模式

**Vue 组件结构**：
```typescript
<script setup lang="ts">
import { ref, onMounted } from 'vue'
// 使用 ref/reactive 管理状态
// 在 onMounted 中调用 API
</script>

<template>
  <!-- 使用 Tailwind 类名进行样式设计 -->
</template>
```

**FastAPI 端点模式**：
```python
@router.get("/api/teas")
def list_teas(
    category: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    # 查询逻辑
    # 返回 Pydantic schema
```

**管理员认证检查**：在受保护的路由上使用 `app.api.deps` 中的 `get_current_admin()` 依赖。

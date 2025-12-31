# 《来喝茶》设计文档（MVP）

## 0. 摘要

本设计文档基于 `docs/prd.md`（PRD）落地“来喝茶”MVP：用户端以极简卡片流沉浸浏览茶叶条目并做喜欢/不喜欢反馈；后台提供单管理员登录、茶叶内容管理、Excel 批量导入、数据看板；后端 FastAPI + SQLite 提供内容、推荐与统计接口；PWA 缓存最近 20 张卡片以支持弱网/离线。

## 1. 范围与非目标

### 1.1 范围（MVP）

- 用户端（H5 + PC）：
  - 卡片流浏览（分页/触底加载）
  - 分类筛选（普洱/白茶/岩茶/红茶）
  - 详情展开（产地/简介/价格区间/规格）
  - 喜欢/不喜欢反馈（移动端手势，PC 键鼠）
  - 防重复：反馈后当日不再展示
  - 异常与占位：空库/网络错误/图片失败
  - PWA：离线缓存最近 20 张卡片
- 后台：
  - 单管理员账号密码登录
  - 茶叶 CRUD + 上下架 + 推荐权重
  - Excel 导入（模板、校验、导入报告）
  - 看板（PV、喜欢、不喜欢、喜好率；排行；预警标注）

### 1.2 非目标（MVP 不做）

- 用户注册/登录体系（仅匿名）
- 付费订阅、趋势报告
- 复杂推荐（深度学习/协同过滤），仅可解释规则模型

## 2. 架构与模块

### 2.1 总体架构

- `apps/user-web`：Vue3 + TS + Vant（卡片流/PWA）
- `apps/admin-web`：Vue3 + TS（管理后台）
- `backend`：FastAPI + SQLite（SQLAlchemy）
- `docs`：PRD/设计/API/数据字典

### 2.2 模块划分

- 用户端：`feed`（卡片流）、`detail`（详情）、`feedback`（喜欢/不喜欢）、`pwa`（缓存/离线提示）
- 后台：`auth`（登录/鉴权）、`teas`（内容管理）、`import`（Excel 导入）、`dashboard`（看板）
- 后端：`public_api`（feed/detail/feedback/events）、`admin_api`（auth/teas/import/dashboard）、`services`（推荐/统计/导入）

## 3. 数据模型（SQLite）

> 约束：字段命名以英文 snake_case；时间均为 UTC 或本地统一时区（MVP 可用本地时间，但需固定）。

### 3.1 `tea`

- `id`：INTEGER PK
- `name`：TEXT（必填）
- `category`：TEXT（必填，枚举：pu_er/white/yancha/black 等）
- `year`：INTEGER（必填）
- `origin`：TEXT（必填）
- `spec`：TEXT（必填）
- `price_min`：INTEGER（可空）
- `price_max`：INTEGER（可空）
- `intro`：TEXT（可空）
- `cover_url`：TEXT（必填）
- `status`：TEXT（online/offline）
- `weight`：INTEGER（默认 0）
- `created_at` / `updated_at`：DATETIME

### 3.2 `event`

- `id`：INTEGER PK
- `anon_user_id`：TEXT（匿名ID）
- `tea_id`：INTEGER
- `type`：TEXT（impression/detail_open）
- `created_at`：DATETIME

### 3.3 `feedback`

- `id`：INTEGER PK
- `anon_user_id`：TEXT
- `tea_id`：INTEGER
- `action`：TEXT（like/dislike）
- `created_at`：DATETIME
- 约束：同一 `anon_user_id + tea_id + date` 仅保留一次（MVP：写入时检查当天是否已有）

## 4. 推荐与防重复

### 4.1 防重复（当日）

- 前端：本地 `localStorage` 记录 `YYYY-MM-DD -> { teaId: action }`
- 后端：列表接口支持 `exclude_ids`（或接收 `anon_user_id` 并在服务端过滤当日反馈过的茶）
- 最终策略：前端过滤 + 后端兜底

### 4.2 推荐排序（可解释）

MVP 采用可解释打分：

- 全局偏好：
  - `pv` = impression 数
  - `likes` / `dislikes` = feedback 聚合
  - 平滑喜好率：\( likeRate = \frac{likes+1}{pv+2} \)
- 时效加成：近 7 天上架微弱加成
- 人工权重：后台可配置 `weight`
- 个性化：按 `anon_user_id` 的历史 like/dislike，给同分类/同年份段条目加减分

最终：`score = weight + 100*likeRate + personal_boost + recency_boost`。

## 5. API（概要）

完整接口见 `docs/api.md`。

- 公共：
  - `GET /api/teas`（feed）
  - `GET /api/teas/{id}`（detail）
  - `POST /api/events`（impression/detail_open）
  - `POST /api/feedback`（like/dislike）
- 管理端（需登录）：
  - `POST /api/admin/login`
  - `POST /api/admin/logout`
  - `GET/POST/PUT/DELETE /api/admin/teas`
  - `POST /api/admin/upload`
  - `POST /api/admin/import/excel`（解析预览）
  - `POST /api/admin/import/commit`（确认导入）
  - `GET /api/admin/dashboard/summary`
  - `GET /api/admin/dashboard/rank`

## 6. 前端交互细则

### 6.1 移动端滑动

- 右滑喜欢：卡片右飞 + 爱心变红
- 左滑不喜欢：卡片左飞
- 滑动阈值：横向位移超过卡片宽度的 30% 即判定

### 6.2 PC 键鼠

- `→` 喜欢、`←` 不喜欢
- 滚轮：切换下一张/上一张（节流）
- Hover：显示两个按钮

### 6.3 异常与文案

- 空库：新茶即将上架，敬请期待
- 网络：网络波动，点击品茗杯重试
- 图片失败：茶山云雾占位图

## 7. 安全与鉴权（后台）

- 单管理员：用户名+密码（密码哈希存储），登录返回 token（Bearer）
- 管理端路由守卫：无 token 跳转登录页
- token 过期：提示并要求重新登录

## 8. 里程碑与验收（MVP）

- 用户端：可连续浏览、可反馈、可筛选、异常可恢复；离线可打开且有最近卡片
- 后台：可登录、可增删改茶叶、可导入 Excel、可看到看板指标
- 后端：接口可用，统计口径一致

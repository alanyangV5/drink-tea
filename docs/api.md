# 《来喝茶》API 文档（MVP）

Base URL（开发）：`http://localhost:8000`

## 1. 通用约定

- 时间：ISO8601 字符串
- 分页：`page` + `page_size`（MVP）；后续可升级 cursor
- 错误结构：

```json
{ "code": "string", "message": "string" }
```

## 2. 公共接口（用户端）

### 2.1 获取卡片流

`GET /api/teas`

Query:
- `category`：可选（pu_er/white/yancha/black）
- `page`：默认 1
- `page_size`：默认 10
- `anon_user_id`：可选（用于个性化/过滤）
- `exclude_ids`：可选（逗号分隔）

Response（示例）：

```json
{
  "items": [
    {
      "id": 1,
      "name": "2022 易武古树生茶",
      "category": "pu_er",
      "year": 2022,
      "origin": "云南·西双版纳·易武",
      "spec": "357g/饼",
      "price_min": 280,
      "price_max": 520,
      "intro": "蜜香清扬，汤感细腻，回甘绵长。",
      "cover_url": "/uploads/tea-1.jpg",
      "status": "online",
      "weight": 0
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 100
}
```

### 2.2 茶叶详情

`GET /api/teas/{id}`

### 2.3 事件上报

`POST /api/events`

Body:

```json
{ "anon_user_id": "uuid", "tea_id": 1, "type": "impression" }
```

### 2.4 反馈（喜欢/不喜欢）

`POST /api/feedback`

Body:

```json
{ "anon_user_id": "uuid", "tea_id": 1, "action": "like" }
```

### 2.5 意见反馈（文本）

`POST /api/feedback/message`

Body:

```json
{ "anon_user_id": "uuid", "message": "想按香型筛选…", "contact": "可选", "tea_id": 1 }
```

## 3. 管理端接口（需登录）

### 3.1 登录

`POST /api/admin/login`

Body:

```json
{ "username": "admin", "password": "***" }
```

Response:

```json
{ "token": "BearerToken" }
```

### 3.2 茶叶管理

- `GET /api/admin/teas`：列表（支持 `keyword/status/category`）
- `POST /api/admin/teas`：创建
- `PUT /api/admin/teas/{id}`：更新
- `DELETE /api/admin/teas/{id}`：删除

### 3.3 图片上传

`POST /api/admin/upload`（multipart/form-data）

### 3.4 Excel 导入

- `POST /api/admin/import/excel`：上传并解析预览（返回校验结果）
- `POST /api/admin/import/commit`：确认写库（可带 `import_id`）

### 3.5 数据看板

- `GET /api/admin/dashboard/summary?from=YYYY-MM-DD&to=YYYY-MM-DD`（可不带参数=全量）
- `GET /api/admin/dashboard/rank?sort=like_rate|created_at&from=YYYY-MM-DD&to=YYYY-MM-DD`
- `GET /api/admin/dashboard/trend?from=YYYY-MM-DD&to=YYYY-MM-DD`

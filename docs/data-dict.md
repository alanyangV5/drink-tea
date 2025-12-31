# 《来喝茶》数据字典（MVP）

## 1. 茶叶表 `tea`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | Y | 主键 |
| name | text | Y | 名称 |
| category | text | Y | 分类：pu_er/white/yancha/black |
| year | int | Y | 年份 |
| origin | text | Y | 产地 |
| spec | text | Y | 规格 |
| price_min | int | N | 价格下限 |
| price_max | int | N | 价格上限 |
| intro | text | N | 简介 |
| cover_url | text | Y | 主图URL |
| status | text | Y | online/offline |
| weight | int | Y | 推荐权重（人工） |
| created_at | datetime | Y | 创建时间 |
| updated_at | datetime | Y | 更新时间 |

## 2. 事件表 `event`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | Y | 主键 |
| anon_user_id | text | Y | 匿名用户ID |
| tea_id | int | Y | 茶叶ID |
| type | text | Y | impression/detail_open |
| created_at | datetime | Y | 发生时间 |

## 3. 反馈表 `feedback`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | Y | 主键 |
| anon_user_id | text | Y | 匿名用户ID |
| tea_id | int | Y | 茶叶ID |
| action | text | Y | like/dislike |
| created_at | datetime | Y | 反馈时间 |

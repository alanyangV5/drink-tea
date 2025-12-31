# 来喝茶（MVP）

本仓库包含：
- 用户端（H5+PC）：`apps/user-web`（Vue3 + TS + Vant + PWA）
- 后台管理：`apps/admin-web`（Vue3 + TS）
- 后端 API：`backend`（FastAPI + SQLite）
- 文档：`docs/`

## 文档

- `docs/prd.md`
- `docs/design.md`
- `docs/api.md`
- `docs/data-dict.md`
- `docs/import-template.csv`（Excel/表格导入模板，直接用 Excel 打开也可）

## 环境要求

- Node.js 18+（用于前端）
- Python 3.10+（用于后端）

> 说明：当前自动化执行环境里没有 Node.js，因此前端依赖安装/运行需要你本机安装 Node 后执行。

## 启动后端（FastAPI）

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 至少配置 ADMIN_PASSWORD 或 ADMIN_PASSWORD_HASH、JWT_SECRET

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 启动用户端（user-web）

```bash
cd apps/user-web
npm install
npm run dev
```

## 启动后台（admin-web）

```bash
cd apps/admin-web
npm install
npm run dev
```

## 常用地址

- 后端：`http://localhost:8000/health`
- 用户端：Vite 输出的地址（默认 `http://localhost:5173`）
- 后台：Vite 输出的地址（默认 `http://localhost:5174` 或占用后顺延）

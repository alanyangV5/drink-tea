# 后端（FastAPI + SQLite）

## 依赖安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 环境变量

复制并修改：

- `backend/.env.example` → `backend/.env`

至少需要配置：
- `ADMIN_PASSWORD` 或 `ADMIN_PASSWORD_HASH`
- `JWT_SECRET`

## 启动

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

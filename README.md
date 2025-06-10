# C-Judge

C语言评测系统，支持学生、教师和管理员三种角色，提供练习管理、课程管理、班级管理和题目评测等功能。

## 功能特点

- 三种用户角色：学生、教师和管理员
- 练习管理：创建、修改、删除练习
- 题目管理：上传、维护题目
- 班级管理：创建班级、添加学生
- 课程管理：创建课程、关联班级和教师
- 自动评测：集成评测服务，支持C语言代码评测
- 操作记录：记录用户的操作历史
- 管理员：admin / admin

## 项目结构

```
C-Judge/
├── docker/             # Docker配置文件
├── backend/            # 后端代码
├── frontend/           # 前端代码
└── README.md           # 项目说明
```

数据库：![1749479270436](image/README/1749479270436.png)

# C-Judge

用于c语言测评的系统（教育场景）

C-Judge/
├── docker/
│   ├── judge/                # 评测服务配置（已有）
│   │   └── docker-compose.yml
│   ├── backend/              # 后端服务Dockerfile
│   ├── frontend/             # 前端服务Dockerfile
│   ├── db/                   # 数据库初始化脚本
│   └── docker-compose.yml    # 主Docker Compose文件
│
├── backend/                  # 后端代码
│   ├── app/
│   │   ├── api/              # API路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑
│   │   └── utils/            # 工具函数
│   ├── config/               # 配置文件
│   ├── requirements.txt      # 依赖
│   └── main.py               # 入口文件
│
├── frontend/                 # 前端代码
│   ├── public/
│   ├── src/
│   │   ├── api/              # API调用
│   │   ├── components/       # 组件
│   │   ├── pages/            # 页面
│   │   ├── store/            # 状态管理
│   │   └── utils/            # 工具函数
│   ├── package.json
│   └── vite.config.js
│
└── README.md                 # 项目说明

## 技术选型

为了保持简洁高效，我建议使用以下技术栈：

后端：* FastAPI (Python)：轻量级、高性能的API框架

* SQLAlchemy：ORM框架
* PostgreSQL：关系型数据库
* Redis：缓存和会话管理

前端：* Vue 3：渐进式JavaScript框架

* Element Plus：UI组件库
* Axios：HTTP客户端
* Pinia：状态管理

部署：* Docker & Docker Compose：容器化部署

* Nginx：反向代理和静态文件服务

api:

# 认证

POST /api/auth/login
POST /api/auth/logout
PUT /api/auth/password

# 用户管理

GET /api/users
POST /api/users
GET /api/users/{id}
PUT /api/users/{id}
DELETE /api/users/{id}
POST /api/users/batch-import

# 班级管理

GET /api/classes
POST /api/classes
PUT /api/classes/{id}
DELETE /api/classes/{id}

# 课程管理

GET /api/courses
POST /api/courses
PUT /api/courses/{id}
DELETE /api/courses/{id}

# 练习管理

GET /api/exercises
POST /api/exercises
GET /api/exercises/{id}
PUT /api/exercises/{id}
DELETE /api/exercises/{id}
GET /api/exercises/{id}/problems
POST /api/exercises/{id}/problems
DELETE /api/exercises/{id}/problems/{problem_id}

# 题目管理

GET /api/problems
POST /api/problems
GET /api/problems/{id}
PUT /api/problems/{id}
DELETE /api/problems/{id}
POST /api/problems/upload

# 提交管理

POST /api/submissions
GET /api/submissions
GET /api/submissions/{id}
GET /api/exercises/{id}/statistics

# 操作日志

GET /api/logs

# 系统设置

GET /api/settings
PUT /api/settings

# C-Judge

C语言测评系统，支持学生、教师和管理员三种角色，提供练习管理、课程管理、班级管理和题目评测等功能。

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
├── 题库/               # 题库目录（不包含在Git仓库中）
└── README.md           # 项目说明
```

## 题库目录结构

题库目录存放评测系统使用的所有题目，按照以下结构组织：

```
题库/
├── 基础题库/                      # 题库分类一
│   ├── 1.顺序结构/                # 题目分类
│   │   ├── problem1/             # 具体题目
│   │   │   ├── Question.INF      # 题目配置文件
│   │   │   ├── Question.md       # 题目描述
│   │   │   ├── StdAnswer.c       # 标准答案
│   │   │   └── TestData/         # 测试数据
│   │   │       ├── input1.txt    # 输入样例
│   │   │       └── output1.txt   # 输出样例
│   │   └── problem2/
│   │       └── ...
│   ├── 2.分支结构/
│   └── ...
└── 高级题库/                      # 题库分类二
    └── ...
```

### 题目配置文件 (Question.INF)

每个题目文件夹中必须包含一个 `Question.INF` 文件，用于配置题目的基本信息：

```
试题中文名称="Hello World"
时间限制=1000 //ms
内存限制=65535 //KB
```

> 注意：题库目录不包含在Git仓库中，需要单独准备并放置在项目根目录下。

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
├── 题库/                     # 题库目录（不包含在Git仓库中）
│   ├── 基础题库/
│   └── 高级题库/
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

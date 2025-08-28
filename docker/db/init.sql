-- 创建用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    real_name VARCHAR(50),
    role VARCHAR(20) NOT NULL, -- 'student', 'teacher', 'admin'
    is_online BOOLEAN DEFAULT FALSE,
    register_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建班级表
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建学生-班级关联表
CREATE TABLE student_class (
    student_id INTEGER REFERENCES users(id),
    class_id INTEGER REFERENCES classes(id),
    PRIMARY KEY (student_id, class_id)
);

-- 创建教师-班级关联表
CREATE TABLE teacher_class (
    teacher_id INTEGER REFERENCES users(id),
    class_id INTEGER REFERENCES classes(id),
    PRIMARY KEY (teacher_id, class_id)
);

-- 创建课程表
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    teacher_id INTEGER REFERENCES users(id),
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建课程-班级关联表
CREATE TABLE course_class (
    course_id INTEGER REFERENCES courses(id),
    class_id INTEGER REFERENCES classes(id),
    PRIMARY KEY (course_id, class_id)
);

-- 创建练习表
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    course_id INTEGER REFERENCES courses(id),
    publisher_id INTEGER REFERENCES users(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_online_judge BOOLEAN DEFAULT TRUE,
    allowed_languages VARCHAR(255), -- 逗号分隔的语言列表
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建标签类型表
CREATE TABLE tag_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建标签表
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    tag_type_id INTEGER REFERENCES tag_types(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, tag_type_id)
);

-- 创建题目表
CREATE TABLE problems (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    chinese_name VARCHAR(100),
    owner_id INTEGER REFERENCES users(id),
    category VARCHAR(50),
    is_shared BOOLEAN DEFAULT FALSE,
    time_limit INTEGER DEFAULT 1000, -- ms
    memory_limit INTEGER DEFAULT 134217728, -- bytes (128MB)
    code_check_score INTEGER DEFAULT 20,
    runtime_score INTEGER DEFAULT 80,
    score_method VARCHAR(20) DEFAULT 'sum', -- 'sum' or 'max'
    data_path VARCHAR(255),
    reference_answer TEXT, -- 新增：参考答案（可为空）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建问题-标签关联表
CREATE TABLE problem_tag (
    problem_id INTEGER REFERENCES problems(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (problem_id, tag_id)
);

-- 创建练习-题目关联表
CREATE TABLE exercise_problem (
    exercise_id INTEGER REFERENCES exercises(id),
    problem_id INTEGER REFERENCES problems(id),
    sequence INTEGER NOT NULL, -- 题目在练习中的序号
    PRIMARY KEY (exercise_id, problem_id)
);

-- 创建提交记录表
CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    problem_id INTEGER REFERENCES problems(id),
    exercise_id INTEGER REFERENCES exercises(id),
    code TEXT NOT NULL,
    language VARCHAR(20) DEFAULT 'c',
    status VARCHAR(20),
    code_check_score INTEGER,
    runtime_score INTEGER,
    total_score INTEGER,
    result JSONB, -- 评测结果详情
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建操作记录表
CREATE TABLE operation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    operation VARCHAR(100) NOT NULL,
    target VARCHAR(255), -- 操作对象，如练习名称、题目名称等
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建系统设置表
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认管理员账户
INSERT INTO users (username, password, real_name, role) 
VALUES ('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '系统管理员', 'admin');

-- 插入默认系统设置
INSERT INTO system_settings (key, value) VALUES 
('rows_per_page', '10'),
('default_code_check_score', '0'),
('allow_student_change_password', 'true'); 

-- 插入默认标签类型
INSERT INTO tag_types (name) VALUES 
('难度'),
('知识点');

-- 创建标签审核请求表
CREATE TABLE tag_approval_requests (
    id SERIAL PRIMARY KEY,
    problem_data_path VARCHAR(255) NOT NULL,
    requestor_id INTEGER REFERENCES users(id),
    tag_ids JSONB NOT NULL, -- 存储标签ID数组
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    request_message TEXT, -- 申请说明
    reviewer_id INTEGER REFERENCES users(id), -- 审核者
    review_message TEXT, -- 审核说明
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

-- 插入默认标签
INSERT INTO tags (name, tag_type_id) VALUES 
('高', 1),
('中', 1),
('低', 1),
('数组', 2),
('结构体', 2),
('指针', 2),
('函数', 2),
('递归', 2); 
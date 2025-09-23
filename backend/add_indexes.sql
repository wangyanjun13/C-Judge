-- 性能优化：添加数据库索引
-- 执行此脚本以提升查询性能

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_online ON users(is_online);
CREATE INDEX IF NOT EXISTS idx_users_register_time ON users(register_time);

-- 操作日志表索引
CREATE INDEX IF NOT EXISTS idx_operation_logs_user_id ON operation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_operation_logs_operation ON operation_logs(operation);
CREATE INDEX IF NOT EXISTS idx_operation_logs_user_created ON operation_logs(user_id, created_at);

-- 提交记录表索引（如果存在）
CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_problem_id ON submissions(problem_id);
CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);

-- 题目表索引（如果存在）
CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty);
CREATE INDEX IF NOT EXISTS idx_problems_category ON problems(category);
CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems(created_at);

-- 练习表索引（如果存在）
CREATE INDEX IF NOT EXISTS idx_exercises_teacher_id ON exercises(teacher_id);
CREATE INDEX IF NOT EXISTS idx_exercises_created_at ON exercises(created_at);

-- 分析表统计信息
ANALYZE users;
ANALYZE operation_logs;
ANALYZE submissions;
ANALYZE problems;
ANALYZE exercises;

-- 显示索引创建结果
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('users', 'operation_logs', 'submissions', 'problems', 'exercises')
ORDER BY tablename, indexname;

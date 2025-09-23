-- 检查数据库索引状态 - 简化版本

-- 1. 查看所有索引
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('users', 'operation_logs', 'submissions', 'problems', 'exercises')
ORDER BY tablename, indexname;

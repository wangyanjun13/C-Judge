-- 查看表结构（确认字段名）
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('users', 'operation_logs', 'submissions', 'problems', 'exercises')
ORDER BY table_name, ordinal_position;

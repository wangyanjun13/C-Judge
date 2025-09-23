-- 检查数据库索引状态
-- 查看所有表的索引信息

-- 1. 查看所有索引
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('users', 'operation_logs', 'submissions', 'problems', 'exercises')
ORDER BY tablename, indexname;

-- 2. 查看表结构（确认字段名）
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('users', 'operation_logs', 'submissions', 'problems', 'exercises')
ORDER BY table_name, ordinal_position;

-- 3. 查看索引使用统计
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_tup_read DESC;

-- 4. 查看表大小和索引大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'operation_logs', 'submissions', 'problems', 'exercises')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 5. 检查是否有重复或无效索引
SELECT 
    i.relname as index_name,
    t.relname as table_name,
    a.attname as column_name,
    ix.indisunique as is_unique,
    ix.indisprimary as is_primary
FROM pg_class i
JOIN pg_index ix ON i.oid = ix.indexrelid
JOIN pg_class t ON ix.indrelid = t.oid
JOIN pg_attribute a ON t.oid = a.attrelid AND a.attnum = ANY(ix.indkey)
WHERE t.relname IN ('users', 'operation_logs', 'submissions', 'problems', 'exercises')
ORDER BY t.relname, i.relname;

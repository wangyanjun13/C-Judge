-- 添加缺失的索引

-- submissions 表缺失的索引
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions USING btree (status);
CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON submissions USING btree (submitted_at);
CREATE INDEX IF NOT EXISTS idx_submissions_user_status ON submissions USING btree (user_id, status);
CREATE INDEX IF NOT EXISTS idx_submissions_problem_status ON submissions USING btree (problem_id, status);

-- problems 表缺失的索引（根据init.sql，problems表没有difficulty和is_active字段）
CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems USING btree (created_at);
CREATE INDEX IF NOT EXISTS idx_problems_category ON problems USING btree (category);
CREATE INDEX IF NOT EXISTS idx_problems_is_shared ON problems USING btree (is_shared);

-- exercises 表缺失的索引（根据init.sql，exercises表没有difficulty和is_active字段）
CREATE INDEX IF NOT EXISTS idx_exercises_created_at ON exercises USING btree (created_at);
CREATE INDEX IF NOT EXISTS idx_exercises_start_time ON exercises USING btree (start_time);
CREATE INDEX IF NOT EXISTS idx_exercises_end_time ON exercises USING btree (end_time);

-- users 表缺失的索引（根据init.sql，users表没有last_login和email字段）
-- 已存在的索引：username, role, is_online, register_time

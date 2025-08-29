-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS q3demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE q3demo;

-- 会话表
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('active', 'expired', 'closed') NOT NULL DEFAULT 'active',
    session_data JSON,  -- 存储额外的会话元数据
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_last_activity (last_activity),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 对话轮次表
CREATE TABLE IF NOT EXISTS conversation_turns (
    turn_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_input TEXT NOT NULL,
    intent VARCHAR(50) NOT NULL,
    confidence DECIMAL(4,3) NOT NULL,  -- 存储置信度分数 (0.000-1.000)
    bot_response TEXT NOT NULL,
    slots JSON,  -- 存储提取的实体/槽位
    turn_number INT NOT NULL,  -- 在会话中的轮次编号
    processing_time INT,  -- 处理时间（毫秒）
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    INDEX idx_session_turn (session_id, turn_number),
    INDEX idx_intent (intent),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 意图统计表（用于分析）
CREATE TABLE IF NOT EXISTS intent_analytics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    intent VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    total_occurrences INT NOT NULL DEFAULT 0,
    avg_confidence DECIMAL(4,3) NOT NULL DEFAULT 0.000,
    success_rate DECIMAL(4,3) NOT NULL DEFAULT 0.000,  -- 基于用户反馈或后续对话分析
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_intent_date (intent, date),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 会话统计表（用于分析）
CREATE TABLE IF NOT EXISTS session_analytics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    total_sessions INT NOT NULL DEFAULT 0,
    avg_turns_per_session DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    avg_session_duration INT NOT NULL DEFAULT 0,  -- 秒数
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date (date),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 用户反馈表（可选，用于收集反馈）
CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    turn_id BIGINT,  -- 可以是针对特定轮次的反馈
    feedback_type ENUM('helpful', 'not_helpful', 'incorrect', 'other') NOT NULL,
    feedback_text TEXT,
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (turn_id) REFERENCES conversation_turns(turn_id),
    INDEX idx_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建视图：每日对话统计
CREATE OR REPLACE VIEW daily_conversation_stats AS
SELECT 
    DATE(timestamp) as date,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(*) as total_turns,
    COUNT(*) / COUNT(DISTINCT session_id) as avg_turns_per_session,
    AVG(confidence) as avg_confidence
FROM conversation_turns
GROUP BY DATE(timestamp);

-- 创建视图：意图分布统计
CREATE OR REPLACE VIEW intent_distribution AS
SELECT 
    intent,
    COUNT(*) as total_occurrences,
    AVG(confidence) as avg_confidence,
    COUNT(DISTINCT session_id) as unique_sessions
FROM conversation_turns
GROUP BY intent;

-- 添加初始统计触发器
DELIMITER //

-- 更新意图统计的触发器
CREATE TRIGGER after_turn_insert
AFTER INSERT ON conversation_turns
FOR EACH ROW
BEGIN
    INSERT INTO intent_analytics (intent, date, total_occurrences, avg_confidence)
    VALUES (NEW.intent, DATE(NEW.timestamp), 1, NEW.confidence)
    ON DUPLICATE KEY UPDATE
        total_occurrences = total_occurrences + 1,
        avg_confidence = ((avg_confidence * total_occurrences) + NEW.confidence) / (total_occurrences + 1);
END //

-- 更新会话统计的触发器
CREATE TRIGGER after_session_update
AFTER UPDATE ON sessions
FOR EACH ROW
BEGIN
    IF NEW.status = 'closed' AND OLD.status = 'active' THEN
        INSERT INTO session_analytics (date, total_sessions, avg_turns_per_session, avg_session_duration)
        VALUES (
            DATE(NEW.last_activity), 
            1,
            (SELECT COUNT(*) FROM conversation_turns WHERE session_id = NEW.session_id),
            TIMESTAMPDIFF(SECOND, NEW.created_at, NEW.last_activity)
        )
        ON DUPLICATE KEY UPDATE
            total_sessions = total_sessions + 1,
            avg_turns_per_session = (
                SELECT AVG(turn_count) 
                FROM (
                    SELECT COUNT(*) as turn_count 
                    FROM conversation_turns 
                    WHERE session_id IN (
                        SELECT session_id 
                        FROM sessions 
                        WHERE DATE(last_activity) = DATE(NEW.last_activity)
                    )
                    GROUP BY session_id
                ) t
            ),
            avg_session_duration = (
                SELECT AVG(TIMESTAMPDIFF(SECOND, created_at, last_activity))
                FROM sessions
                WHERE DATE(last_activity) = DATE(NEW.last_activity)
                AND status = 'closed'
            );
    END IF;
END //

DELIMITER ;

-- 添加情感分析和紧急度字段
ALTER TABLE conversation_turns
ADD COLUMN emotion ENUM('positive', 'negative', 'neutral') NOT NULL DEFAULT 'neutral',
ADD COLUMN urgency ENUM('high', 'medium', 'low') NOT NULL DEFAULT 'low';

-- 添加一些基础的测试数据
INSERT INTO sessions (session_id, created_at, last_activity, status)
VALUES ('test-session-1', NOW(), NOW(), 'active');

INSERT INTO conversation_turns 
(session_id, user_input, intent, confidence, bot_response, turn_number)
VALUES 
('test-session-1', 'hello', 'greet', 0.95, 'Hello! How can I help you today?', 1);
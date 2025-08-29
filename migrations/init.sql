-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS q3demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE q3demo;

-- 会话表
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    status ENUM('active', 'expired', 'closed') NOT NULL DEFAULT 'active',
    session_data JSON,  -- 存储额外的会话元数据
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_create_time (create_time),
    INDEX idx_update_time (update_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 对话轮次表
CREATE TABLE IF NOT EXISTS conversation_turns (
    turn_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    user_input TEXT NOT NULL,
    intent VARCHAR(50) NOT NULL,
    confidence DECIMAL(4,3) NOT NULL,  -- 存储置信度分数 (0.000-1.000)
    bot_response TEXT NOT NULL,
    slots JSON,  -- 存储提取的实体/槽位
    turn_number INT NOT NULL,  -- 在会话中的轮次编号
    processing_time INT,  -- 处理时间（毫秒）
    emotion ENUM('positive', 'negative', 'neutral') NOT NULL DEFAULT 'neutral',
    urgency ENUM('high', 'medium', 'low') NOT NULL DEFAULT 'low',
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    INDEX idx_session_turn (session_id, turn_number),
    INDEX idx_intent (intent),
    INDEX idx_create_time (create_time),
    INDEX idx_update_time (update_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 意图统计表（用于分析）
CREATE TABLE IF NOT EXISTS intent_analytics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    intent VARCHAR(50) NOT NULL,
    total_occurrences INT NOT NULL DEFAULT 0,
    avg_confidence DECIMAL(4,3) NOT NULL DEFAULT 0.000,
    success_rate DECIMAL(4,3) NOT NULL DEFAULT 0.000,  -- 基于用户反馈或后续对话分析
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_intent (intent),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 会话统计表（用于分析）
CREATE TABLE IF NOT EXISTS session_analytics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    total_sessions INT NOT NULL DEFAULT 0,
    avg_turns_per_session DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    avg_session_duration INT NOT NULL DEFAULT 0,  -- 秒数
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_create_time (create_time)
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

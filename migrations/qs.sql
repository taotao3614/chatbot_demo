-- 建表：FAQ 问答
CREATE TABLE IF NOT EXISTS faq_qa (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  uuid VARCHAR(36) NOT NULL,                           -- UUID 字符串形式
  category VARCHAR(64) NOT NULL,                        -- 问题分类（如: 账号/支付/发票/技术/合同）
  question TEXT NOT NULL,                               -- 问题
  answer MEDIUMTEXT NOT NULL,                          -- 答案
  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_uuid (uuid),
  KEY idx_category (category),
  FULLTEXT KEY ft_q (question, answer)                  -- 可选：关键词检索（CJK 分词效果有限）
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
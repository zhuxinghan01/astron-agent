-- Create AI prompt template table
CREATE TABLE IF NOT EXISTS ai_prompt_template (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key ID',
    prompt_key VARCHAR(100) NOT NULL COMMENT 'Prompt unique identifier',
    language_code VARCHAR(10) NOT NULL COMMENT 'Language code: zh/en',
    prompt_content TEXT NOT NULL COMMENT 'Prompt template content',
    is_active TINYINT(1) DEFAULT 1 COMMENT 'Is active (0-disabled, 1-enabled)',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',

    UNIQUE KEY uk_prompt_key_lang (prompt_key, language_code),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI prompt template table';
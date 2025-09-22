SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_token_records`;
CREATE TABLE `chat_token_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sid` varchar(64) DEFAULT NULL COMMENT 'Session identifier',
  `prompt_tokens` int DEFAULT NULL COMMENT 'Prompt token count',
  `question_tokens` int DEFAULT NULL COMMENT 'Current question token count',
  `completion_tokens` int DEFAULT NULL COMMENT 'Response completion token count',
  `total_tokens` int DEFAULT NULL COMMENT 'Total token count',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_create_time` (`create_time`),
  KEY `idx_sid` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chat token record table';

SET FOREIGN_KEY_CHECKS = 1;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_bot_list`;
CREATE TABLE `chat_bot_list` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `market_bot_id` int DEFAULT '0' COMMENT 'Market bot ID, if 0 then original, if other value then reference to other user bot',
  `real_bot_id` int DEFAULT '0' COMMENT 'Self-created assistant is 0, only when adding others assistant from market, original bot_id is added',
  `name` varchar(48) DEFAULT NULL COMMENT 'Bot name',
  `bot_type` tinyint DEFAULT '1' COMMENT 'Bot type: 1 Custom Assistant, 2 Life Assistant, 3 Workplace Assistant, 4 Marketing Assistant, 5 Writing Expert, 6 Knowledge Expert',
  `avatar` varchar(1024) DEFAULT NULL COMMENT 'Bot avatar',
  `prompt` varchar(2048) DEFAULT NULL COMMENT 'bot_prompt',
  `bot_desc` varchar(255) DEFAULT NULL COMMENT 'Bot description',
  `is_act` tinyint DEFAULT '1' COMMENT 'Whether enabled: 0 disabled, 1 enabled',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `support_context` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether to support multi-turn conversation: 1 support, 0 not support',
  PRIMARY KEY (`id`),
  KEY `idx_act` (`is_act`),
  KEY `idx_create_time2` (`create_time`),
  KEY `idx_real_bot_id` (`real_bot_id`),
  KEY `idx_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User added assistant table';

SET FOREIGN_KEY_CHECKS = 1;
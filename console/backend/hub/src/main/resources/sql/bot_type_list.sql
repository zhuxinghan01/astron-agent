SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `bot_type_list`;
CREATE TABLE `bot_type_list` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Non-business primary key',
  `type_key` int DEFAULT NULL COMMENT 'Assistant type code',
  `type_name` varchar(255) DEFAULT NULL COMMENT 'Assistant type name',
  `order_num` int DEFAULT '0' COMMENT 'Sort sequence number',
  `show_index` tinyint DEFAULT '0' COMMENT 'Whether recommended: 1 recommended, 0 not recommended',
  `is_act` tinyint DEFAULT '1' COMMENT 'Enable status: 0 disabled, 1 enabled',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `icon` varchar(500) DEFAULT '' COMMENT 'Icon URL',
  `type_name_en` varchar(128) DEFAULT NULL COMMENT 'Assistant type English name',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Assistant type mapping table';

SET FOREIGN_KEY_CHECKS = 1;
SET NAMES utf8mb4;
SET
FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `bot_favorite`;
CREATE TABLE `bot_favorite`
(
    `id`          bigint(20) NOT NULL AUTO_INCREMENT,
    `uid`         varchar(128) NOT NULL,
    `bot_id`      int(11) NOT NULL,
    `create_time` datetime DEFAULT NULL,
    `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY           `idx_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Assistant favorites';

SET
FOREIGN_KEY_CHECKS = 1;

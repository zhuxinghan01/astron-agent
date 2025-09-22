CREATE TABLE `user_lang_chain_info`
(
    `id`          bigint NOT NULL AUTO_INCREMENT COMMENT 'Non-business primary key',
    `bot_id`      int  NOT NULL COMMENT 'Agent ID',
    `name`        varchar(255) DEFAULT NULL COMMENT 'LangChain name',
    `desc`        text COMMENT 'Agent description',
    `open`        json COMMENT 'Open configuration information, including nodes and edges',
    `gcy`         json COMMENT 'GCY configuration information, including virtual nodes and edges',
    `uid`         varchar(255) NOT NULL COMMENT 'User ID',
    `flow_id`     varchar(64) DEFAULT NULL COMMENT 'Flow ID',
    `maas_id`     bigint DEFAULT NULL COMMENT 'Group ID',
    `bot_name`    varchar(255) DEFAULT NULL COMMENT 'Agent name',
    `extra_inputs` json COMMENT 'Extra input items',
    `extra_inputs_config` json COMMENT 'Multi-file parameters',
    `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
    `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
    PRIMARY KEY (`id`),
    KEY           `idx_bot_id` (`bot_id`),
    KEY           `idx_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Workflow configuration table';
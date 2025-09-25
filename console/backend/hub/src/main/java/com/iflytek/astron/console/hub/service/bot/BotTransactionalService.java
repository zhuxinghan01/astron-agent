package com.iflytek.astron.console.hub.service.bot;


import jakarta.servlet.http.HttpServletRequest;

/**
 * @author cczhu10
 * @date 2025-06-30
 * @description 助手事务操作 在service中直接使用自身会导致aop失效从而导致事务失败
 */
public interface BotTransactionalService {
    void copyBot(String uid, Integer botId, HttpServletRequest request, Long spaceId);
}

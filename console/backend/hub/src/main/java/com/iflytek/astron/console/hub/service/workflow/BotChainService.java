package com.iflytek.astron.console.hub.service.workflow;

import jakarta.servlet.http.HttpServletRequest;

/**
 * @author minguiyongheng
 */
public interface BotChainService {

    /**
     * 复制助手2.0
     */
    void copyBot(String uid, Long sourceId, Long targetId, Long spaceId);

    /**
     * 复制工作流
     *
     * @param uid uid
     * @param spaceId
     */
    void cloneWorkFlow(String uid, Long sourceId, Long targetId, HttpServletRequest request, Long spaceId);
}

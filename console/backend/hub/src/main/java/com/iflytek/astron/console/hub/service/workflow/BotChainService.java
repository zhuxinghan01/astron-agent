package com.iflytek.astron.console.hub.service.workflow;

import jakarta.servlet.http.HttpServletRequest;

/**
 * @author minguiyongheng
 */
public interface BotChainService {

    /**
     * Copy assistant 2.0
     */
    void copyBot(String uid, Long sourceId, Long targetId, Long spaceId);

    /**
     * Copy workflow
     */
    void cloneWorkFlow(String uid, Long sourceId, Long targetId, HttpServletRequest request, Long spaceId);
}

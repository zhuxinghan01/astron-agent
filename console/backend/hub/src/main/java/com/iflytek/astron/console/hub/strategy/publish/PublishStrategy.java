package com.iflytek.astron.console.hub.strategy.publish;

import com.iflytek.astron.console.commons.response.ApiResult;

/**
 * Publish strategy interface for different publish types
 * Each publish type (MARKET, MCP, WECHAT, API, FEISHU) should implement this interface
 */
public interface PublishStrategy {

    /**
     * Publish bot to specific channel
     *
     * @param botId Bot ID
     * @param publishData Publish data specific to the channel
     * @param currentUid Current user ID
     * @param spaceId Space ID
     * @return Publish result
     */
    ApiResult<String> publish(Integer botId, Object publishData, String currentUid, Long spaceId);

    /**
     * Offline bot from specific channel
     *
     * @param botId Bot ID
     * @param publishData Offline data specific to the channel
     * @param currentUid Current user ID
     * @param spaceId Space ID
     * @return Offline result
     */
    ApiResult<String> offline(Integer botId, Object publishData, String currentUid, Long spaceId);

    /**
     * Get supported publish type
     *
     * @return Publish type name
     */
    String getPublishType();
}

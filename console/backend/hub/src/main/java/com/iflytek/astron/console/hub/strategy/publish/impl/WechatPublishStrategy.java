package com.iflytek.astron.console.hub.strategy.publish.impl;

import com.iflytek.astron.console.commons.enums.PublishChannelEnum;
import com.iflytek.astron.console.commons.enums.bot.BotPublishTypeEnum;
import com.iflytek.astron.console.commons.response.ApiResult;
import com.iflytek.astron.console.hub.service.publish.BotPublishService;
import com.iflytek.astron.console.hub.service.wechat.BotOffiaccountService;
import com.iflytek.astron.console.hub.strategy.publish.PublishStrategy;
import com.alibaba.fastjson2.JSON;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * WeChat publish strategy implementation
 * Handles bot publishing to WeChat official account channel
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class WechatPublishStrategy implements PublishStrategy {

    private final BotOffiaccountService botOffiaccountService;
    private final BotPublishService botPublishService;

    @Override
    public ApiResult<String> publish(Integer botId, Object publishData, String currentUid, Long spaceId) {
        log.info("Publishing bot to WeChat: botId={}, currentUid={}, spaceId={}", botId, currentUid, spaceId);
        
        try {
            // Parse WeChat publish data
            WechatPublishData wechatData = parsePublishData(publishData);
            
            log.debug("WeChat publish data: appId={}", wechatData.getAppId());
            
            // 1. Bind bot to WeChat official account
            botOffiaccountService.bind(botId, wechatData.getAppId(), currentUid);
            
            // 2. Update publish channel to include WeChat
            botPublishService.updatePublishChannel(botId, currentUid, spaceId, PublishChannelEnum.WECHAT, true);
            
            log.info("WeChat publish completed successfully: botId={}, appId={}", botId, wechatData.getAppId());
            return ApiResult.success("Bot published to WeChat successfully");
            
        } catch (Exception e) {
            log.error("WeChat publish failed: botId={}, error={}", botId, e.getMessage(), e);
            throw e; // Let the controller handle the exception and convert to ApiResult
        }
    }

    @Override
    public ApiResult<String> offline(Integer botId, Object publishData, String currentUid, Long spaceId) {
        log.info("Offlining bot from WeChat: botId={}, currentUid={}, spaceId={}", botId, currentUid, spaceId);
        
        try {
            // 1. Unbind bot from WeChat official account  
            // Note: unbind method takes appId, need to get it first or modify the service method
            // For now, we'll update publish channel only
            // TODO: Enhance unbind logic to get appId from botId
            
            // 2. Update publish channel to remove WeChat
            botPublishService.updatePublishChannel(botId, currentUid, spaceId, PublishChannelEnum.WECHAT, false);
            
            log.info("WeChat offline completed successfully: botId={}", botId);
            return ApiResult.success("Bot removed from WeChat successfully");
            
        } catch (Exception e) {
            log.error("WeChat offline failed: botId={}, error={}", botId, e.getMessage(), e);
            throw e; // Let the controller handle the exception and convert to ApiResult
        }
    }

    @Override
    public String getPublishType() {
        return BotPublishTypeEnum.WECHAT.getCode();
    }

    /**
     * Parse publish data to WeChat configuration
     */
    private WechatPublishData parsePublishData(Object publishData) {
        if (publishData == null) {
            throw new IllegalArgumentException("WeChat publish data cannot be null");
        }

        try {
            WechatPublishData wechatData;
            
            if (publishData instanceof WechatPublishData) {
                wechatData = (WechatPublishData) publishData;
            } else {
                // Try to parse from JSON
                String jsonData = JSON.toJSONString(publishData);
                wechatData = JSON.parseObject(jsonData, WechatPublishData.class);
            }
            
            // Validate required fields
            if (wechatData.getAppId() == null || wechatData.getAppId().trim().isEmpty()) {
                throw new IllegalArgumentException("WeChat appId is required");
            }
            
            return wechatData;
            
        } catch (Exception e) {
            log.error("Failed to parse WeChat publish data: data={}", publishData, e);
            throw new IllegalArgumentException("Invalid WeChat publish data format", e);
        }
    }

    /**
     * WeChat publish data structure
     */
    public static class WechatPublishData {
        private String appId;
        private String menuConfig; // Optional menu configuration
        
        public String getAppId() {
            return appId;
        }
        
        public void setAppId(String appId) {
            this.appId = appId;
        }
        
        public String getMenuConfig() {
            return menuConfig;
        }
        
        public void setMenuConfig(String menuConfig) {
            this.menuConfig = menuConfig;
        }
    }
}

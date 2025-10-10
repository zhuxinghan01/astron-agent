package com.iflytek.astron.console.hub.strategy.publish.impl;

import com.iflytek.astron.console.commons.enums.bot.BotPublishTypeEnum;
import com.iflytek.astron.console.commons.enums.PublishChannelEnum;
import com.iflytek.astron.console.commons.enums.ShelfStatusEnum;
import com.iflytek.astron.console.commons.response.ApiResult;
import com.iflytek.astron.console.commons.mapper.bot.ChatBotMarketMapper;
import com.iflytek.astron.console.commons.mapper.bot.ChatBotBaseMapper;
import com.iflytek.astron.console.commons.entity.bot.BotPublishQueryResult;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.hub.service.publish.PublishChannelService;
import com.iflytek.astron.console.hub.strategy.publish.PublishStrategy;
import com.iflytek.astron.console.hub.event.BotPublishStatusChangedEvent;
import com.alibaba.fastjson2.JSON;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;

/**
 * Market publish strategy implementation
 * Handles bot publishing to market channel using event-driven architecture
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class MarketPublishStrategy implements PublishStrategy {

    private final ChatBotBaseMapper chatBotBaseMapper;
    private final ChatBotMarketMapper chatBotMarketMapper;
    private final PublishChannelService publishChannelService;
    private final ApplicationEventPublisher eventPublisher;

    @Override
    public ApiResult<Object> publish(Integer botId, Object publishData, String currentUid, Long spaceId) {
        log.info("Publishing bot to market: botId={}, currentUid={}, spaceId={}", botId, currentUid, spaceId);
        
        try {
            // 1. Validate bot permission
            int hasPermission = chatBotBaseMapper.checkBotPermission(botId, currentUid, spaceId);
            if (hasPermission == 0) {
                throw new BusinessException(ResponseEnum.BOT_NOT_EXISTS);
            }

            // 2. Query current publish status
            BotPublishQueryResult queryResult = chatBotMarketMapper.selectBotDetail(botId, currentUid, spaceId);
            Integer currentStatus = queryResult != null ? queryResult.getBotStatus() : null;
            String currentChannels = queryResult != null ? queryResult.getPublishChannels() : null;

            // 3. Calculate new status and channels
            Integer effectiveStatus = currentStatus != null ? currentStatus : ShelfStatusEnum.OFF_SHELF.getCode();

            if (ShelfStatusEnum.isOnShelf(effectiveStatus)) {
                log.warn("Bot already published, no need to repeat operation: botId={}", botId);
                return ApiResult.success(null);
            }

            if (!ShelfStatusEnum.isOffShelf(effectiveStatus)) {
                throw new BusinessException(ResponseEnum.BOT_STATUS_NOT_ALLOW_PUBLISH);
            }

            Integer newStatus = ShelfStatusEnum.ON_SHELF.getCode();
            String newChannels = publishChannelService.updatePublishChannels(
                    currentChannels, PublishChannelEnum.MARKET.getCode(), true);

            // 4. Parse market-specific publish data
            if (publishData != null) {
                log.debug("Market publish data: {}", JSON.toJSONString(publishData));
                // TODO: Parse market-specific data like category, tags, visibility settings
            }

            // 5. Publish event to trigger database operations
            eventPublisher.publishEvent(new BotPublishStatusChangedEvent(
                    this, botId, currentUid, spaceId, "PUBLISH",
                    currentStatus, newStatus, newChannels));
            
            log.info("Market publish completed successfully: botId={}", botId);
            return ApiResult.success(null);
                
        } catch (Exception e) {
            log.error("Market publish failed: botId={}, error={}", botId, e.getMessage(), e);
            throw e;
        }
    }

    @Override
    public ApiResult<Object> offline(Integer botId, Object publishData, String currentUid, Long spaceId) {
        log.info("Offlining bot from market: botId={}, currentUid={}, spaceId={}", botId, currentUid, spaceId);
        
        try {
            // 1. Validate bot permission
            int hasPermission = chatBotBaseMapper.checkBotPermission(botId, currentUid, spaceId);
            if (hasPermission == 0) {
                throw new BusinessException(ResponseEnum.BOT_NOT_EXISTS);
            }

            // 2. Query current publish status
            BotPublishQueryResult queryResult = chatBotMarketMapper.selectBotDetail(botId, currentUid, spaceId);
            Integer currentStatus = queryResult != null ? queryResult.getBotStatus() : null;
            String currentChannels = queryResult != null ? queryResult.getPublishChannels() : null;

            // 3. Validate offline conditions
            if (currentStatus == null || !ShelfStatusEnum.isOnShelf(currentStatus)) {
                throw new BusinessException(ResponseEnum.BOT_STATUS_NOT_ALLOW_OFFLINE);
            }

            Integer newStatus = ShelfStatusEnum.OFF_SHELF.getCode();
            String newChannels = publishChannelService.updatePublishChannels(
                    currentChannels, PublishChannelEnum.MARKET.getCode(), false);

            // 4. Publish event to trigger database operations
            eventPublisher.publishEvent(new BotPublishStatusChangedEvent(
                    this, botId, currentUid, spaceId, "OFFLINE",
                    currentStatus, newStatus, newChannels));
            
           log.info("Market offline completed successfully: botId={}", botId);
           return ApiResult.success(null);
            
        } catch (Exception e) {
            log.error("Market offline failed: botId={}, error={}", botId, e.getMessage(), e);
            throw e;
        }
    }

    @Override
    public String getPublishType() {
        return BotPublishTypeEnum.MARKET.getCode();
    }
}

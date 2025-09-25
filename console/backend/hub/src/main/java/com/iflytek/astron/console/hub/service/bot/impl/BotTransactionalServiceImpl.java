package com.iflytek.astron.console.hub.service.bot.impl;

import com.iflytek.astron.console.commons.entity.bot.ChatBotBase;
import com.iflytek.astron.console.commons.service.bot.BotService;
import com.iflytek.astron.console.commons.util.MaasUtil;
import com.iflytek.astron.console.hub.service.bot.BotTransactionalService;
import com.iflytek.astron.console.hub.service.workflow.BotChainService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RedissonClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;

/**
 * @author cczhu10
 * @date 2025-06-30
 * @description
 */
@Service
@Slf4j
public class BotTransactionalServiceImpl implements BotTransactionalService {

    @Autowired
    private BotService botService;

    @Autowired
    private BotChainService botChainService;

    @Autowired
    private RedissonClient redissonClient;

    @Transactional(rollbackFor = Exception.class)
    @Override
    public void copyBot(String uid, Integer botId, HttpServletRequest request, Long spaceId) {
        ChatBotBase base = botService.copyBot(uid, botId, spaceId);
        // 新助手的botId就是target id
        Long targetId = Long.valueOf(base.getId());
        if (base.getVersion() == 2) {
            botChainService.copyBot(uid, Long.valueOf(botId), targetId, spaceId);
        } else if (base.getVersion() == 3) {
            // 创建一个事件,在 /massCopySynchronize被消费
            redissonClient.getBucket(MaasUtil.generatePrefix(uid, botId)).set(String.valueOf(botId));
            redissonClient.getBucket(MaasUtil.generatePrefix(uid, botId)).expire(Duration.ofSeconds(60));
            // 同步星辰 MASS
            botChainService.cloneWorkFlow(uid, Long.valueOf(botId), targetId, request, spaceId);
        }
    }
}

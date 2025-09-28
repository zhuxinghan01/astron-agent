package com.iflytek.astron.console.hub.service.workflow.impl;

import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.entity.bot.UserLangChainInfo;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.service.data.UserLangChainDataService;
import com.iflytek.astron.console.commons.util.MaasUtil;
import com.iflytek.astron.console.hub.service.workflow.BotChainService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@Slf4j
public class BotChainServiceImpl implements BotChainService {

    @Autowired
    private UserLangChainDataService userLangChainDataService;

    @Autowired
    private MaasUtil maasUtil;

    /**
     * 复制助手2.0
     *
     * @param uid
     * @param sourceId
     * @param targetId
     * @param spaceId
     */
    @Override
    public void copyBot(String uid, Long sourceId, Long targetId, Long spaceId) {
        // 查源助手
        List<UserLangChainInfo> botList = userLangChainDataService.findListByBotId(Math.toIntExact(sourceId));
        if (Objects.isNull(botList) || botList.isEmpty()) {
            log.info("***** source助手不存在, id: {}", sourceId);
            return;
        }

        UserLangChainInfo chainInfo = botList.getFirst();
        // 把节点id 换掉，防止数据回流错乱
        replaceNodeId(chainInfo);
        // 配置 _id, id, botId, flowId, uid, updateTime
        chainInfo.setId(null);
        chainInfo.setBotId(Math.toIntExact(targetId));
        chainInfo.setFlowId(null);
        if (null == spaceId) {
            chainInfo.setUid(uid);
        } else {
            chainInfo.setSpaceId(spaceId);
        }
        chainInfo.setUpdateTime(LocalDateTime.now());

        // 添加新json
        userLangChainDataService.insertUserLangChainInfo(chainInfo);
    }

    /**
     * 复制工作流
     *
     * @param uid uid
     * @param sourceId
     * @param targetId
     * @param request
     * @param spaceId
     */
    @Override
    @Transactional
    public void cloneWorkFlow(String uid, Long sourceId, Long targetId, HttpServletRequest request, Long spaceId) {
        // 查源助手
        List<UserLangChainInfo> botList = userLangChainDataService.findListByBotId(Math.toIntExact(sourceId));
        if (Objects.isNull(botList) || botList.isEmpty()) {
            log.info("***** source助手不存在, id: {}", sourceId);
            return;
        }

        UserLangChainInfo chainInfo = botList.getFirst();
        Long massId = Long.valueOf(String.valueOf(chainInfo.getMaasId()));
        JSONObject res = maasUtil.copyWorkFlow(massId, uid);
        if (Objects.isNull(res)) {
            // 抛出异常,保持数据的事务性
            throw new BusinessException(ResponseEnum.BOT_CHAIN_UPDATE_ERROR);
        }
        JSONObject data = res.getJSONObject("data");
        Long currentMass = data.getLong("id");
        String flowId = data.getString("flowId");
        UserLangChainInfo chain = new UserLangChainInfo();
        chain.setBotId(Math.toIntExact(targetId));
        chain.setMaasId(currentMass);
        chain.setFlowId(flowId);
        if (null == spaceId) {
            chain.setUid(uid);
        } else {
            chain.setSpaceId(spaceId);
        }
        chain.setUpdateTime(LocalDateTime.now());
        userLangChainDataService.insertUserLangChainInfo(chain);
        log.info("----- 源助手: {}, 目标助手: {} 得到的新画布id: {}, flowId: {}", sourceId, targetId, currentMass, flowId);
    }

    public static void replaceNodeId(UserLangChainInfo botMap) {
        JSONObject open = JSONObject.parseObject(botMap.getOpen());
        String openStr = botMap.getOpen();
        String gcyStr = botMap.getGcy();

        JSONArray nodes = open.getJSONArray("nodes");
        for (Object o : nodes) {
            JSONObject node = (JSONObject) o;
            String oldNodeId = node.getString("id");
            String newNodeId = getNewNodeId(oldNodeId);
            // 直接匹配字符串并替换
            openStr = openStr.replace(oldNodeId, newNodeId);
            gcyStr = gcyStr.replace(oldNodeId, newNodeId);
        }
        botMap.setOpen(openStr);
        botMap.setGcy(gcyStr);
    }

    public static String getNewNodeId(String original) {
        int colonIndex = original.indexOf(':');
        if (colonIndex != -1) {
            return original.substring(0, colonIndex + 1) + UUID.randomUUID();
        }
        // 如果没有找到冒号，则返回原始字符串
        log.info("***** {}没有找到冒号", original);
        throw new RuntimeException("助手后台数据不符合规范");
    }
}

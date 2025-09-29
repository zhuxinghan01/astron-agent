package com.iflytek.astron.console.hub.service.publish.impl;

import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.entity.bot.ChatBotBase;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.service.bot.ChatBotDataService;
import com.iflytek.astron.console.commons.service.space.SpaceService;
import com.iflytek.astron.console.commons.service.user.AppMstService;
import com.iflytek.astron.console.commons.util.RequestContextUtil;
import com.iflytek.astron.console.commons.util.space.SpaceInfoUtil;
import com.iflytek.astron.console.hub.dto.publish.AppListDTO;
import com.iflytek.astron.console.hub.dto.publish.BotApiInfoDTO;
import com.iflytek.astron.console.hub.dto.publish.CreateAppVo;
import com.iflytek.astron.console.hub.dto.publish.CreateBotApiVo;
import com.iflytek.astron.console.hub.dto.user.TenantAuth;
import com.iflytek.astron.console.hub.enums.BotVersionEnum;
import com.iflytek.astron.console.hub.service.chat.ChatBotApiService;
import com.iflytek.astron.console.hub.service.publish.PublishApiService;
import com.iflytek.astron.console.hub.service.publish.TenantService;
import com.iflytek.astron.console.toolkit.util.RedisUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * @author yun-zhi-ztl
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PublishApiServiceImpl implements PublishApiService {

    @Autowired
    private AppMstService appMstService;

    @Autowired
    private TenantService tenantService;

    @Autowired
    private RedisUtil redisUtil;

    @Autowired
    private SpaceService spaceService;

    @Autowired
    private ChatBotDataService chatBotDataService;

    @Autowired
    private ChatBotApiService chatBotApiService;

    private static final String PUBLISH_API = "publish_api";

    @Override
    public Boolean createApp(CreateAppVo createAppVo) {
        String uid = RequestContextUtil.getUID();

        if (appMstService.exist(createAppVo.getAppName())) {
            throw new BusinessException(ResponseEnum.USER_APP_NAME_REPEAT);
        }

        String appId = tenantService.createApp(uid, createAppVo.getAppName(), createAppVo.getAppDescribe());
        if (appId == null) {
            throw new BusinessException(ResponseEnum.USER_APP_ID_CREATE_ERROR);
        }
        TenantAuth tenantAuth = tenantService.getAppDetail(appId);
        if (tenantAuth == null) {
            throw new BusinessException(ResponseEnum.USER_APP_ID_CREATE_ERROR);
        }
        appMstService.insert(uid, appId, createAppVo.getAppName(), createAppVo.getAppDescribe(), tenantAuth.getApiKey(), tenantAuth.getApiSecret());

        return true;
    }

    @Override
    public List<AppListDTO> getAppList() {
        String uid = RequestContextUtil.getUID();
        return appMstService.getAppListByUid(uid)
                .stream()
                .map(appMst -> new AppListDTO(appMst.getAppId(), appMst.getAppName(), appMst.getAppDescribe()))
                .collect(Collectors.toList());
    }

    @Override
    public BotApiInfoDTO createBotApi(CreateBotApiVo createBotApiVo) {
        String uid = RequestContextUtil.getUID();
        String uuid = UUID.randomUUID().toString();
        String teamCreateUid = SpaceInfoUtil.getUidByCurrentSpaceId();
        // Only the space creator can publish APIs
        if (!uid.equals(teamCreateUid)) {
            throw new BusinessException(ResponseEnum.USER_NO_APPROVEL);
        }
        if (!redisUtil.tryLock(PUBLISH_API + uid, 3000, uuid)) {
            throw new BusinessException(ResponseEnum.BOT_API_CREATE_LIMIT_ERROR);
        }

        ChatBotBase botBase = chatBotDataService.findOne(uid, createBotApiVo.getBotId());
        if (botBase == null) {
            throw new BusinessException(ResponseEnum.BOT_NOT_EXISTS);
        }

        if (chatBotApiService.exists(createBotApiVo.getBotId()) &&
                !botBase.getVersion().equals(BotVersionEnum.WORKFLOW.getVersion())) {
            throw new BusinessException(ResponseEnum.BOT_API_CREATE_REPEAT);
        }


        return null;
    }
}

package com.iflytek.astron.console.hub.service.publish.impl;

import cn.hutool.core.util.StrUtil;
import com.alibaba.fastjson2.JSONObject;
import com.iflytek.astron.console.commons.enums.bot.ReleaseTypeEnum;
import com.iflytek.astron.console.commons.service.data.UserLangChainDataService;
import com.iflytek.astron.console.commons.util.MaasUtil;
import com.iflytek.astron.console.hub.service.publish.ReleaseManageClientService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

/**
 * @author yun-zhi-ztl
 */
@Service
@Slf4j
public class ReleaseManageClientServiceImpl implements ReleaseManageClientService {
    @Value("${mass.workflowVersion}")
    private String BASE_URL;
    @Autowired
    private UserLangChainDataService userLangChainDataService;

    @Autowired
    private MaasUtil maasUtil;

    private static final String GET_VERSION_NAME_URL = "/getVersionName";

    private static final String RELEASE_SUCCESS = "SUCCESS";

    private static final OkHttpClient HTTP_CLIENT = new OkHttpClient().newBuilder()
            .connectionPool(new ConnectionPool(100, 5, TimeUnit.MINUTES))
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build();

    @Override
    public String getVersionNameByBotId(Long botId, Long spaceId, HttpServletRequest request) {
        String flowId = userLangChainDataService.findFlowIdByBotId(botId.intValue());
        if (StrUtil.isBlank(flowId)) {
            log.error("getVersionNameByBotId-根据botId获取flowId失败，botId={}", botId);
            return null;
        }
        return getVersionName(flowId, spaceId, request);
    }

    @Override
    public void releaseBotApi(Integer botId, String flowId, String versionName, Long spaceId, HttpServletRequest request) {
        releaseBot(botId.toString(), flowId, ReleaseTypeEnum.BOT_API.getCode(), RELEASE_SUCCESS, "", versionName, spaceId, request);
    }

    private void releaseBot(String botId, String flowId, Integer channel, String result,
                            String desc, String versionName, Long spaceId, HttpServletRequest request) {
    }

    private String getVersionName(String flowId, Long spaceId, HttpServletRequest request) {
        FormBody formBody = new FormBody.Builder()
                .add("flowId", flowId)
                .build();
        Request.Builder builder = new Request.Builder()
                .url(BASE_URL + GET_VERSION_NAME_URL)
                .addHeader("Authorization", MaasUtil.getAuthorizationHeader(request));
        if (spaceId != null) {
            builder.addHeader("space-id", spaceId.toString());
        }
        Request versionRequest = builder.post(formBody).build();

        try (Response response = HTTP_CLIENT.newCall(versionRequest).execute()) {
            if (!response.isSuccessful() || response.body() == null) {
                log.error("Failed to fetch version name - HTTP status: {}", response.code());
                return null;
            }
            JSONObject responseJson = JSONObject.parseObject(response.body().string());
            log.debug("API Response: {}", responseJson);
            if (responseJson.containsKey("data") && responseJson.getJSONObject("data").containsKey("workflowVersionName")) {
                return responseJson.getJSONObject("data").getString("workflowVersionName");
            }
            log.error("Missing expected fields in response for flowId: {}", flowId);
            return null;
        } catch (IOException e) {
            log.error("Exception occurred while getting version name for flowId={}, error={}", flowId, e.getMessage(), e);
            return null;
        }
    }
}

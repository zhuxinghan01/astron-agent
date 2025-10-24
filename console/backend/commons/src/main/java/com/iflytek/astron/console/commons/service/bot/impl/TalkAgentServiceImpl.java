package com.iflytek.astron.console.commons.service.bot.impl;

import com.iflytek.astron.console.commons.service.bot.TalkAgentService;
import com.iflytek.astron.console.commons.util.AuthStringUtil;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class TalkAgentServiceImpl implements TalkAgentService {
    @Value("${spark.api-key}")
    private String apiKey;
    @Value("${spark.api-secret}")
    private String apiSecret;
    private static final String SIGNATURE_URL = "wss://avatar.cn-huadong-1.xf-yun.com/v1/interact";

    @Override
    public String getSignature() {
        return AuthStringUtil.assembleRequestUrl(SIGNATURE_URL,apiKey, apiSecret,"GET");
    }
}

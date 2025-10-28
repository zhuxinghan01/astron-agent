package com.iflytek.astron.console.commons.util;

import cn.hutool.core.collection.ListUtil;
import cn.hutool.core.util.ObjectUtil;
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.dto.bot.*;
import com.iflytek.astron.console.commons.dto.workflow.MaasApi;
import com.iflytek.astron.console.commons.entity.bot.ChatBotBase;
import com.iflytek.astron.console.commons.entity.bot.ChatBotTag;
import com.iflytek.astron.console.commons.entity.bot.UserLangChainInfo;
import com.iflytek.astron.console.commons.enums.bot.BotUploadEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.mapper.bot.ChatBotBaseMapper;
import com.iflytek.astron.console.commons.service.bot.ChatBotTagService;
import com.iflytek.astron.console.commons.service.data.UserLangChainDataService;
import com.iflytek.astron.console.commons.service.workflow.impl.WorkflowBotParamServiceImpl;
import com.iflytek.astron.console.commons.util.space.SpaceInfoUtil;
import jakarta.annotation.Resource;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.apache.commons.lang3.StringUtils;
import org.redisson.api.RedissonClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.time.Duration;
import java.util.*;
import java.util.stream.Collectors;


@Slf4j
@Service
public class MaasUtil {
    private static final OkHttpClient HTTP_CLIENT = new OkHttpClient.Builder()
            .connectTimeout(Duration.ofSeconds(10))
            .readTimeout(Duration.ofSeconds(30))
            .writeTimeout(Duration.ofSeconds(30))
            .retryOnConnectionFailure(true)
            .build();

    @Resource
    private ChatBotBaseMapper chatBotBaseMapper;

    @Value("${maas.synchronizeWorkFlow}")
    private String synchronizeUrl;

    @Value("${maas.cloneWorkFlow}")
    private String cloneWorkFlowUrl;

    @Value("${maas.getInputs}")
    private String getInputsUrl;

    @Value("${maas.appId}")
    private String maasAppId;

    @Value("${maas.consumerId}")
    private String consumerId;

    @Value("${maas.consumerSecret}")
    private String consumerSecret;

    @Value("${maas.consumerKey}")
    private String consumerKey;

    @Value("${maas.publishApi}")
    private String publishApi;

    @Value("${maas.authApi}")
    private String authApi;

    @Value("${maas.mcpHost}")
    private String mcpHost;

    @Value("${maas.mcpRegister}")
    private String mcpReleaseUrl;

    @Autowired
    private UserLangChainDataService userLangChainDataService;

    @Autowired
    private ChatBotTagService chatBotTagService;

    @Autowired
    private RedissonClient redissonClient;

    public static final String PREFIX_MAAS_COPY = "maas_copy_";
    private static final String BOT_TAG_LIST = "bot_tag_list";
    private static final String AUTHORIZATION_HEADER = "Authorization";
    private static final String X_AUTH_SOURCE_HEADER = "x-auth-source";
    private static final String X_AUTH_SOURCE_VALUE = "xfyun";

    private final OkHttpClient client = new OkHttpClient();

    public static final List<String> NO_SUPPORT_TYPE = ListUtil.of("string", "integer", "boolean", "number",
            "object", "array-string", "array-integer",
            "array-boolean", "array-number", "array-object");

    public JSONObject deleteSynchronize(Integer botId, Long spaceId, HttpServletRequest request) {
        if (botId == null || spaceId == null || request == null) {
            log.error("Parameters cannot be null: botId={}, spaceId={}, request={}", botId, spaceId, request);
            return new JSONObject();
        }

        ChatBotBase base = chatBotBaseMapper.selectById(botId);
        if (base == null || 3 != base.getVersion()) {
            return new JSONObject();
        }

        List<UserLangChainInfo> botInfo = userLangChainDataService.findListByBotId(botId);
        if (Objects.isNull(botInfo) || botInfo.isEmpty()) {
            return new JSONObject();
        }

        UserLangChainInfo firstInfo = botInfo.get(0);
        if (firstInfo.getMaasId() == null) {
            log.error("MaasId is null, botId: {}", botId);
            return new JSONObject();
        }

        String maasId = String.valueOf(firstInfo.getMaasId());
        String authHeader = getAuthorizationHeader(request);

        // Build form data
        FormBody formBody = new FormBody.Builder()
                .add("id", maasId)
                .add("spaceId", String.valueOf(spaceId))
                .build();

        // Build request
        Request deleteRequest = new Request.Builder()
                .url(synchronizeUrl)
                .delete(formBody)
                .addHeader("Authorization", authHeader)
                .addHeader(X_AUTH_SOURCE_HEADER, X_AUTH_SOURCE_VALUE)
                .build();

        String response;
        try (Response httpResponse = HTTP_CLIENT.newCall(deleteRequest).execute()) {
            ResponseBody responseBody = httpResponse.body();
            if (responseBody != null) {
                response = responseBody.string();
            } else {
                log.error("Delete maas workflow request response is empty");
                return new JSONObject();
            }
        } catch (IOException e) {
            log.error("Delete maas workflow request failed: {}", e.getMessage());
            return new JSONObject();
        }
        JSONObject res = JSON.parseObject(response);
        if (res.getInteger("code") != 0) {
            log.info("------ Delete maas workflow failed, reason: {}", response);
            return new JSONObject();
        }
        return res;

    }

    public JSONObject synchronizeWorkFlow(UserLangChainInfo userLangChainInfo, BotCreateForm botCreateForm,
            HttpServletRequest request, Long spaceId, Integer version, TalkAgentConfigDto talkAgentConfig) {
        AdvancedConfig advancedConfig = new AdvancedConfig(botCreateForm.getPrologue(), botCreateForm.getInputExample(), botCreateForm.getAppBackground());
        JSONObject param = new JSONObject();
        param.put("avatarIcon", botCreateForm.getAvatar());
        param.put("avatarColor", "");
        param.put("description", botCreateForm.getBotDesc());
        param.put("advancedConfig", advancedConfig);
        param.put("appId", maasAppId);
        param.put("domain", "generalv3.5");
        param.put("name", botCreateForm.getName());
        param.put("spaceId", spaceId);
        JSONObject ext = new JSONObject();
        ext.put("botId", botCreateForm.getBotId());
        param.put("ext", ext);
        param.put("flowType", version);
        if (Objects.nonNull(talkAgentConfig)) {
            param.put("flowConfig", talkAgentConfig);
        }
        if (botCreateForm.getBotType() != 0) {
            param.put("category", botCreateForm.getBotType());
        }


        String authHeader = getAuthorizationHeader(request);

        // Not empty, use PUT request for update
        String httpMethod;
        if (Objects.nonNull(userLangChainInfo)) {
            Long maasId = userLangChainInfo.getMaasId();
            param.put("id", maasId);
            param.put("flowId", userLangChainInfo.getFlowId());
            httpMethod = "PUT";
            redissonClient.getBucket(generatePrefix(maasId.toString(), botCreateForm.getBotId())).set(maasId, Duration.ofSeconds(60));
        } else {
            // If it's newly created, then it's empty, use POST request
            httpMethod = "POST";
        }
        log.info("----- maas synchronization request body: {}", JSONObject.toJSONString(param));

        // Build request body
        RequestBody requestBody = RequestBody.create(
                JSONObject.toJSONString(param),
                MediaType.parse("application/json; charset=utf-8"));

        // Build request
        Request.Builder requestBuilder = new Request.Builder()
                .url(synchronizeUrl)
                .addHeader("Authorization", authHeader)
                .addHeader(X_AUTH_SOURCE_HEADER, X_AUTH_SOURCE_VALUE)
                .addHeader("Lang-Code", I18nUtil.getLanguage());

        if ("PUT".equals(httpMethod)) {
            requestBuilder.put(requestBody);
        } else {
            requestBuilder.post(requestBody);
        }

        Request synchronizeRequest = requestBuilder.build();

        String response;
        try (Response httpResponse = HTTP_CLIENT.newCall(synchronizeRequest).execute()) {
            ResponseBody responseBody = httpResponse.body();
            if (responseBody != null) {
                response = responseBody.string();
            } else {
                log.error("Synchronize maas workflow request response is empty");
                return new JSONObject();
            }
        } catch (IOException e) {
            log.error("Synchronize maas workflow request failed: {}", e.getMessage());
            return new JSONObject();
        }

        JSONObject res = JSONObject.parseObject(response);
        if (res.getInteger("code") != 0) {
            log.error("------ Synchronize maas workflow failed, reason: {}", res);
            return new JSONObject();
        }
        return res;
    }

    @Deprecated(since = "1.0.0", forRemoval = true)
    public static String getRequestCookies(HttpServletRequest request) {
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            return Arrays.stream(cookies)
                    .map(cookie -> cookie.getName() + "=" + cookie.getValue())
                    .collect(Collectors.joining("; "));
        }
        return "";
    }

    public static String getAuthorizationHeader(HttpServletRequest request) {
        String authHeader = request.getHeader("Authorization");
        if (StringUtils.isNotBlank(authHeader)) {
            return authHeader;
        }
        log.debug("MaaSUtil.getAuthorizationToken(): Authorization header is empty");
        return "";
    }

    /**
     * Handle file type
     *
     * @param type
     * @param param
     * @return
     */
    public static int getFileType(String type, JSONObject param) {
        if (StringUtils.isBlank(type)) {
            return BotUploadEnum.NONE.getValue();
        }
        switch (type.toLowerCase()) {
            case "pdf":
                return WorkflowBotParamServiceImpl.isFileArray(param) ? BotUploadEnum.DOC_ARRAY.getValue() : BotUploadEnum.DOC.getValue();
            case "image":
                return WorkflowBotParamServiceImpl.isFileArray(param) ? BotUploadEnum.IMG_ARRAY.getValue() : BotUploadEnum.IMG.getValue();
            case "doc":
                return WorkflowBotParamServiceImpl.isFileArray(param) ? BotUploadEnum.DOC2_ARRAY.getValue() : BotUploadEnum.DOC2.getValue();
            case "ppt":
                return WorkflowBotParamServiceImpl.isFileArray(param) ? BotUploadEnum.PPT_ARRAY.getValue() : BotUploadEnum.PPT.getValue();
            case "excel":
                return WorkflowBotParamServiceImpl.isFileArray(param) ? BotUploadEnum.EXCEL_ARRAY.getValue() : BotUploadEnum.EXCEL.getValue();
            case "txt":
                return WorkflowBotParamServiceImpl.isFileArray(param) ? BotUploadEnum.TXT_ARRAY.getValue() : BotUploadEnum.TXT.getValue();
            case "audio":
                return WorkflowBotParamServiceImpl.isFileArray(param) ? BotUploadEnum.AUDIO_ARRAY.getValue() : BotUploadEnum.AUDIO.getValue();
            default:
                return BotUploadEnum.NONE.getValue();
        }
    }

    public static String generatePrefix(String uid, Integer botId) {
        return PREFIX_MAAS_COPY + uid + "_" + botId;
    }

    /**
     * Set tags for workflow assistant
     */
    @Transactional
    public void setBotTag(JSONObject botInfo) {
        try {
            // Get assistant tag mapping table from redis
            // Structure is like [{"name":"Knowledge Base","tag":["Knowledge Base"]}, omitted..................]
            String botTagList = redissonClient.getBucket(BOT_TAG_LIST).get().toString();
            if (StringUtils.isNotBlank(botTagList)) {
                JSONArray jsonBotTag = JSONArray.parseArray(botTagList);
                Integer botId = botInfo.getInteger("botId");
                JSONArray nodes = botInfo.getJSONObject("data").getJSONArray("nodes");
                // Count node name occurrences, as tags may differ for single vs multiple node appearances
                Map<String, Integer> nodeNameCountMap = new HashMap<>();
                for (int i = 0; i < nodes.size(); i++) {
                    String name = nodes.getJSONObject(i).getJSONObject("data").getJSONObject("nodeMeta").getString("aliasName");
                    nodeNameCountMap.put(name, nodeNameCountMap.getOrDefault(name, 0) + 1);
                }
                // Final tag list, ensure no duplicate tags
                HashSet<BotTag> tags = new HashSet<>();
                for (int i = 0; i < nodes.size(); i++) {
                    String name = nodes.getJSONObject(i).getJSONObject("data").getJSONObject("nodeMeta").getString("aliasName");
                    for (int j = 0; j < jsonBotTag.size(); j++) {
                        JSONObject botTag = (JSONObject) jsonBotTag.get(j);
                        if (botTag.getString("name").equals(name)) {
                            if (nodeNameCountMap.get(name) > 1) {
                                BotTag multiNodeTag = botTag.getJSONObject("tag").getObject("multiNode", BotTag.class);
                                tags.add(multiNodeTag);
                            } else {
                                BotTag tag = botTag.getObject("tag", BotTag.class);
                                tags.add(tag);
                            }
                        }
                    }
                }
                // When republishing, first disable the original tags
                ChatBotTag updateChatBotTag = new ChatBotTag();
                updateChatBotTag.setIsAct(0);
                chatBotTagService.update(updateChatBotTag, Wrappers.lambdaQuery(ChatBotTag.class).eq(ChatBotTag::getBotId, botId));
                // Publish tags for this time, maximum of 3 tags needed
                List<ChatBotTag> chatBotTagList = new ArrayList<>();
                List<BotTag> list = new ArrayList<>(tags);
                // Sort by index in descending order
                list.sort((a, b) -> b.getIndex() - a.getIndex());
                for (int i = 0; i < list.size(); i++) {
                    BotTag item = list.get(i);
                    ChatBotTag chatBotTag = new ChatBotTag();
                    chatBotTag.setBotId(botId);
                    chatBotTag.setTag(item.getTagName());
                    chatBotTag.setOrder(item.getIndex());
                    chatBotTagList.add(chatBotTag);
                }
                chatBotTagService.saveBatch(chatBotTagList);
            } else {
                log.error("Assistant tag mapping table is null in Redis");
            }
        } catch (Exception e) {
            log.error("Failed to parse assistant tags, request parameters: {}, error: {}", JSONObject.toJSONString(botInfo), e.getMessage());
            throw e;
        }
    }

    /**
     * Create API (without version)
     *
     * @param flowId Workflow ID
     * @param appid Application ID
     * @return JSONObject response result
     */
    public JSONObject createApi(String flowId, String appid) {
        return createApiInternal(flowId, appid, null, null);
    }

    public void createApi(String flowId, String appid, String version) {
        createApiInternal(flowId, appid, version, null);
    }

    /**
     * Create API (with version) - data parameter is not sent to workflow/v1/publish
     *
     * @param flowId Workflow ID
     * @param appid Application ID
     * @param version Version number
     * @param data Version data (not used in publish request)
     * @return JSONObject response result
     */
    public JSONObject createApi(String flowId, String appid, String version, JSONObject data) {
        // Note: data parameter is not passed to publish API as per requirement
        return createApiInternal(flowId, appid, version, null);
    }

    /**
     * Internal generic method for creating API
     *
     * @param flowId Workflow ID
     * @param appid Application ID
     * @param version Version number (can be null)
     * @return JSONObject response result
     */
    private JSONObject createApiInternal(String flowId, String appid, String version, JSONObject data) {
        log.info("----- Publishing maas workflow flowId: {}", flowId);
        // Create MaasApi without data parameter for publish request
        MaasApi maasApi = new MaasApi(flowId, appid, version);

        // Execute publish request
        String publishResponse = executeRequest(publishApi, maasApi);
        validateResponse(publishResponse, "publish", flowId, appid);

        // Execute authentication request
        String authResponse = executeRequest(authApi, maasApi);
        validateResponse(authResponse, "bind", flowId, appid);

        return new JSONObject();
    }

    /**
     * Execute HTTP POST request and return response string
     *
     * @param url Request URL
     * @param bodyData Request body data object
     * @return String representation of response content
     */
    private String executeRequest(String url, MaasApi bodyData) {
        RequestBody requestBody = RequestBody.create(
                JSONObject.toJSONString(bodyData),
                MediaType.parse("application/json; charset=utf-8"));
        Request request = new Request.Builder()
                .url(url)
                .post(requestBody)
                .addHeader("X-Consumer-Username", consumerId)
                .addHeader("Lang-Code", I18nUtil.getLanguage())
                .addHeader("Authorization", "Bearer %s:%s".formatted(consumerKey, consumerSecret))
                .addHeader(X_AUTH_SOURCE_HEADER, X_AUTH_SOURCE_VALUE)
                .build();
        log.info("MaasUtil executeRequest url: {} request: {}, header: {}", request.url(), request, request.headers());
        try (Response httpResponse = HTTP_CLIENT.newCall(request).execute()) {
            ResponseBody responseBody = httpResponse.body();
            if (responseBody != null) {
                return responseBody.string();
            } else {
                log.error("Request to {} returned empty response", url);
                return "{}"; // Return empty JSON object string to avoid parsing errors
            }
        } catch (IOException e) {
            throw new BusinessException(ResponseEnum.BOT_API_CREATE_ERROR, e);
        }
    }

    /**
     * Validate whether the response is successful
     *
     * @param responseStr Response content string representation
     * @param action Description of current operation being performed (e.g., "publish", "bind")
     * @param flowId Workflow ID
     * @param appid Application ID
     */
    private void validateResponse(String responseStr, String action, String flowId, String appid) {
        log.info("----- {} maas api response: {}", action, responseStr);
        JSONObject res = JSONObject.parseObject(responseStr);
        if (res.getInteger("code") != 0) {
            log.error("------ Failed to {} maas api, maasId: {}, appid: {}, reason: {}", action, flowId, appid, responseStr);
            throw new BusinessException(ResponseEnum.BOT_API_CREATE_ERROR);
        }
    }


    public JSONObject copyWorkFlow(Long maasId, HttpServletRequest request, Integer version, Long targetId, TalkAgentConfigDto talkAgentConfig) {
        log.info("----- Copying maas workflow id: {}", maasId);
        HttpUrl baseUrl = HttpUrl.parse(cloneWorkFlowUrl);
        if (baseUrl == null) {
            log.error("Failed to parse clone workflow URL: {}", cloneWorkFlowUrl);
            throw new BusinessException(ResponseEnum.CLONE_BOT_FAILED);
        }
        BotCloneWorkflowDto cloneWorkflowDto = new BotCloneWorkflowDto();
        cloneWorkflowDto.setMaasId(maasId);
        cloneWorkflowDto.setFlowType(version);
        cloneWorkflowDto.setBotId(Math.toIntExact(targetId));
        cloneWorkflowDto.setPassword("xfyun");
        cloneWorkflowDto.setFlowConfig(talkAgentConfig);
        RequestBody requestBody = RequestBody.create(JSONObject.toJSONString(cloneWorkflowDto), MediaType.parse("application/json; charset=utf-8"));

        Request httpRequest = new Request.Builder()
                .url(baseUrl)
                .addHeader("X-Consumer-Username", consumerId)
                .addHeader("Lang-Code", I18nUtil.getLanguage())
                .addHeader("space-id", String.valueOf(SpaceInfoUtil.getSpaceId()))
                .addHeader(AUTHORIZATION_HEADER, MaasUtil.getAuthorizationHeader(request))
                .addHeader(X_AUTH_SOURCE_HEADER, X_AUTH_SOURCE_VALUE)
                .post(requestBody)
                .build();
        String responseBody;
        try (Response response = client.newCall(httpRequest).execute()) {
            if (!response.isSuccessful()) {
                // Handle request failure
                throw new IOException("Unexpected code " + response);
            }
            ResponseBody body = response.body();
            if (body != null) {
                responseBody = body.string();
            } else {
                throw new IOException("Response body is null");
            }
        } catch (IOException e) {
            // Handle exception
            log.error("Failed to call internal-clone endpoint", e);
            throw new BusinessException(ResponseEnum.CLONE_BOT_FAILED);
        }
        JSONObject resClone = JSON.parseObject(responseBody);

        if (resClone == null) {
            log.info("------ Failed to copy maas workflow, maasId: {}, reason: response is null", maasId);
            return null;
        }
        return resClone;
    }

    @Transactional
    public JSONObject getInputsType(Integer botId, UserLangChainInfo chainInfo, String authorizationHeaderValue) {
        String flowId = chainInfo.getFlowId();

        // Build URL with query parameter
        String urlWithParams = getInputsUrl + "?flowId=" + flowId;

        // Build request
        Request getInputsRequest = new Request.Builder()
                .url(urlWithParams)
                .get()
                .addHeader("Authorization", authorizationHeaderValue)
                .addHeader(X_AUTH_SOURCE_HEADER, X_AUTH_SOURCE_VALUE)
                .build();

        String response;
        try (Response httpResponse = HTTP_CLIENT.newCall(getInputsRequest).execute()) {
            ResponseBody responseBody = httpResponse.body();
            if (responseBody != null) {
                response = responseBody.string();
            } else {
                log.error("Get inputs type request response is empty");
                return null;
            }
        } catch (IOException e) {
            log.error("Get inputs type request failed: {}", e.getMessage());
            return null;
        }
        JSONObject res = JSON.parseObject(response);
        if (res.getInteger("code") != 0) {
            log.info("------ Failed to get workflow input parameter types, flowId: {}, reason: {}", flowId, response);
            return null;
        }
        log.info("----- flowId: {} workflow input parameters: {}", flowId, response);
        JSONArray dataArray = res.getJSONArray("data");
        // Remove fixed inputs first
        List<JSONObject> filteredParams = new ArrayList<>();
        for (int i = 0; i < dataArray.size(); i++) {
            JSONObject param = dataArray.getJSONObject(i);
            if ("AGENT_USER_INPUT".equals(param.getString("name"))) {
                continue;
            }
            filteredParams.add(param);
        }
        LambdaUpdateWrapper<ChatBotBase> wrapper = new LambdaUpdateWrapper<>();
        wrapper.eq(ChatBotBase::getId, botId);
        List<JSONObject> extraInputs = new ArrayList<>();
        if (!filteredParams.isEmpty()) {
            // Get the input type of this parameter
            for (JSONObject param : filteredParams) {
                String type;
                JSONObject extraInput = new JSONObject();
                if (Objects.nonNull(param.getJSONArray("allowedFileType"))) {
                    type = param.getJSONArray("allowedFileType").getString(0).toLowerCase();
                    extraInput.put(param.getString("name"), type);
                    extraInput.put("required", param.getBoolean("required"));

                    extraInput.put("schema", param.get("schema"));
                    extraInput.put("name", param.getString("name"));
                    extraInput.put("type", type);
                    extraInput.put("fullParam", param);
                } else {
                    // Handle non-file & non-String type parameters (e.g. integer/boolean...)
                    extraInput.put(param.getString("name"), param.getJSONObject("schema").getString("type"));
                    extraInput.put(param.getString("name") + "_required", param.getBoolean("required"));
                    extraInput.put("name", param.getString("name"));
                    extraInput.put("type", param.getJSONObject("schema").getString("type"));
                    extraInput.put("schema", param.get("schema"));
                }

                extraInputs.add(extraInput);
            }
            JSONObject oldExtraInputs = keepOldValue(extraInputs);
            wrapper.set(ChatBotBase::getSupportUpload, getFileType(oldExtraInputs.getString("type"), oldExtraInputs));
        } else {
            wrapper.set(ChatBotBase::getSupportUpload, BotUploadEnum.NONE.getValue());
        }
        // Update fields
        if (!Objects.isNull(wrapper.getSqlSet())) {
            chatBotBaseMapper.update(null, wrapper);
        }
        // Update record
        chainInfo.setExtraInputsConfig(JSON.toJSONString(extraInputs));
        chainInfo.setExtraInputs(JSON.toJSONString(keepOldValue(extraInputs)));
        userLangChainDataService.updateByBotId(botId, chainInfo);
        return res;
    }

    /**
     * Keep old logic, find the first parameter that is not a file array type and return it
     *
     * @param extraInputs
     * @return
     */
    public static JSONObject keepOldValue(List<JSONObject> extraInputs) {
        if (ObjectUtil.isEmpty(extraInputs)) {
            return new JSONObject();
        }
        for (JSONObject extraInput : extraInputs) {
            // Not file array & not other basic types
            if (!isFileArray(extraInput)) {
                if (!NO_SUPPORT_TYPE.contains(extraInput.getString("type"))) {
                    return extraInput;
                }
            }
        }
        return new JSONObject();
    }

    /**
     * Determine if parameter is array type
     *
     * @param param
     * @return
     */
    public static boolean isFileArray(JSONObject param) {
        try {
            return "array-string".equalsIgnoreCase(param.getJSONObject("schema").getString("type"));
        } catch (Exception e) {
            log.error("Exception determining if parameter is array type: {}", e.getMessage());
            return false;
        }
    }

}

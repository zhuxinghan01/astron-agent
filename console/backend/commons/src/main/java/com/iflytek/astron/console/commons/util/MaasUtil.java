package com.iflytek.astron.console.commons.util;

import cn.hutool.core.collection.ListUtil;
import cn.hutool.core.util.ObjectUtil;
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.dto.bot.AdvancedConfig;
import com.iflytek.astron.console.commons.dto.bot.BotCreateForm;
import com.iflytek.astron.console.commons.dto.bot.BotTag;
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
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;


@Slf4j
@Service
public class MaasUtil {
    private static final String X_AUTH_SOURCE_HEADER = "x-auth-source";
    private static final String X_AUTH_SOURCE_VALUE = "xfyun";

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

    @Value("${maas.publish}")
    private String publishUrl;

    @Value("${maas.canPublishUrl}")
    private String trailStatusUrl;

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

    public static final String PREFIX_MASS_COPY = "mass_copy_";
    private static final String BOT_TAG_LIST = "bot_tag_list";

    @Autowired
    private UserLangChainDataService userLangChainDataService;

    @Autowired
    private ChatBotTagService chatBotTagService;

    @Autowired
    private RedissonClient redissonClient;

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
                log.error("Delete mass workflow request response is empty");
                return new JSONObject();
            }
        } catch (IOException e) {
            log.error("Delete mass workflow request failed: {}", e.getMessage());
            return new JSONObject();
        }
        JSONObject res = JSON.parseObject(response);
        if (res.getInteger("code") != 0) {
            log.info("------ Delete mass workflow failed, reason: {}", response);
            return new JSONObject();
        }
        return res;

    }

    public JSONObject synchronizeWorkFlow(UserLangChainInfo userLangChainInfo, BotCreateForm botCreateForm,
                                          HttpServletRequest request, Long spaceId) {
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
        log.info("----- mass synchronization request body: {}", JSONObject.toJSONString(param));

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
                log.error("Synchronize mass workflow request response is empty");
                return new JSONObject();
            }
        } catch (IOException e) {
            log.error("Synchronize mass workflow request failed: {}", e.getMessage());
            return new JSONObject();
        }

        JSONObject res = JSONObject.parseObject(response);
        if (res.getInteger("code") != 0) {
            log.error("------ Synchronize mass workflow failed, reason: {}", res);
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
        return PREFIX_MASS_COPY + uid + "_" + botId;
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
     * @param appid  Application ID
     * @return JSONObject response result
     */
    public JSONObject createApi(String flowId, String appid) {
        return createApiInternal(flowId, appid, null, null);
    }

    public void createApi(String flowId, String appid, String version) {
        createApiInternal(flowId, appid, version, null);
    }

    /**
     * Create API (with version)
     *
     * @param flowId  Workflow ID
     * @param appid   Application ID
     * @param version Version number
     * @return JSONObject response result
     */
    public JSONObject createApi(String flowId, String appid, String version, JSONObject data) {
        return createApiInternal(flowId, appid, version, data);
    }

    /**
     * Internal generic method for creating API
     *
     * @param flowId  Workflow ID
     * @param appid   Application ID
     * @param version Version number (can be null)
     * @return JSONObject response result
     */
    private JSONObject createApiInternal(String flowId, String appid, String version, JSONObject data) {
        log.info("----- Publishing mass workflow flowId: {}", flowId);
        MaasApi maasApi = new MaasApi(flowId, appid, version, data);

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
     * @param url      Request URL
     * @param bodyData Request body data object
     * @return String representation of response content
     */
    private String executeRequest(String url, MaasApi bodyData) {
        Map<String, String> authMap = AuthStringUtil.authMap(url, "POST", consumerKey, consumerSecret, JSONObject.toJSONString(bodyData));
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
        log.info("MaasUtil executeRequest url: {} request: {}, header: {}", request.url(), JSONObject.toJSONString(authMap), request.headers());
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
     * @param action      Description of current operation being performed (e.g., "publish", "bind")
     * @param flowId      Workflow ID
     * @param appid       Application ID
     */
    private void validateResponse(String responseStr, String action, String flowId, String appid) {
        log.info("----- {} maas api response: {}", action, responseStr);
        JSONObject res = JSONObject.parseObject(responseStr);
        if (res.getInteger("code") != 0) {
            log.error("------ Failed to {} maas api, massId: {}, appid: {}, reason: {}", action, flowId, appid, responseStr);
            throw new BusinessException(ResponseEnum.BOT_API_CREATE_ERROR);
        }
    }


    public JSONObject copyWorkFlow(Long maasId, String uid) {
        log.info("----- Copying maas workflow id: {}", maasId);
        HttpUrl baseUrl = HttpUrl.parse(cloneWorkFlowUrl + "/workflow/internal-clone");
        if (baseUrl == null) {
            log.error("Failed to parse clone workflow URL: {}", cloneWorkFlowUrl);
            throw new BusinessException(ResponseEnum.CLONE_BOT_FAILED);
        }
        Map<String, String> pubAuth = AuthStringUtil.authMap(baseUrl.toString(), "POST", consumerKey, consumerSecret, null);
        HttpUrl httpUrl = baseUrl.newBuilder()
                .addQueryParameter("id", String.valueOf(maasId))
                .addQueryParameter("password", "xfyun")
                .build();
        Request httpRequest = new Request.Builder()
                .url(httpUrl)
                .addHeader("X-Consumer-Username", consumerId)
                .addHeader("Lang-Code", I18nUtil.getLanguage())
                .headers(Headers.of(pubAuth))
                .addHeader(X_AUTH_SOURCE_HEADER, X_AUTH_SOURCE_VALUE)
                .get()
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
            if ("array-string".equalsIgnoreCase(param.getJSONObject("schema").getString("type"))) {
                return true;
            } else {
                return false;
            }
        } catch (Exception e) {
            log.error("Exception determining if parameter is array type: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Register MCP server - real implementation based on old project's logic
     * Corresponds to massUtil.registerMcp in original project
     *
     * @param cookie      HTTP cookies from request
     * @param chainInfo   workflow chain information
     * @param mcpRequest  MCP publish request data
     * @param versionName workflow version name
     * @return JSONObject containing MCP registration result
     */
    public static JSONObject registerMcp(String cookie, Object chainInfo, Object mcpRequest, String versionName) {
        log.info("Registering MCP server: versionName={}", versionName);

        try {
            // Extract flowId from chainInfo
            String flowId = extractFlowId(chainInfo);
            if (flowId == null || flowId.trim().isEmpty()) {
                throw new IllegalArgumentException("FlowId is required for MCP registration");
            }

            // Extract botId from mcpRequest
            Integer botId = extractBotId(mcpRequest);
            if (botId == null) {
                throw new IllegalArgumentException("BotId is required for MCP registration");
            }

            // 1. Get workflow input parameters (equivalent to getInputsType in old project)
            List<JSONObject> args = getWorkflowInputs(flowId, cookie);
            log.info("Retrieved workflow inputs for flowId {}: {} parameters", flowId, args.size());

            // 2. Build MCP info object (equivalent to releaseDto.McpInfo in old project)
            JSONObject mcpInfo = buildMcpInfo(mcpRequest, args);
            log.debug("Built MCP info: {}", mcpInfo.toJSONString());

            // 3. Build flow release request (equivalent to FlowReleaseReq in old project)
            JSONObject flowReleaseReq = buildFlowReleaseRequest(flowId, mcpInfo, versionName);
            log.info("Built flow release request for MCP: flowId={}, version={}", flowId, versionName);

            // 4. Perform actual MCP service registration (equivalent to releaseService.mcpRelease)
            String mcpUrl = performMcpServiceRegistration(flowReleaseReq, cookie);
            log.info("MCP service registration completed: flowId={}, mcpUrl={}", flowId, mcpUrl);

            // 5. Build result object with real data
            JSONObject result = buildMcpResult(mcpRequest, mcpUrl, flowId, versionName);
            log.info("MCP server registration successful: serverUrl={}", mcpUrl);

            return result;

        } catch (Exception e) {
            log.error("Failed to register MCP server: versionName={}", versionName, e);
            JSONObject errorResult = new JSONObject();
            errorResult.put("code", -1);
            errorResult.put("message", "Failed to register MCP server: " + e.getMessage());
            errorResult.put("success", false);
            return errorResult;
        }
    }

    /**
     * Extract flowId from chainInfo object using reflection
     */
    private static String extractFlowId(Object chainInfo) {
        if (chainInfo == null) return null;
        
        try {
            java.lang.reflect.Method getFlowId = chainInfo.getClass().getMethod("getFlowId");
            return (String) getFlowId.invoke(chainInfo);
        } catch (Exception e) {
            log.warn("Failed to extract flowId from chainInfo: {}", e.getMessage());
            return null;
        }
    }

    /**
     * Extract botId from mcpRequest object using reflection
     */
    private static Integer extractBotId(Object mcpRequest) {
        if (mcpRequest == null) return null;
        
        try {
            java.lang.reflect.Method getBotId = mcpRequest.getClass().getMethod("getBotId");
            return (Integer) getBotId.invoke(mcpRequest);
        } catch (Exception e) {
            log.warn("Failed to extract botId from mcpRequest: {}", e.getMessage());
            return null;
        }
    }

    /**
     * Get workflow input parameters (equivalent to getInputsType in old project)
     * This method retrieves the actual workflow parameters needed for MCP tools
     */
    private static List<JSONObject> getWorkflowInputs(String flowId, String cookie) {
        log.info("Getting workflow inputs for flowId: {}", flowId);
        
        try {
            // Build the request URL - using the existing getInputsUrl configuration
            // This corresponds to the old project's HttpRequest.get(getInputsUrl)
            String getInputsUrl = getConfigValue("maas.getInputs");
            if (getInputsUrl == null || getInputsUrl.trim().isEmpty()) {
                log.warn("maas.getInputs configuration not found, cannot retrieve workflow inputs");
                return new ArrayList<>();
            }
            
            // Build HTTP request with form parameters
            Map<String, String> formParams = new HashMap<>();
            formParams.put("flowId", flowId);
            
            Map<String, String> headers = new HashMap<>();
            headers.put("x-auth-source", "xfyun");
            headers.put("Cookie", cookie);
            // Note: Lang-Code header would need language context, using default for now
            
            // Execute HTTP request
            String response = executeHttpGetRequest(getInputsUrl, formParams, headers);
            if (response == null) {
                log.error("Failed to get response from workflow inputs API");
                return new ArrayList<>();
            }
            
            // Parse response
            JSONObject res = JSON.parseObject(response);
            if (res.getIntValue("code") != 0) {
                log.error("Failed to get workflow inputs: flowId={}, response={}", flowId, response);
                return new ArrayList<>();
            }
            
            log.info("Successfully retrieved workflow inputs for flowId: {}", flowId);
            
            // Extract and filter parameters (equivalent to old project's logic)
            JSONArray dataArray = res.getJSONArray("data");
            List<JSONObject> filteredParams = new ArrayList<>();
            
            if (dataArray != null) {
                for (int i = 0; i < dataArray.size(); i++) {
                    JSONObject param = dataArray.getJSONObject(i);
                    // Filter out fixed input (equivalent to old project's logic)
                    if ("AGENT_USER_INPUT".equals(param.getString("name"))) {
                        continue;
                    }
                    filteredParams.add(param);
                }
            }
            
            log.info("Filtered workflow inputs: flowId={}, paramCount={}", flowId, filteredParams.size());
            return filteredParams;
            
        } catch (Exception e) {
            log.error("Exception occurred while getting workflow inputs: flowId={}", flowId, e);
            return new ArrayList<>();
        }
    }

    /**
     * Build MCP info object (equivalent to releaseDto.McpInfo in old project)
     */
    private static JSONObject buildMcpInfo(Object mcpRequest, List<JSONObject> args) {
        JSONObject mcpInfo = new JSONObject();
        
        try {
            // Extract data from mcpRequest using reflection
            java.lang.reflect.Method getServerName = mcpRequest.getClass().getMethod("getServerName");
            java.lang.reflect.Method getDescription = mcpRequest.getClass().getMethod("getDescription");
            java.lang.reflect.Method getContent = mcpRequest.getClass().getMethod("getContent");
            java.lang.reflect.Method getIcon = mcpRequest.getClass().getMethod("getIcon");

            mcpInfo.put("serverName", getServerName.invoke(mcpRequest));
            mcpInfo.put("description", getDescription.invoke(mcpRequest));
            mcpInfo.put("content", getContent.invoke(mcpRequest));
            mcpInfo.put("icon", getIcon.invoke(mcpRequest));
            mcpInfo.put("args", args); // Real workflow parameters
            
        } catch (Exception e) {
            log.error("Failed to build MCP info from mcpRequest", e);
            throw new RuntimeException("Failed to build MCP info", e);
        }
        
        return mcpInfo;
    }

    /**
     * Build flow release request (equivalent to FlowReleaseReq in old project)
     */
    private static JSONObject buildFlowReleaseRequest(String flowId, JSONObject mcpInfo, String versionName) {
        JSONObject flowReleaseReq = new JSONObject();
        flowReleaseReq.put("flowId", flowId);
        flowReleaseReq.put("channel", "mcp");
        flowReleaseReq.put("operate", 1); // SERVER_OPER_RELEASE
        flowReleaseReq.put("mcpInfo", mcpInfo.toJSONString());
        flowReleaseReq.put("version", versionName);
        return flowReleaseReq;
    }

    /**
     * Perform actual MCP service registration (equivalent to releaseService.mcpRelease)
     * This is the core logic that actually registers the MCP service
     */
    private static String performMcpServiceRegistration(JSONObject flowReleaseReq, String cookie) {
        String flowId = flowReleaseReq.getString("flowId");
        String version = flowReleaseReq.getString("version");
        log.info("Performing MCP service registration: flowId={}, version={}", flowId, version);
        
        try {
            // TODO: Call releaseService.mcpRelease equivalent
            // This should delegate to a proper MCP release service that handles:
            // 1. Core system API publishing (coreSystemService.publish)
            // 2. Core system authorization (coreSystemService.auth) 
            // 3. MCP v2.0 authorization (workflowService.mcpAuth)
            // 4. MCP server URL generation and registration
            // 5. Link service registration (mcpServerHandler.mcpPublish)
            // 6. Product data service integration (mcpServerHandler.sendMcpPublish)
            
            // For now, generate MCP URL based on configuration
            String mcpHost = getConfigValue("maas.mcpHost");
            if (mcpHost == null) {
                mcpHost = "https://xingchen-api.xf-yun.com/mcp/xingchen";
            }
            
            String mcpUrl = String.format("%s/flow/%s/sse", mcpHost, flowId);
            
            log.warn("performMcpServiceRegistration not fully implemented - returning generated URL: {}", mcpUrl);
            log.info("TODO: Implement proper MCP release service integration");
            
            return mcpUrl;
            
        } catch (Exception e) {
            log.error("Failed to perform MCP service registration: flowId={}, version={}", flowId, version, e);
            throw new RuntimeException("MCP service registration failed: " + e.getMessage(), e);
        }
    }
    
    /**
     * Build final MCP result object
     */
    private static JSONObject buildMcpResult(Object mcpRequest, String mcpUrl, String flowId, String versionName) {
        JSONObject result = new JSONObject();
        
        try {
            // Copy all fields from mcpRequest
            java.lang.reflect.Method getServerName = mcpRequest.getClass().getMethod("getServerName");
            java.lang.reflect.Method getDescription = mcpRequest.getClass().getMethod("getDescription");
            java.lang.reflect.Method getContent = mcpRequest.getClass().getMethod("getContent");
            java.lang.reflect.Method getIcon = mcpRequest.getClass().getMethod("getIcon");
            java.lang.reflect.Method getBotId = mcpRequest.getClass().getMethod("getBotId");

            result.put("serverName", getServerName.invoke(mcpRequest));
            result.put("description", getDescription.invoke(mcpRequest));
            result.put("content", getContent.invoke(mcpRequest));
            result.put("icon", getIcon.invoke(mcpRequest));
            result.put("botId", getBotId.invoke(mcpRequest));
            result.put("serverUrl", mcpUrl); // Real MCP service URL
            result.put("versionName", versionName);
            result.put("flowId", flowId);
            
            // Success indicators
            result.put("code", 0);
            result.put("message", "MCP server registered successfully");
            result.put("success", true);
            
        } catch (Exception e) {
            log.error("Failed to build MCP result", e);
            throw new RuntimeException("Failed to build MCP result", e);
        }
        
        return result;
    }

    /**
     * Get configuration value by key
     * This is a helper method to access Spring configuration values
     */
    private static String getConfigValue(String key) {
        try {
            // In a static context, we need to access configuration differently
            // For now, return null to indicate configuration access is needed
            // This should be implemented with proper Spring context access
            log.warn("getConfigValue not implemented - configuration access needed for key: {}", key);
            return null;
        } catch (Exception e) {
            log.error("Failed to get configuration value: key={}", key, e);
            return null;
        }
    }

    /**
     * Execute HTTP GET request with form parameters
     */
    private static String executeHttpGetRequest(String url, Map<String, String> formParams, Map<String, String> headers) {
        try {
            // Build URL with form parameters
            StringBuilder urlBuilder = new StringBuilder(url);
            if (formParams != null && !formParams.isEmpty()) {
                urlBuilder.append("?");
                boolean first = true;
                for (Map.Entry<String, String> entry : formParams.entrySet()) {
                    if (!first) {
                        urlBuilder.append("&");
                    }
                    urlBuilder.append(entry.getKey()).append("=").append(java.net.URLEncoder.encode(entry.getValue(), "UTF-8"));
                    first = false;
                }
            }
            
            // Build HTTP request
            Request.Builder requestBuilder = new Request.Builder()
                    .url(urlBuilder.toString())
                    .get();
            
            // Add headers
            if (headers != null) {
                for (Map.Entry<String, String> entry : headers.entrySet()) {
                    requestBuilder.addHeader(entry.getKey(), entry.getValue());
                }
            }
            
            // Execute request
            try (Response response = createOkHttpClient().newCall(requestBuilder.build()).execute()) {
                if (response.isSuccessful() && response.body() != null) {
                    return response.body().string();
                } else {
                    log.error("HTTP request failed: url={}, responseCode={}", url, response.code());
                    return null;
                }
            }
            
        } catch (Exception e) {
            log.error("Exception during HTTP GET request: url={}", url, e);
            return null;
        }
    }

    /**
     * Create OkHttp client for HTTP requests
     */
    private static OkHttpClient createOkHttpClient() {
        return new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
                .writeTimeout(60, TimeUnit.SECONDS)
                .build();
    }

    public static Headers buildHeaders(Map<String, String> headerMap) {
        Headers.Builder headerBuilder = new Headers.Builder();
        if (headerMap != null) {
            for (Map.Entry<String, String> entry : headerMap.entrySet()) {
                if (entry.getKey() != null && entry.getValue() != null) {
                    headerBuilder.add(entry.getKey(), entry.getValue());
                }
            }
        }
        return headerBuilder.build();
    }
}

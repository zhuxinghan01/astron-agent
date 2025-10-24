package com.iflytek.astron.console.commons.service.bot.impl;

import cn.hutool.core.collection.CollectionUtil;
import cn.hutool.core.util.ObjectUtil;
import cn.hutool.core.util.PhoneUtil;
import cn.hutool.core.util.RandomUtil;
import cn.hutool.core.util.StrUtil;
import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.data.UserInfoDataService;
import com.iflytek.astron.console.commons.dto.bot.BotCreateForm;
import com.iflytek.astron.console.commons.dto.bot.BotDetail;
import com.iflytek.astron.console.commons.dto.bot.BotInfoDto;
import com.iflytek.astron.console.commons.entity.bot.*;
import com.iflytek.astron.console.commons.entity.user.UserInfo;
import com.iflytek.astron.console.commons.enums.ShelfStatusEnum;
import com.iflytek.astron.console.commons.enums.bot.BotTypeEnum;
import com.iflytek.astron.console.commons.enums.bot.BotVersionEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.mapper.bot.ChatBotBaseMapper;
import com.iflytek.astron.console.commons.mapper.bot.ChatBotPromptStructMapper;
import com.iflytek.astron.console.commons.service.bot.*;
import com.iflytek.astron.console.commons.service.data.ChatListDataService;
import com.iflytek.astron.console.commons.service.data.DatasetDataService;
import com.iflytek.astron.console.commons.service.data.UserLangChainDataService;
import com.iflytek.astron.console.commons.service.data.UserLangChainLogService;
import com.iflytek.astron.console.commons.util.BotFileParamUtil;
import com.iflytek.astron.console.commons.util.I18nUtil;
import com.iflytek.astron.console.commons.util.MaasUtil;
import com.iflytek.astron.console.commons.util.RequestContextUtil;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.apache.commons.lang3.StringUtils;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

/**
 * @author wowo_zZ
 * @since 2025/9/9 20:24
 **/
@Service
@Slf4j
public class BotServiceImpl implements BotService {

    @Autowired
    private ChatBotDataService chatBotDataService;

    @Autowired
    private UserLangChainDataService userLangChainDataService;

    @Autowired
    private UserInfoDataService userInfoDataService;

    @Autowired
    private BotFavoriteService botFavoriteService;

    @Autowired
    private ChatListDataService chatListDataService;

    @Autowired
    private DatasetDataService datasetDataService;

    @Autowired
    private BotDatasetService botDatasetService;

    @Autowired
    private BotTypeListService botTypeListService;

    @Autowired
    private ChatBotMarketService chatBotMarketService;

    @Autowired
    private RedissonClient redissonClient;

    @Autowired
    private MaasUtil maasUtil;

    @Autowired
    private UserLangChainLogService userLangChainLogService;

    @Autowired
    private ChatBotBaseMapper chatBotBaseMapper;

    @Autowired
    private ChatBotPromptStructMapper chatBotPromptStructMapper;

    @Value("${bot.default.avatar}")
    private String DEFAULT_AVATAR;

    @Value("${maas.workflowConfig}")
    private String workflowConfigUrl;

    public static final String BOT_INPUT_EXAMPLE_SPLIT = "%%split%%";

    private final OkHttpClient httpClient = new OkHttpClient.Builder()
            .connectTimeout(Duration.ofSeconds(10))
            .readTimeout(Duration.ofSeconds(30))
            .writeTimeout(Duration.ofSeconds(30))
            .connectionPool(new ConnectionPool(20, 5, java.util.concurrent.TimeUnit.MINUTES))
            .retryOnConnectionFailure(true)
            .build();

    @Override
    public List<BotTypeList> getBotTypeList() {
        List<BotTypeList> typeList = botTypeListService.getBotTypeList();

        String currentLang = I18nUtil.getLanguage();
        if ("en".equals(currentLang)) {
            typeList.forEach(botType -> {
                if (StringUtils.isNotBlank(botType.getTypeNameEn())) {
                    botType.setTypeName(botType.getTypeNameEn());
                }
            });
        }

        return typeList;
    }

    /**
     * Add 2.0 assistant to chat_bot_list
     */
    @Override
    public void addV2Bot(String uid, Integer botId) {
        ChatBotList chatBot = chatBotDataService.findByUidAndBotId(uid, botId);
        if (chatBot == null) {
            log.error("Data does not exist in chat_bot_list, ignoring insert operation. uid: {}, real_bot_id: {}", uid, botId);
            return;
        }
        // Here botId is the auto-increment primary key id, not the real assistant id, so it should be set
        // to null
        chatBot.setId(null);
        chatBot.setCreateTime(LocalDateTime.now());
        chatBot.setUpdateTime(LocalDateTime.now());
        chatBotDataService.createUserBotList(chatBot);
    }

    @Override
    public BotInfoDto getBotInfo(HttpServletRequest request, Integer botId, Long chatId, String workflowVersion) {
        String uid = RequestContextUtil.getUID();
        String langCode = I18nUtil.getLanguage();
        ChatBotBase chatBotBase = chatBotDataService.findById(botId).orElse(null);

        if (chatBotBase == null) {
            return null;
        }

        BotInfoDto botInfo = createBasicBotInfo(chatBotBase);
        setupFileUploadConfig(botInfo, botId);
        setupMarketInfo(botInfo, chatBotBase, uid);
        setupInputExamples(botInfo, chatBotBase);
        setupCreatorInfo(botInfo, chatBotBase, uid, langCode);
        setupUserRelatedInfo(botInfo, botId, uid, chatBotBase.getUid(), chatId);
        setupDatasetInfo(botInfo, botId);
        setupLanguageSpecificContent(botInfo, chatBotBase, langCode);
        setupWorkflowInfo(botInfo, chatBotBase, request, botId, workflowVersion, uid);

        return botInfo;
    }

    @Override
    public BotInfoDto insertWorkflowBot(String uid, BotCreateForm bot, Long spaceId, Integer version) {
        return executeWithLock("user:create:workflow:bot:uid:" + uid, () -> {
            validateBotCreation(uid, bot.getName(), spaceId);
            ChatBotBase botBase = createWorkflowBotBase(uid, bot, spaceId, version);
            saveBotAndAddToList(botBase);
            return createBotInfoDto(botBase.getId());
        });
    }

    @Override
    public BotInfoDto insertBotBasicInfo(String uid, BotCreateForm bot, Long spaceId) {
        return executeWithLock("user:create:basic:bot:uid:" + uid, () -> {
            validateBotCreation(uid, bot.getName(), spaceId);
            ChatBotBase botBase = createBasicBotBase(uid, bot, spaceId);
            saveBotAndAddToList(botBase);
            processPromptStruct(botBase.getId(), bot);
            return createBotInfoDto(botBase.getId());
        });
    }

    @Override
    public ChatBotBase copyBot(String uid, Integer botId, Long spaceId) {
        // Create new assistant with same name
        BotDetail detail = chatBotBaseMapper.botDetail(Math.toIntExact(botId));
        ChatBotBase botBase = new ChatBotBase();
        BeanUtils.copyProperties(detail, botBase);
        botBase.setId(null);
        // Set a new assistant name as differentiation
        botBase.setVersion(Integer.valueOf(detail.getVersion()));
        botBase.setIsDelete(0);
        botBase.setUid(uid);
        botBase.setSpaceId(spaceId);
        botBase.setBotName(detail.getBotName() + RandomUtil.randomString(6));
        botBase.setUpdateTime(LocalDateTime.now());
        botBase.setCreateTime(LocalDateTime.now());
        chatBotBaseMapper.insert(botBase);
        return botBase;
    }

    /**
     * Edit assistant 2.0 basic information
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public Boolean updateWorkflowBot(String uid, BotCreateForm bot, HttpServletRequest request, Long spaceId) {
        return executeWithLock("user:update:workflow:bot:uid:" + uid, () -> {
            validateBotNameForUpdate(uid, bot.getName(), spaceId);
            updateWorkflowBotInternal(uid, bot, request, spaceId);
            return Boolean.TRUE;
        });
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Boolean updateBotBasicInfo(String uid, BotCreateForm bot, Long spaceId) {
        return executeWithLock("user:update:basic:bot:uid:" + uid, () -> {
            validateBotNameForUpdate(uid, bot.getName(), bot.getBotId(), spaceId);
            updateBasicBotInternal(uid, bot);
            processPromptStruct(bot.getBotId(), bot);
            return Boolean.TRUE;
        });
    }

    @Override
    public void addMaasInfo(String uid, JSONObject maas, Integer botId, Long spaceId) {
        // Synchronize MAAS table
        JSONObject data = maas.getJSONObject("data");
        UserLangChainLog userLangChainLog = UserLangChainLog.builder()
                .id(Long.parseLong(botId.toString()))
                .botId(Long.parseLong(botId.toString()))
                .maasId(data.getLong("id"))
                .flowId(data.getString("flowId"))
                .uid(uid)
                .spaceId(spaceId)
                .updateTime(LocalDateTime.now())
                .build();

        userLangChainLogService.insertUserLangChainLog(userLangChainLog);
        UserLangChainInfo userLangChainInfo = UserLangChainInfo.builder()
                .id(Long.parseLong(botId.toString()))
                .botId(Integer.parseInt(botId.toString()))
                .maasId(data.getLong("id"))
                .flowId(data.getString("flowId"))
                .uid(uid)
                .spaceId(spaceId)
                .updateTime(LocalDateTime.now())
                .build();
        userLangChainDataService.insertUserLangChainInfo(userLangChainInfo);
    }

    private <T> T executeWithLock(String lockKey, java.util.function.Supplier<T> operation) {
        RLock lock = redissonClient.getLock(lockKey);
        try {
            boolean acquired = lock.tryLock(5, 10, TimeUnit.SECONDS);
            if (!acquired) {
                throw new IllegalStateException("Distributed lock acquisition timeout, please try again later");
            }
            return operation.get();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Thread interrupted while acquiring lock", e);
        } catch (Exception e) {
            log.error("Operation failed with lock: {}", lockKey, e);
            throw e;
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    private void validateBotCreation(String uid, String botName, Long spaceId) {
        if (chatBotDataService.checkRepeatBotName(uid, null, botName, spaceId)) {
            throw new BusinessException(ResponseEnum.DUPLICATE_BOT_NAME);
        }

        Long count = (spaceId == null) ? chatBotDataService.countBotsByUid(uid) : chatBotDataService.countBotsByUid(uid, spaceId);

        if (count.intValue() > 100) {
            throw new BusinessException(ResponseEnum.TOO_MANY_BOTS);
        }
    }

    private void validateBotNameForUpdate(String uid, String botName, Long spaceId) {
        if (chatBotDataService.checkRepeatBotName(uid, null, botName, spaceId)) {
            throw new BusinessException(ResponseEnum.DUPLICATE_BOT_NAME);
        }
    }

    private void validateBotNameForUpdate(String uid, String botName, Integer botId, Long spaceId) {
        if (chatBotDataService.checkRepeatBotName(uid, botId, botName, spaceId)) {
            throw new BusinessException(ResponseEnum.DUPLICATE_BOT_NAME);
        }
    }

    private ChatBotBase createWorkflowBotBase(String uid, BotCreateForm bot, Long spaceId, Integer version) {
        ChatBotBase botBase = new ChatBotBase();
        botBase.setUid(uid);
        botBase.setBotType(bot.getBotType());
        botBase.setBotName(bot.getName());
        botBase.setAvatar(bot.getAvatar());
        botBase.setPcBackground(bot.getPcBackground());
        botBase.setAppBackground(bot.getAppBackground());
        botBase.setPrologue(bot.getPrologue());
        botBase.setBotDesc(bot.getBotDesc());
        botBase.setBotTemplate(bot.getBotTemplate());
        botBase.setSupportContext(1);
        botBase.setSupportSystem(bot.getSupportSystem());
        botBase.setPromptType(0);
        botBase.setSpaceId(spaceId);
        setInputExamples(botBase, bot.getInputExample(), null);
        botBase.setBotwebStatus(0);
        botBase.setVersion(version);
        return botBase;
    }

    private ChatBotBase createBasicBotBase(String uid, BotCreateForm bot, Long spaceId) {
        ChatBotBase botBase = new ChatBotBase();
        botBase.setUid(uid);
        botBase.setBotType(bot.getBotType());
        botBase.setBotName(bot.getName());
        botBase.setAvatar(bot.getAvatar());
        botBase.setPcBackground(bot.getPcBackground());
        botBase.setAppBackground(bot.getAppBackground());
        botBase.setBackgroundColor(bot.getBackgroundColor());
        botBase.setPrologue(bot.getPrologue());
        botBase.setBotDesc(bot.getBotDesc());
        botBase.setBotTemplate(bot.getBotTemplate());
        botBase.setSupportContext(bot.getSupportContext());
        botBase.setSupportSystem(bot.getSupportSystem());
        botBase.setSupportDocument(bot.getSupportDocument());
        botBase.setPromptType(bot.getPromptType() != null ? bot.getPromptType() : 0);
        botBase.setPrompt(bot.getPrompt());
        botBase.setPromptSystem(1);
        botBase.setSupportUpload(bot.getSupportUpload());
        botBase.setModel(bot.getModel());
        botBase.setVcnCn(bot.getVcnCn());
        botBase.setVcnEn(bot.getVcnEn());
        botBase.setVcnSpeed(bot.getVcnSpeed());
        botBase.setIsSentence(bot.getIsSentence());
        botBase.setOpenedTool(bot.getOpenedTool());
        botBase.setClientType(bot.getClientType());
        botBase.setBotNameEn(bot.getBotNameEn());
        botBase.setBotDescEn(bot.getBotDescEn());
        botBase.setPrologueEn(bot.getPrologueEn());
        botBase.setClientHide(bot.getClientHide());
        botBase.setVirtualBotType(bot.getVirtualBotType());
        botBase.setVirtualAgentId(bot.getVirtualAgentId());
        botBase.setStyle(bot.getStyle());
        botBase.setBackground(bot.getBackground());
        botBase.setVirtualCharacter(bot.getVirtualCharacter());
        botBase.setMaasBotId(bot.getMaasBotId());
        botBase.setVersion(1);
        botBase.setSpaceId(spaceId);
        setInputExamples(botBase, bot.getInputExample(), bot.getInputExampleEn());
        botBase.setBotwebStatus(0);
        botBase.setModelId(bot.getModelId());
        return botBase;
    }

    private void setInputExamples(ChatBotBase botBase, List<String> inputExample, List<String> inputExampleEn) {
        if (inputExample != null && !inputExample.isEmpty()) {
            botBase.setInputExample(String.join(BOT_INPUT_EXAMPLE_SPLIT, inputExample));
        }
        if (inputExampleEn != null && !inputExampleEn.isEmpty()) {
            botBase.setInputExampleEn(String.join(BOT_INPUT_EXAMPLE_SPLIT, inputExampleEn));
        }
    }

    private void saveBotAndAddToList(ChatBotBase botBase) {
        try {
            chatBotDataService.createBot(botBase);
            chatListDataService.insertChatBotList(botBase);
        } catch (Exception e) {
            log.error("Failed to save bot, uid: {}", botBase.getUid(), e);
            throw new BusinessException(ResponseEnum.CREATE_BOT_FAILED);
        }
    }

    private BotInfoDto createBotInfoDto(Integer botId) {
        BotInfoDto dto = new BotInfoDto();
        dto.setBotId(botId);
        return dto;
    }

    private void updateWorkflowBotInternal(String uid, BotCreateForm bot, HttpServletRequest request, Long spaceId) {
        try {
            Integer botId = bot.getBotId();
            ChatBotBase botBase = ChatBotBase.builder()
                    .uid(uid)
                    .id(botId)
                    .botType(bot.getBotType())
                    .botName(bot.getName())
                    .avatar(bot.getAvatar())
                    .pcBackground(bot.getPcBackground())
                    .appBackground(bot.getAppBackground())
                    .prologue(bot.getPrologue())
                    .botDesc(bot.getBotDesc())
                    .botTemplate(bot.getBotTemplate())
                    .prompt(bot.getPrompt())
                    .supportContext(0)
                    .supportDocument(bot.getSupportDocument())
                    .supportSystem(bot.getSupportSystem())
                    .promptType(bot.getPromptType())
                    .inputExample(bot.getInputExample() != null && bot.getInputExample().size() > 0 ? String.join(BOT_INPUT_EXAMPLE_SPLIT, bot.getInputExample()) : null)
                    .build();

            chatBotDataService.updateBot(botBase);
            chatListDataService.updateChatBotList(botBase);
            chatBotMarketService.updateBotMarketStatus(uid, botId);

            synchronizeWorkflowIfNeeded(botId, bot, request, spaceId);
        } catch (Exception e) {
            log.error("uid update bot error, uid: {}", uid, e);
            throw new BusinessException(ResponseEnum.UPDATE_BOT_FAILED);
        }
    }

    private void synchronizeWorkflowIfNeeded(Integer botId, BotCreateForm bot, HttpServletRequest request, Long spaceId) {
        UserLangChainInfo userLangChainInfo = userLangChainDataService.findOneByBotId(botId);
        if (Objects.nonNull(userLangChainInfo)) {
            maasUtil.synchronizeWorkFlow(userLangChainInfo, bot, request, spaceId, BotVersionEnum.WORKFLOW.getVersion(), null);
        }
    }

    private void updateBasicBotInternal(String uid, BotCreateForm bot) {
        try {
            ChatBotBase botBase = createUpdateBotBase(uid, bot);
            setEnglishInputExamplesIfPresent(botBase, bot.getInputExampleEn());

            chatBotDataService.updateBot(botBase);
            chatListDataService.updateChatBotList(botBase);
            chatBotDataService.updateChatBotMarket(botBase);
        } catch (Exception e) {
            log.error("uid update bot basic info error, uid: {}", uid, e);
            throw new BusinessException(ResponseEnum.UPDATE_BOT_FAILED);
        }
    }

    private ChatBotBase createUpdateBotBase(String uid, BotCreateForm bot) {
        return ChatBotBase.builder()
                .uid(uid)
                .id(bot.getBotId())
                .botType(bot.getBotType())
                .botName(bot.getName())
                .avatar(bot.getAvatar())
                .pcBackground(bot.getPcBackground())
                .appBackground(bot.getAppBackground())
                .backgroundColor(bot.getBackgroundColor())
                .prologue(bot.getPrologue())
                .botDesc(bot.getBotDesc())
                .botTemplate(bot.getBotTemplate())
                .version(BotTypeEnum.SYSTEM_BOT.getType())
                .supportContext(bot.getSupportContext())
                .supportSystem(bot.getSupportSystem())
                .supportDocument(bot.getSupportDocument())
                .promptType(bot.getPromptType())
                .prompt(bot.getPrompt())
                .promptSystem(bot.getPromptSystem())
                .supportUpload(bot.getSupportUpload())
                .model(bot.getModel())
                .vcnCn(bot.getVcnCn())
                .vcnEn(bot.getVcnEn())
                .vcnSpeed(bot.getVcnSpeed())
                .isSentence(bot.getIsSentence())
                .openedTool(bot.getOpenedTool())
                .clientType(bot.getClientType())
                .botNameEn(bot.getBotNameEn())
                .botDescEn(bot.getBotDescEn())
                .prologueEn(bot.getPrologueEn())
                .clientHide(bot.getClientHide())
                .virtualBotType(bot.getVirtualBotType())
                .virtualAgentId(bot.getVirtualAgentId())
                .style(bot.getStyle())
                .background(bot.getBackground())
                .virtualCharacter(bot.getVirtualCharacter())
                .maasBotId(bot.getMaasBotId())
                .inputExample(bot.getInputExample() != null && !bot.getInputExample().isEmpty() ? String.join(BOT_INPUT_EXAMPLE_SPLIT, bot.getInputExample()) : null)
                .modelId(bot.getModelId())
                .build();
    }

    private void setEnglishInputExamplesIfPresent(ChatBotBase botBase, List<String> inputExampleEn) {
        if (inputExampleEn != null && !inputExampleEn.isEmpty()) {
            botBase.setInputExampleEn(String.join(BOT_INPUT_EXAMPLE_SPLIT, inputExampleEn));
        }
    }

    private BotInfoDto createBasicBotInfo(ChatBotBase chatBotBase) {
        BotInfoDto botInfo = new BotInfoDto();
        BeanUtils.copyProperties(chatBotBase, botInfo);
        botInfo.setBotId(chatBotBase.getId());
        botInfo.setBotStatus(ShelfStatusEnum.OFF_SHELF.getCode());
        botInfo.setHotNum("0");
        return botInfo;
    }

    /**
     * Set file upload configuration.
     *
     * @param botInfo Bot information data transfer object
     * @param botId Bot ID
     */
    private void setupFileUploadConfig(BotInfoDto botInfo, Integer botId) {
        try {
            if (Objects.equals(botInfo.getVersion(), BotTypeEnum.WORKFLOW_BOT.getType())) {
                UserLangChainInfo userLangChainInfo = userLangChainDataService.findOneByBotId(botId);
                processFileUploadConfig(botInfo, userLangChainInfo);
            }
        } catch (Exception e) {
            log.error("Failed to get upload file information, botId: {}, error: {}", botId, e.getMessage(), e);
            botInfo.setSupportUpload(new ArrayList<>());
            botInfo.setSupportUploadConfig(new ArrayList<>());
        }
    }

    /**
     * Function to handle file upload configuration
     *
     * @param botInfo Bot information object
     * @param userLangChainInfo User language chain information object
     */
    private void processFileUploadConfig(BotInfoDto botInfo, UserLangChainInfo userLangChainInfo) {
        if (ObjectUtil.isEmpty(userLangChainInfo.getExtraInputs())) {
            botInfo.setSupportUpload(new ArrayList<>());
        } else {
            botInfo.setSupportUpload(BotFileParamUtil.getOldExtraInputsConfig(userLangChainInfo));
        }

        if (ObjectUtil.isEmpty(userLangChainInfo.getExtraInputsConfig())) {
            botInfo.setSupportUploadConfig(BotFileParamUtil.mergeSupportUploadFields(botInfo.getSupportUpload(), new ArrayList<>()));
        } else {
            botInfo.setSupportUploadConfig(BotFileParamUtil.mergeSupportUploadFields(botInfo.getSupportUpload(), BotFileParamUtil.getExtraInputsConfig(userLangChainInfo)));
        }
    }

    private void setupMarketInfo(BotInfoDto botInfo, ChatBotBase chatBotBase, String uid) {
        ChatBotMarket market = chatBotDataService.findMarketBotByBotId(botInfo.getBotId());
        if (Objects.nonNull(market)) {
            if (!uid.equals(chatBotBase.getUid())) {
                botInfo.setAvatar(market.getAvatar());
                botInfo.setBotDesc(market.getBotDesc());
            }
            botInfo.setBotStatus(market.getBotStatus());
        }
    }

    private void setupInputExamples(BotInfoDto botInfo, ChatBotBase chatBotBase) {
        String inputExample = chatBotBase.getInputExample();
        if (StringUtils.isNotBlank(inputExample)) {
            botInfo.setInputExample(parseInputExamples(inputExample));
        } else {
            botInfo.setInputExample(new ArrayList<>());
        }
    }

    private List<String> parseInputExamples(String inputExample) {
        if (!StrUtil.contains(inputExample, BOT_INPUT_EXAMPLE_SPLIT)) {
            inputExample = inputExample.replace(",", BOT_INPUT_EXAMPLE_SPLIT);
        }
        return Arrays.asList(inputExample.split(BOT_INPUT_EXAMPLE_SPLIT));
    }

    private void setupCreatorInfo(BotInfoDto botInfo, ChatBotBase chatBotBase, String uid, String langCode) {
        String creatorUid = chatBotBase.getUid();
        if (creatorUid != null) {
            UserInfo creator = userInfoDataService.findByUid(creatorUid).orElse(null);
            if (ObjectUtil.isNull(creator)) {
                setDefaultCreatorInfo(botInfo, langCode, false);
            } else {
                setCreatorInfoFromUser(botInfo, creator);
            }
        } else {
            setDefaultCreatorInfo(botInfo, langCode, true);
        }
    }

    private void setDefaultCreatorInfo(BotInfoDto botInfo, String langCode, boolean isOfficial) {
        botInfo.setCreatorAvatar(DEFAULT_AVATAR);
        if (isOfficial) {
            botInfo.setCreatorNickname(I18nUtil.getMessage("bot.creator.official"));
        } else {
            botInfo.setCreatorNickname(I18nUtil.getMessage("bot.creator.user_created"));
        }
    }

    private void setCreatorInfoFromUser(BotInfoDto botInfo, UserInfo creator) {
        botInfo.setCreatorAvatar(creator.getAvatar());
        String nickname = creator.getNickname();
        if (StringUtils.isBlank(nickname)) {
            nickname = creator.getMobile();
        }
        if (PhoneUtil.isMobile(nickname)) {
            nickname = PhoneUtil.hideBetween(nickname).toString();
        }
        botInfo.setCreatorNickname(nickname);
    }

    private void setupUserRelatedInfo(BotInfoDto botInfo, Integer botId, String uid, String creatorUid, Long chatId) {
        // Whether favorited
        List<Integer> favoriteBotIdList = botFavoriteService.list(uid);
        botInfo.setIsFavorite(favoriteBotIdList.contains(Math.toIntExact(botId)) ? 1 : 0);

        // Whether created by self
        if (uid != null) {
            botInfo.setMine(uid.equals(creatorUid));
        }

        // Chat related information
        setupChatInfo(botInfo, botId, uid, chatId);

        // Assistant template ID
        botInfo.setTemplateId(!"1".equals(creatorUid) ? botId : -1);
    }

    private void setupChatInfo(BotInfoDto botInfo, Integer botId, String uid, Long chatId) {
        botInfo.setIsAdd(chatId != null ? 1 : 0);
        botInfo.setChatId(chatId);
    }

    private void setupDatasetInfo(BotInfoDto botInfo, Integer botId) {
        List<DatasetInfo> datasetInfoList = datasetDataService.selectDatasetListByBotId(botId);
        List<String> datasetNameList = datasetInfoList.stream()
                .map(DatasetInfo::getName)
                .collect(Collectors.toList());
        botInfo.setDataset(CollectionUtil.isNotEmpty(datasetNameList) ? datasetNameList : new ArrayList<>());
    }

    private void setupLanguageSpecificContent(BotInfoDto botInfo, ChatBotBase chatBotBase, String langCode) {
        if ("en".equals(langCode)) {
            botInfo.setBotName(chatBotBase.getBotNameEn() != null ? chatBotBase.getBotNameEn() : chatBotBase.getBotName());
            botInfo.setBotDesc(chatBotBase.getBotDescEn() != null ? chatBotBase.getBotDescEn() : chatBotBase.getBotDesc());
            botInfo.setPrologue(chatBotBase.getPrologueEn() != null ? chatBotBase.getPrologueEn() : chatBotBase.getPrologue());

            String inputExampleEn = chatBotBase.getInputExampleEn();
            if (StringUtils.isNotBlank(inputExampleEn)) {
                botInfo.setInputExample(parseInputExamples(inputExampleEn));
            }
        }
    }

    private void setupWorkflowInfo(BotInfoDto botInfo, ChatBotBase chatBotBase, HttpServletRequest request,
            Integer botId, String workflowVersion, String uid) {
        Integer version = chatBotBase.getVersion();
        if (!version.equals(BotTypeEnum.WORKFLOW_BOT.getType())) {
            return;
        }

        String background = getFlowAdvancedConfig(botId, MaasUtil.getAuthorizationHeader(request));
        if (StrUtil.isNotEmpty(background)) {
            botInfo.setPcBackground(background);
        }

        if (workflowVersion != null && uid.equals(chatBotBase.getUid())) {
            updateWorkflowStatus(botInfo, botId, workflowVersion);
        }
    }

    private void updateWorkflowStatus(BotInfoDto botInfo, Integer botId, String workflowVersion) {
        try {
            String flowId = userLangChainDataService.findFlowIdByBotId(botId);
            JSONObject releaseStatusJson = getWorkflowApiResponse("http://127.0.0.1:8080/workflow/version/publish-result?flowId=" + flowId + "&name=" + workflowVersion);
            JSONObject versionResult = getWorkflowApiResponse("http://127.0.0.1:8080/workflow/version/get-max-version?botId=" + botId);

            if (!releaseStatusJson.getJSONArray("data").isEmpty()) {
                String releaseStatus = releaseStatusJson.getJSONArray("data").getJSONObject(0).getString("publishResult");
                log.info("botId:{} query release status: {}", botId, releaseStatus);
                botInfo.setBotStatus(Objects.equals(releaseStatus, "success") ? ShelfStatusEnum.ON_SHELF.getCode() : ShelfStatusEnum.OFF_SHELF.getCode());
            }

            String versionMax = versionResult.getJSONObject("data").getString("workflowMaxVersion");
            botInfo.setWorkflowVersion(versionMax);
        } catch (Exception e) {
            log.error("botId:{} query release status exception", botId, e);
            botInfo.setBotStatus(ShelfStatusEnum.OFF_SHELF.getCode());
        }
    }

    @Override
    public Boolean deleteBot(Integer botId) {
        String uid = RequestContextUtil.getUID();
        chatBotDataService.deleteBot(botId, uid);
        // Update status of datasets associated with assistant
        botDatasetService.deleteByBotId(botId);
        return true;
    }

    public String getFlowAdvancedConfig(Integer botId, String authorizationHeaderValue) {
        RequestBody formBody = new FormBody.Builder()
                .add("botId", String.valueOf(botId))
                .build();

        Request request = new Request.Builder()
                .url(workflowConfigUrl)
                .addHeader("Authorization", authorizationHeaderValue)
                .post(formBody)
                .build();

        String response = null;
        try (Response okResponse = httpClient.newCall(request).execute()) {
            if (!okResponse.isSuccessful()) {
                log.error("HTTP request failed: {}", okResponse.code());
                return null;
            }

            ResponseBody responseBody = okResponse.body();
            if (responseBody == null) {
                return null;
            }

            response = responseBody.string();
            if (StringUtils.isBlank(response)) {
                return null;
            }

            JSONObject res = JSONObject.parseObject(response);
            if (Objects.equals(res.getInteger("code"), 0)) {
                JSONObject data = res.getJSONObject("data");
                if (data.getBooleanValue("enabled")) {
                    return data.getJSONObject("info").getString("url");
                }
            }
        } catch (Exception e) {
            log.error("Failed to get assistant background image: {}: {}, botId: {}, response: {}", e.getClass().getName(), e.getMessage(), botId, response);
        }
        return null;
    }

    private JSONObject getWorkflowApiResponse(String url) {
        Request request = new Request.Builder()
                .url(url)
                .get()
                .build();

        try (Response okResponse = httpClient.newCall(request).execute()) {
            if (!okResponse.isSuccessful()) {
                log.error("Workflow API request failed: {}, URL: {}", okResponse.code(), url);
                return new JSONObject();
            }

            ResponseBody responseBody = okResponse.body();
            if (responseBody == null) {
                return new JSONObject();
            }

            String response = responseBody.string();
            if (StringUtils.isBlank(response)) {
                return new JSONObject();
            }

            return JSONObject.parseObject(response);
        } catch (Exception e) {
            log.error("Workflow API call exception, URL: {}, error: {}", url, e.getMessage(), e);
            return new JSONObject();
        }
    }

    public void processPromptStruct(Integer botId, BotCreateForm bot) {
        if (botId == null || bot == null || bot.getPromptType() != 1) {
            return;
        }

        List<BotCreateForm.PromptStruct> promptStructList = bot.getPromptStructList();
        if (promptStructList == null || promptStructList.isEmpty()) {
            return;
        }

        chatBotPromptStructMapper.delete(Wrappers.lambdaQuery(ChatBotPromptStruct.class).eq(ChatBotPromptStruct::getBotId, botId));
        LocalDateTime now = LocalDateTime.now();

        for (BotCreateForm.PromptStruct promptStruct : promptStructList) {
            if (StringUtils.isBlank(promptStruct.getPromptKey()) || StringUtils.isBlank(promptStruct.getPromptValue())) {
                continue;
            }

            ChatBotPromptStruct entity = new ChatBotPromptStruct();
            entity.setBotId(botId);
            entity.setPromptKey(promptStruct.getPromptKey());
            entity.setPromptValue(promptStruct.getPromptValue());
            entity.setCreateTime(now);
            entity.setUpdateTime(now);

            chatBotPromptStructMapper.insert(entity);
        }
    }
}

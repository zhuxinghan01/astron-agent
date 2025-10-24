package com.iflytek.astron.console.hub.controller.bot;

import com.alibaba.fastjson2.JSONObject;
import com.iflytek.astron.console.commons.dto.bot.BotCreateForm;
import com.iflytek.astron.console.commons.dto.bot.BotInfoDto;
import com.iflytek.astron.console.commons.dto.bot.TalkAgentCreateDto;
import com.iflytek.astron.console.commons.response.ApiResult;
import com.iflytek.astron.console.commons.service.bot.BotService;
import com.iflytek.astron.console.commons.service.bot.TalkAgentService;
import com.iflytek.astron.console.commons.util.MaasUtil;
import com.iflytek.astron.console.commons.util.RequestContextUtil;
import com.iflytek.astron.console.commons.util.space.SpaceInfoUtil;
import com.iflytek.astron.console.commons.enums.bot.BotVersionEnum;
import com.iflytek.astron.console.hub.enums.TalkAgentSceneEnum;
import com.iflytek.astron.console.hub.enums.TalkAgentVCNEnum;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "Talk Agent")
@RestController
@RequestMapping(value = "/talkAgent")
public class TalkAgentController {
    @Autowired
    private BotService botService;

    @Autowired
    private TalkAgentService talkAgentService;

    @Autowired
    private MaasUtil maasUtil;

    @PostMapping("/getSceneList")
    public ApiResult<List<TalkAgentSceneEnum>> getSceneList() {
        List<TalkAgentSceneEnum> sceneList = TalkAgentSceneEnum.getAllScenes();
        return ApiResult.success(sceneList);
    }

    @PostMapping("/getVCNList")
    public ApiResult<List<TalkAgentVCNEnum>> getVcnList() {
        List<TalkAgentVCNEnum> vcnList = TalkAgentVCNEnum.getAllVCN();
        return ApiResult.success(vcnList);
    }

    @PostMapping("/create")
    public ApiResult createTalkAgent(HttpServletRequest request, @RequestBody TalkAgentCreateDto bot){
        String uid = RequestContextUtil.getUID();
        Long spaceId = SpaceInfoUtil.getSpaceId();
        //create talk assistant
        BotInfoDto dto = botService.insertWorkflowBot(uid, bot, spaceId, BotVersionEnum.TALK.getVersion());
        int botId = dto.getBotId();
        bot.setBotId(botId);
        JSONObject maas = maasUtil.synchronizeWorkFlow(null, bot, request, spaceId, BotVersionEnum.TALK.getVersion(), bot.getTalkAgentConfig());
        dto.setFlowId(maas.getJSONObject("data").getLong("flowId"));
        dto.setMaasId(maas.getJSONObject("data").getLong("id"));
        botService.addMaasInfo(uid, maas, botId, spaceId);
        return ApiResult.success(dto);
    }

    @PostMapping("/upgradeWorkflow")
    public ApiResult upgradeWorkflow(HttpServletRequest request, @RequestBody BotCreateForm bot) {
        return  ApiResult.success();
    }

    @PostMapping("/saveHistory")
    public ApiResult saveHistory() {
        return ApiResult.success();
    }

    @GetMapping("/signature")
    public ApiResult getSignature(){
        return ApiResult.success(talkAgentService.getSignature());
    }
}

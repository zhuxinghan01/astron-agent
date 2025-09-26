package com.iflytek.astron.console.toolkit.controller.bot;

import com.alibaba.fastjson2.JSONObject;
import com.iflytek.astron.console.toolkit.common.Result;
import com.iflytek.astron.console.toolkit.common.anno.ResponseResultBody;
import com.iflytek.astron.console.toolkit.entity.biz.AiCode;
import com.iflytek.astron.console.toolkit.entity.biz.AiGenerate;
import com.iflytek.astron.console.toolkit.service.bot.PromptService;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;


@RestController
@ResponseResultBody
@RequestMapping("/prompt")
public class PromptController {

    @Resource
    PromptService promptService;

    @PostMapping(path = "/enhance", produces = "text/event-stream;charset=UTF-8")
    public SseEmitter enhance(@RequestBody JSONObject req, HttpServletResponse response) {
        response.addHeader("X-Accel-Buffering", "no");
        return promptService.enhance(req.getString("name"), req.getString("prompt"));
    }

    @PostMapping("/next-question-advice")
    public Object nqa(@RequestBody JSONObject req) {
        return Result.success(promptService.nextQuestionAdvice(req.getString("question")));
    }

    @PostMapping(path = "/ai-generate", produces = "text/event-stream;charset=UTF-8")
    public SseEmitter aiGenerate(@RequestBody AiGenerate aiGenerate, HttpServletResponse response) {
        response.addHeader("X-Accel-Buffering", "no");
        return promptService.aiGenerate(aiGenerate);
    }

    @PostMapping(path = "/ai-code", produces = "text/event-stream;charset=UTF-8")
    public SseEmitter aiCode(@RequestBody AiCode aiCode, HttpServletResponse response) {
        response.addHeader("X-Accel-Buffering", "no");
        return promptService.aiCode(aiCode);
    }
}

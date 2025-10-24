package com.iflytek.astron.console.toolkit.service.bot;

import com.alibaba.fastjson2.JSONArray;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.iflytek.astron.console.commons.entity.workflow.Workflow;
import com.iflytek.astron.console.toolkit.entity.biz.AiCode;
import com.iflytek.astron.console.toolkit.entity.biz.AiGenerate;
import com.iflytek.astron.console.toolkit.entity.table.ConfigInfo;
import com.iflytek.astron.console.toolkit.entity.table.bot.SparkBot;
import com.iflytek.astron.console.toolkit.mapper.ConfigInfoMapper;
import com.iflytek.astron.console.toolkit.mapper.bot.SparkBotMapper;
import com.iflytek.astron.console.toolkit.mapper.workflow.WorkflowMapper;
import com.iflytek.astron.console.toolkit.tool.spark.SparkApiTool;
import static org.assertj.core.api.InstanceOfAssertFactories.list;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for PromptService.
 */
@ExtendWith(MockitoExtension.class)
class PromptServiceTest {

    @Mock
    private SparkApiTool sparkApiTool;
    @Mock
    private ConfigInfoMapper configInfoMapper;
    @Mock
    private SparkBotMapper sparkBotMapper;
    @Mock
    private WorkflowMapper workflowMapper;

    @InjectMocks
    private PromptService service;

    // --------------------- enhance ---------------------

    @Test
    @DisplayName("enhance: Template placeholders should be replaced and Spark should be called to generate SSE")
    void enhance_shouldFillTemplate_andCallSpark() {
        ConfigInfo cfg = new ConfigInfo();
        cfg.setValue("Hi {assistant_name} - {assistant_description}");
        when(configInfoMapper.getByCategoryAndCode("TEMPLATE", "prompt-enhance")).thenReturn(cfg);

        SseEmitter expected = new SseEmitter();
        ArgumentCaptor<String> msgCap = ArgumentCaptor.forClass(String.class);
        when(sparkApiTool.onceChatReturnSseByWs(msgCap.capture())).thenReturn(expected);

        SseEmitter out = service.enhance("alice", "a helpful bot");

        assertThat(out).isSameAs(expected);
        assertThat(msgCap.getValue()).isEqualTo("Hi alice - a helpful bot");
    }

    // --------------------- nextQuestionAdvice ---------------------

    @Test
    @DisplayName("nextQuestionAdvice: Should parse directly when Spark returns a valid JSON array")
    void nqa_shouldParseValidJsonArray() throws InterruptedException {
        ConfigInfo cfg = new ConfigInfo();
        cfg.setValue("Q: {q}");
        when(configInfoMapper.getByCategoryAndCode("TEMPLATE", "next-question-advice")).thenReturn(cfg);

        when(sparkApiTool.onceChatReturnWholeByWs("Q: hello"))
                .thenReturn("[\"a\",\"b\",\"c\"]");

        Object res = service.nextQuestionAdvice("hello");

        assertThat(res).isInstanceOf(JSONArray.class);
        JSONArray arr = (JSONArray) res;
        assertThat(arr.toJavaList(String.class)).containsExactly("a", "b", "c");
    }

    @Test
    @DisplayName("nextQuestionAdvice: Should extract and parse content within brackets when text is not JSON but contains [...] fragment")
    void nqa_shouldExtractBracketContent_whenNotJson() throws InterruptedException {
        ConfigInfo cfg = new ConfigInfo();
        cfg.setValue("MSG:{q}");
        when(configInfoMapper.getByCategoryAndCode("TEMPLATE", "next-question-advice")).thenReturn(cfg);

        when(sparkApiTool.onceChatReturnWholeByWs("MSG:hi"))
                .thenReturn("prefix blah [\"x\",\"y\",\"z\"] tail");

        Object res = service.nextQuestionAdvice("hi");

        assertThat(res).isInstanceOf(JSONArray.class);
        JSONArray arr = (JSONArray) res;
        assertThat(arr.toJavaList(String.class)).containsExactly("x", "y", "z");
    }

    @Test
    @DisplayName("nextQuestionAdvice: Should return three empty strings when underlying exception occurs")
    void nqa_shouldFallbackOnException() throws InterruptedException {
        ConfigInfo cfg = new ConfigInfo();
        cfg.setValue("X:{q}");
        when(configInfoMapper.getByCategoryAndCode("TEMPLATE", "next-question-advice")).thenReturn(cfg);

        when(sparkApiTool.onceChatReturnWholeByWs(anyString()))
                .thenThrow(new RuntimeException("ws err"));

        Object res = service.nextQuestionAdvice("whatever");
        assertThat(res).isInstanceOfAny(List.class);
        assertThat(res)
                .asInstanceOf(list(String.class))
                .containsExactly("", "", "");
    }

    // --------------------- aiGenerate ---------------------

    @Nested
    class AiGenerateTests {

        @Test
        @DisplayName("aiGenerate: Should return SSE fallback when configuration is missing (without calling Spark)")
        void aiGenerate_shouldReturnSseFallback_whenConfigMissing() {
            when(configInfoMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(null);

            SseEmitter out = service.aiGenerate(new AiGenerate());

            assertThat(out).isNotNull();
            verifyNoInteractions(sparkApiTool);
        }

        @Test
        @DisplayName("aiGenerate: For normal code, should use template value directly to call Spark")
        void aiGenerate_normalCode_shouldUseTemplateValue() {
            ConfigInfo cfg = new ConfigInfo();
            cfg.setValue("TEMPLATE_VALUE");
            when(configInfoMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(cfg);

            SseEmitter expected = new SseEmitter();
            ArgumentCaptor<String> msgCap = ArgumentCaptor.forClass(String.class);
            when(sparkApiTool.onceChatReturnSseByWs(msgCap.capture())).thenReturn(expected);

            AiGenerate req = new AiGenerate();
            req.setCode("some-code");

            SseEmitter out = service.aiGenerate(req);

            assertThat(out).isSameAs(expected);
            assertThat(msgCap.getValue()).isEqualTo("TEMPLATE_VALUE");
        }

        @Test
        @DisplayName("aiGenerate: For prologue with botId, should replace {name}/{desc}")
        void aiGenerate_prologue_withBot_shouldReplaceBotFields() {
            ConfigInfo cfg = new ConfigInfo();
            cfg.setValue("Hi {name}; {desc}");
            when(configInfoMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(cfg);

            SparkBot bot = new SparkBot();
            bot.setName("Neo");
            bot.setDescription("Matrix");
            when(sparkBotMapper.selectById(100L)).thenReturn(bot);

            SseEmitter expected = new SseEmitter();
            ArgumentCaptor<String> msgCap = ArgumentCaptor.forClass(String.class);
            when(sparkApiTool.onceChatReturnSseByWs(msgCap.capture())).thenReturn(expected);

            AiGenerate req = new AiGenerate();
            req.setCode("prologue");
            req.setBotId(100L);

            SseEmitter out = service.aiGenerate(req);

            assertThat(out).isSameAs(expected);
            assertThat(msgCap.getValue()).isEqualTo("Hi Neo; Matrix");
            verifyNoInteractions(workflowMapper);
        }

        @Test
        @DisplayName("aiGenerate: For prologue with flowId, should replace {name}/{desc}")
        void aiGenerate_prologue_withFlow_shouldReplaceFlowFields() {
            ConfigInfo cfg = new ConfigInfo();
            cfg.setValue("Hi {name}; {desc}");
            when(configInfoMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(cfg);

            Workflow flow = new Workflow();
            flow.setName("WF");
            flow.setDescription("desc");
            when(workflowMapper.selectById(9L)).thenReturn(flow);

            SseEmitter expected = new SseEmitter();
            ArgumentCaptor<String> msgCap = ArgumentCaptor.forClass(String.class);
            when(sparkApiTool.onceChatReturnSseByWs(msgCap.capture())).thenReturn(expected);

            AiGenerate req = new AiGenerate();
            req.setCode("prologue");
            req.setFlowId(9L);

            SseEmitter out = service.aiGenerate(req);

            assertThat(out).isSameAs(expected);
            assertThat(msgCap.getValue()).isEqualTo("Hi WF; desc");
            verifyNoInteractions(sparkBotMapper);
        }
    }

    // --------------------- aiCode ---------------------

    @Nested
    class AiCodeTests {
        @Test
        @DisplayName("aiCode: Should return SSE fallback when template is missing")
        void aiCode_shouldReturnSseFallback_whenPromptMissing() {
            when(configInfoMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(null);

            SseEmitter out = service.aiCode(new AiCode());

            assertThat(out).isNotNull();
            verifyNoInteractions(sparkApiTool);
        }

        @Test
        @DisplayName("aiCode: Should return SSE fallback when template value is empty")
        void aiCode_shouldReturnSseFallback_whenPromptEmpty() {
            ConfigInfo cfg = new ConfigInfo();
            cfg.setValue("   "); // blank
            when(configInfoMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(cfg);

            SseEmitter out = service.aiCode(new AiCode());

            assertThat(out).isNotNull();
            verifyNoInteractions(sparkApiTool);
        }

        @Test
        @DisplayName("aiCode: For create branch, should replace {var}/{prompt} and use provided URL/Domain")
        void aiCode_create_shouldFillVars_andUseExplicitUrlDomain() {
            // Template
            ConfigInfo cfg = new ConfigInfo();
            cfg.setValue("var={var};prompt={prompt}");
            when(configInfoMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(cfg);

            // URL/Domain configuration
            ConfigInfo url = new ConfigInfo();
            url.setValue("http://code.url");
            ConfigInfo domain = new ConfigInfo();
            domain.setValue("code.domain");
            when(configInfoMapper.getByCategoryAndCode("AI_CODE", "DS_V3_url")).thenReturn(url);
            when(configInfoMapper.getByCategoryAndCode("AI_CODE", "DS_V3_domain")).thenReturn(domain);

            SseEmitter expected = new SseEmitter();
            ArgumentCaptor<String> urlCap = ArgumentCaptor.forClass(String.class);
            ArgumentCaptor<String> domainCap = ArgumentCaptor.forClass(String.class);
            ArgumentCaptor<String> msgCap = ArgumentCaptor.forClass(String.class);
            when(sparkApiTool.onceChatReturnSseByWs(urlCap.capture(), domainCap.capture(), msgCap.capture()))
                    .thenReturn(expected);

            AiCode req = new AiCode();
            req.setPrompt("P");
            req.setVar("V");
            // req.setCode("") remains empty action=create

            SseEmitter out = service.aiCode(req);

            assertThat(out).isSameAs(expected);
            assertThat(urlCap.getValue()).isEqualTo("http://code.url");
            assertThat(domainCap.getValue()).isEqualTo("code.domain");
            assertThat(msgCap.getValue()).isEqualTo("var=V;prompt=P");
        }

        @Test
        @DisplayName("aiCode: For fix branch, should extract error fragment from after 2nd '(' to second-to-last character, and use default URL/Domain")
        void aiCode_fix_shouldExtractError_andUseDefaults() {
            // Template fix
            ConfigInfo cfg = new ConfigInfo();
            cfg.setValue("ERR={errMsg}");
            when(configInfoMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(cfg);

            // URL/domain missing use SparkApiTool default constants
            when(configInfoMapper.getByCategoryAndCode("AI_CODE", "DS_V3_url")).thenReturn(null);
            when(configInfoMapper.getByCategoryAndCode("AI_CODE", "DS_V3_domain")).thenReturn(null);

            SseEmitter expected = new SseEmitter();
            ArgumentCaptor<String> urlCap = ArgumentCaptor.forClass(String.class);
            ArgumentCaptor<String> domainCap = ArgumentCaptor.forClass(String.class);
            ArgumentCaptor<String> msgCap = ArgumentCaptor.forClass(String.class);
            when(sparkApiTool.onceChatReturnSseByWs(urlCap.capture(), domainCap.capture(), msgCap.capture()))
                    .thenReturn(expected);

            // Construct error message that satisfies secLBracketIdx extraction logic
            // From after the second '(' to the second-to-last character:
            // "prefix first ValueError: bad)X" expect to extract "ValueError: bad"
            AiCode req = new AiCode();
            req.setErrMsg("prefix (first) (ValueError: bad)X");

            SseEmitter out = service.aiCode(req);

            assertThat(out).isSameAs(expected);
            assertThat(urlCap.getValue()).isEqualTo(SparkApiTool.sparkCodeUrl);
            assertThat(domainCap.getValue()).isEqualTo(SparkApiTool.CODE_DOMAIN);
            assertThat(msgCap.getValue()).isEqualTo("ERR=ValueError: bad");
        }
    }
}

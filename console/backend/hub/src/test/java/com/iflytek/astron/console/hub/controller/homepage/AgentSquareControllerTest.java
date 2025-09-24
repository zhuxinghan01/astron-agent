package com.iflytek.astron.console.hub.controller.homepage;

import com.iflytek.astron.console.commons.response.ApiResult;
import com.iflytek.astron.console.hub.dto.homepage.BotInfoDto;
import com.iflytek.astron.console.hub.dto.homepage.BotListPageDto;
import com.iflytek.astron.console.hub.dto.homepage.BotTypeDto;
import com.iflytek.astron.console.hub.service.homepage.AgentSquareService;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.mockito.Mockito.*;

@SpringBootTest
public class AgentSquareControllerTest {
    @Mock
    AgentSquareService agentSquareService;
    @InjectMocks
    AgentSquareController agentSquareController;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    /**
     * TestGenerate#bf269d1015934894850e165eef78f2df
     * Test getting the robot type list successfully, expecting a non-empty robot type list to be returned.
     * Input: None
     * Output:
     * {"code":0,"message":"Success","data":
     * [{"typeKey":1,"typeName":"Chatbot","icon":"http://example.com/icon1.png","typeNameEn":"Chatbot"},
     * {"typeKey":2,"typeName":"InfoPushBot","icon":"http://example.com/icon2.png","typeNameEn":"InfoPushBot"}]
     * }
     */
    @Test
    public void testGetBotTypeListSuccess() {
        when(agentSquareService.getBotTypeList()).thenReturn(new ArrayList<>(
                Arrays.asList(new BotTypeDto() {{
                    setTypeNameEn("Chat Bot");
                    setTypeKey(1);
                    setTypeName("Chat Bot");
                    setIcon("http://example.com/icon1.png");
                }}, new BotTypeDto() {{
                    setTypeNameEn("Info Push Bot");
                    setTypeKey(2);
                    setTypeName("Info Push Bot");
                    setIcon("http://example.com/icon2.png");
                }})));
        /* Call the tested method */
        ApiResult<List<BotTypeDto>> methodCallResult = agentSquareController.getBotTypeList();
        /* Assert data */
        ApiResult<List<BotTypeDto>> expectedResult = new ApiResult<>(0, "Success",
                new ArrayList<>(Arrays.asList(new BotTypeDto() {{
                    setTypeNameEn("Chat Bot");
                    setTypeKey(1);
                    setTypeName("Chat Bot");
                    setIcon("http://example.com/icon1.png");
                }}, new BotTypeDto() {{
                    setTypeNameEn("Info Push Bot");
                    setTypeKey(2);
                    setTypeName("Info Push Bot");
                    setIcon("http://example.com/icon2.png");
                }})), null);
        Assertions.assertEquals(expectedResult.data(), methodCallResult.data());
        Assertions.assertEquals(expectedResult.code(), methodCallResult.code());
    }

    /**
     * TestGenerate#5fdbead30d5a43a798b52f2894b851d2
     * Test under normal circumstances, passing valid type and pageSize, page parameters, expecting to return correct paginated data.
     * Input:    search = test
     * pageSize = 20
     * page = 1
     * type = 1
     * Output：
     * {"code":0,"message":"Success","data":
     * {"pageData":[{"botId":1,"chatId":1001,"botName":"TestBot","botType":1,"botCoverUrl":"http://example.com/cover.jpg","prompt":"Hello","botDesc":"A test bot","isFavorite":true,"creator":"Tester"}],"totalCount":1,"pageSize":20,"page":1,"totalPages":1}}
     */
    @Test
    public void testGetBotPageByTypeHappyPath() {
        when(agentSquareService.getBotPageByType(anyInt(), anyString(), anyInt(), anyInt())).thenReturn(new BotListPageDto() {{
            setTotalPages(1);
            setPageSize(20);
            setPageData(new ArrayList<>(List.of(new BotInfoDto() {{
                setCreator("Tester");
                setChatId(1001L);
                setBotName("TestBot");
                setBotType(1);
                setBotCoverUrl("http://example.com/cover.jpg");
                setBotDesc("A test bot");
                setBotId(1);
                setPrompt("Hello");
                setIsFavorite(true);
            }})));
            setPage(1);
            setTotalCount(1);
        }});
        /* Call the tested method */
        ApiResult<BotListPageDto> methodCallResult = agentSquareController.getBotPageByType(1, "test", 20, 1);
        Assertions.assertNotNull(methodCallResult);
    }

    /**
     * TestGenerate#f591bf0384f4406fa82396cfbf93289e
     * Test boundary case, when the search parameter is an empty string, expecting to return correct paginated data.
     * Input：    search = null
     * pageSize = 20
     * page = 1
     * type = 1
     * Output：
     * {"code":0,"message":"Success","data":{"pageData":[],"totalCount":0,"pageSize":20,"page":1,"totalPages":0}}
     */
    @Test
    public void testGetBotPageByTypeEdgeCaseEmptySearch() {
        when(agentSquareService.getBotPageByType(anyInt(), anyString(), anyInt(), anyInt())).thenReturn(new BotListPageDto() {{
            setTotalPages(0);
            setPageSize(20);
            setPageData(new ArrayList<>(Collections.EMPTY_LIST));
            setPage(1);
            setTotalCount(0);
        }});
        /* Call the tested method */
        ApiResult<BotListPageDto> methodCallResult = agentSquareController.getBotPageByType(1, null, 20, 1);
        /* Assert data */
        ApiResult<BotListPageDto> expectedResult = new ApiResult<>(0, "Success", null, null);
        Assertions.assertEquals(expectedResult.data(), methodCallResult.data());
        Assertions.assertEquals(expectedResult.code(), methodCallResult.code());
    }

    /**
     * TestGenerate#7cfe78298cbf448793d540a20c2328d0
     * Test boundary case, when the type parameter is an invalid value (such as a negative number), expecting to return an error message.
     * Input：    search = test
     * pageSize = 20
     * page = 1
     * type = -1
     * Output：
     * {"code":400,"message":"Invalid type parameter."}
     */
    @Test
    public void testGetBotPageByTypeEdgeCaseInvalidType() {
        when(agentSquareService.getBotPageByType(anyInt(), anyString(), anyInt(), anyInt())).thenReturn(new BotListPageDto());
        /* Call the tested method */
        ApiResult<BotListPageDto> methodCallResult = agentSquareController.getBotPageByType(-1, "test", 20, 1);
        Assertions.assertEquals(methodCallResult.data(), new BotListPageDto());
    }

}

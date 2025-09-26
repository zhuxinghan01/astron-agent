// package com.iflytek.astron.console.hub.controller.homepage;
//
// import com.iflytek.astron.console.commons.response.ApiResult;
// import com.iflytek.astron.console.hub.dto.homepage.BotInfoDto;
// import com.iflytek.astron.console.hub.dto.homepage.BotListPageDto;
// import com.iflytek.astron.console.hub.dto.homepage.BotTypeDto;
// import com.iflytek.astron.console.hub.service.homepage.AgentSquareService;
// import org.junit.jupiter.api.Assertions;
// import org.junit.jupiter.api.BeforeEach;
// import org.junit.jupiter.api.Test;
// import org.mockito.InjectMocks;
// import org.mockito.Mock;
// import org.mockito.MockitoAnnotations;
// import org.springframework.boot.test.context.SpringBootTest;
//
// import java.util.ArrayList;
// import java.util.Arrays;
// import java.util.Collections;
// import java.util.List;
//
// import static org.mockito.ArgumentMatchers.*;
// import static org.mockito.Mockito.when;
//
// @SpringBootTest
// public class AgentSquareControllerTest {
// @Mock
// AgentSquareService agentSquareService;
// @InjectMocks
// AgentSquareController agentSquareController;
//
// @BeforeEach
// void setUp() {
// MockitoAnnotations.openMocks(this);
// }
//
// /**
// * Test getting the robot type list successfully, expecting a non-empty robot type list to be
// returned.
// * Input: None
// * Output:
// * {"code":0,"message":"Success","data":
// *
// [{"typeKey":1,"typeName":"Chatbot","icon":"http://example.com/icon1.png","typeNameEn":"Chatbot"},
// *
// {"typeKey":2,"typeName":"InfoPushBot","icon":"http://example.com/icon2.png","typeNameEn":"InfoPushBot"}]
// * }
// */
// @Test
// public void testGetBotTypeListSuccess() {
// List<BotTypeDto> mockData = Arrays.asList(
// createBotTypeDto(1, "Chat Bot", "http://example.com/icon1.png"),
// createBotTypeDto(2, "Info Push Bot", "http://example.com/icon2.png")
// );
// when(agentSquareService.getBotTypeList()).thenReturn(mockData);
//
// ApiResult<List<BotTypeDto>> result = agentSquareController.getBotTypeList();
//
// Assertions.assertEquals(0, result.code());
// Assertions.assertEquals("Success", result.message());
// Assertions.assertEquals(mockData, result.data());
// }
//
// /**
// * Test under normal circumstances, passing valid type and pageSize, page parameters, expecting to
// return correct paginated data.
// * Input: search = test
// * pageSize = 20
// * page = 1
// * type = 1
// * Output：
// * {"code":0,"message":"Success","data":
// *
// {"pageData":[{"botId":1,"chatId":1001,"botName":"TestBot","botType":1,"botCoverUrl":"http://example.com/cover.jpg","prompt":"Hello","botDesc":"A
// test
// bot","isFavorite":true,"creator":"Tester"}],"totalCount":1,"pageSize":20,"page":1,"totalPages":1}}
// */
// @Test
// public void testGetBotPageByTypeHappyPath() {
// BotListPageDto mockPage = new BotListPageDto();
// mockPage.setTotalPages(1);
// mockPage.setPageSize(20);
// mockPage.setPage(1);
// mockPage.setTotalCount(1);
// mockPage.setPageData(Collections.singletonList(createBotInfoDto()));
//
// when(agentSquareService.getBotPageByType(eq(1), eq("test"), eq(20), eq(1))).thenReturn(mockPage);
//
// ApiResult<BotListPageDto> result = agentSquareController.getBotPageByType(1, "test", 20, 1);
//
// Assertions.assertNotNull(result);
// Assertions.assertEquals(0, result.code());
// Assertions.assertEquals("Success", result.message());
// Assertions.assertEquals(mockPage, result.data());
// }
//
// /**
// * Test boundary case, when the search parameter is an empty string, expecting to return correct
// paginated data.
// * Input： search = null
// * pageSize = 20
// * page = 1
// * type = 1
// * Output：
// *
// {"code":0,"message":"Success","data":{"pageData":[],"totalCount":0,"pageSize":20,"page":1,"totalPages":0}}
// */
// @Test
// public void testGetBotPageByTypeEdgeCaseEmptySearch() {
// BotListPageDto mockPage = new BotListPageDto();
// mockPage.setTotalPages(0);
// mockPage.setPageSize(20);
// mockPage.setPage(1);
// mockPage.setTotalCount(0);
// mockPage.setPageData(new ArrayList<>());
//
// when(agentSquareService.getBotPageByType(eq(1), isNull(), eq(20), eq(1))).thenReturn(mockPage);
//
// ApiResult<BotListPageDto> result = agentSquareController.getBotPageByType(1, null, 20, 1);
//
// Assertions.assertNotNull(result);
// Assertions.assertEquals(0, result.code());
// Assertions.assertEquals("Success", result.message());
// Assertions.assertEquals(mockPage, result.data());
// }
//
// /**
// * Test boundary case, when the type parameter is an invalid value (such as a negative number),
// expecting to return an error message.
// * Input： search = test
// * pageSize = 20
// * page = 1
// * type = -1
// * Output：
// * {"code":400,"message":"Invalid type parameter."}
// */
// @Test
// public void testGetBotPageByTypeEdgeCaseInvalidType() {
// ApiResult<BotListPageDto> expectedError = new ApiResult<>(400, "Invalid type parameter.", null,
// null);
//
// when(agentSquareService.getBotPageByType(eq(-1), anyString(), anyInt(),
// anyInt())).thenReturn(null);
//
// ApiResult<BotListPageDto> result = agentSquareController.getBotPageByType(-1, "test", 20, 1);
//
// Assertions.assertEquals(expectedError.code(), result.code());
// Assertions.assertEquals(expectedError.message(), result.message());
// Assertions.assertNull(result.data());
// }
//
// private BotTypeDto createBotTypeDto(int typeKey, String typeName, String iconUrl) {
// BotTypeDto dto = new BotTypeDto();
// dto.setTypeKey(typeKey);
// dto.setTypeName(typeName);
// dto.setTypeNameEn(typeName);
// dto.setIcon(iconUrl);
// return dto;
// }
//
// private BotInfoDto createBotInfoDto() {
// BotInfoDto dto = new BotInfoDto();
// dto.setBotId(1);
// dto.setChatId(1001L);
// dto.setBotName("TestBot");
// dto.setBotType(1);
// dto.setBotCoverUrl("http://example.com/cover.jpg");
// dto.setPrompt("Hello");
// dto.setBotDesc("A test bot");
// dto.setIsFavorite(true);
// dto.setCreator("Tester");
// return dto;
// }
// }
//
//

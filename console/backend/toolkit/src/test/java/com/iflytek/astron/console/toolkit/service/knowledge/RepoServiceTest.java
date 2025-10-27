package com.iflytek.astron.console.toolkit.service.knowledge;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.iflytek.astron.console.commons.config.JwtClaimsFilter;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.service.data.IDatasetFileService;
import com.iflytek.astron.console.toolkit.common.constant.ProjectContent;
import com.iflytek.astron.console.toolkit.config.properties.ApiUrl;
import com.iflytek.astron.console.toolkit.config.properties.RepoAuthorizedConfig;
import com.iflytek.astron.console.toolkit.entity.table.repo.Repo;
import com.iflytek.astron.console.toolkit.entity.table.repo.FileInfoV2;
import com.iflytek.astron.console.toolkit.entity.table.repo.HitTestHistory;
import com.iflytek.astron.console.toolkit.entity.table.repo.FileDirectoryTree;
import com.iflytek.astron.console.toolkit.entity.dto.RepoDto;
import com.iflytek.astron.console.toolkit.entity.dto.SparkBotVO;
import com.iflytek.astron.console.toolkit.entity.common.PageData;
import com.iflytek.astron.console.toolkit.entity.core.knowledge.QueryRequest;
import com.iflytek.astron.console.toolkit.entity.core.knowledge.KnowledgeResponse;
import com.iflytek.astron.console.toolkit.entity.core.knowledge.QueryRespData;
import com.iflytek.astron.console.toolkit.entity.core.knowledge.ChunkInfo;
import com.iflytek.astron.console.toolkit.entity.vo.knowledge.RepoVO;
import com.iflytek.astron.console.toolkit.handler.KnowledgeV2ServiceCallHandler;
import com.iflytek.astron.console.toolkit.handler.UserInfoManagerHandler;
import com.iflytek.astron.console.commons.util.space.SpaceInfoUtil;
import com.iflytek.astron.console.toolkit.mapper.ConfigInfoMapper;
import com.iflytek.astron.console.toolkit.mapper.bot.SparkBotMapper;
import com.iflytek.astron.console.toolkit.mapper.knowledge.KnowledgeMapper;
import com.iflytek.astron.console.toolkit.mapper.relation.FlowRepoRelMapper;
import com.iflytek.astron.console.toolkit.mapper.repo.FileInfoV2Mapper;
import com.iflytek.astron.console.toolkit.mapper.repo.RepoMapper;
import com.iflytek.astron.console.toolkit.service.bot.BotRepoRelService;
import com.iflytek.astron.console.toolkit.service.bot.BotRepoSubscriptService;
import com.iflytek.astron.console.toolkit.service.extra.AppService;
import com.iflytek.astron.console.toolkit.service.extra.OpenPlatformService;
import com.iflytek.astron.console.toolkit.service.group.GroupVisibilityService;
import com.iflytek.astron.console.toolkit.service.repo.FileDirectoryTreeService;
import com.iflytek.astron.console.toolkit.service.repo.FileInfoV2Service;
import com.iflytek.astron.console.toolkit.service.repo.HitTestHistoryService;
import com.iflytek.astron.console.toolkit.service.repo.RepoService;
import com.iflytek.astron.console.toolkit.tool.DataPermissionCheckTool;
import com.iflytek.astron.console.toolkit.util.S3Util;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import com.alibaba.fastjson2.JSONObject;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for RepoService
 *
 * <p>
 * Technology Stack: JUnit5 + Mockito + AssertJ
 * </p>
 *
 * <p>
 * Coverage Requirements:
 * </p>
 * <ul>
 * <li>JaCoCo Statement Coverage >= 80%</li>
 * <li>JaCoCo Branch Coverage >= 90%</li>
 * <li>High PIT Mutation Test Score</li>
 * <li>Covers normal flows, edge cases, and exceptions</li>
 * </ul>
 *
 * @author AI Assistant
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("RepoService Unit Tests")
class RepoServiceTest {

    @Mock
    private RepoMapper repoMapper;

    @Mock
    private ConfigInfoMapper configInfoMapper;

    @Mock
    private RepoAuthorizedConfig repoAuthorizedConfig;

    @Mock
    private KnowledgeV2ServiceCallHandler knowledgeV2ServiceCallHandler;

    @Mock
    private BotRepoSubscriptService botRepoSubscriptService;

    @Mock
    private BotRepoRelService botRepoRelService;

    @Mock
    private HitTestHistoryService historyService;

    @Mock
    private FileInfoV2Service fileInfoV2Service;

    @Mock
    private FileInfoV2Mapper fileInfoV2Mapper;

    @Mock
    private IDatasetFileService datasetFileService;

    @Mock
    private FileDirectoryTreeService directoryTreeService;

    @Mock
    private S3Util s3UtilClient;

    @Mock
    private SparkBotMapper sparkBotMapper;

    @Mock
    private GroupVisibilityService groupVisibilityService;

    @Mock
    private DataPermissionCheckTool dataPermissionCheckTool;

    @Mock
    private OpenPlatformService openPlatformService;

    @Mock
    private FlowRepoRelMapper flowRepoRelMapper;

    @Mock
    private KnowledgeMapper knowledgeMapper;

    @Mock
    private ApiUrl apiUrl;

    @InjectMocks
    private RepoService repoService;

    private RepoVO mockRepoVO;
    private Repo mockRepo;
    private MockHttpServletRequest mockRequest;

    // Static mocks for utility classes
    private MockedStatic<UserInfoManagerHandler> userInfoManagerHandlerMock;
    private MockedStatic<SpaceInfoUtil> spaceInfoUtilMock;

    /**
     * Set up test fixtures before each test method.
     * Initializes common test data including mock repository objects and request context.
     */
    @BeforeEach
    void setUp() {
        // Mock static utility methods
        userInfoManagerHandlerMock = mockStatic(UserInfoManagerHandler.class);
        userInfoManagerHandlerMock.when(UserInfoManagerHandler::getUserId).thenReturn("user-001");

        spaceInfoUtilMock = mockStatic(SpaceInfoUtil.class);
        spaceInfoUtilMock.when(SpaceInfoUtil::getSpaceId).thenReturn(null);  // Default to null (no space)

        // Initialize mock HttpServletRequest and set up RequestContextHolder
        mockRequest = new MockHttpServletRequest();
        mockRequest.setAttribute(JwtClaimsFilter.USER_ID_ATTRIBUTE, "user-001");
        ServletRequestAttributes attributes = new ServletRequestAttributes(mockRequest);
        RequestContextHolder.setRequestAttributes(attributes);

        // Set baseMapper for ServiceImpl - Required for MyBatis-Plus
        ReflectionTestUtils.setField(repoService, "baseMapper", repoMapper);

        // Initialize mock RepoVO
        mockRepoVO = new RepoVO();
        mockRepoVO.setName("Test Repository");
        mockRepoVO.setDesc("Test Description");
        mockRepoVO.setTag("AIUI-RAG2");  // Use correct tag value for validation
        mockRepoVO.setAvatarIcon("icon-url");
        mockRepoVO.setAvatarColor("#FF0000");
        mockRepoVO.setVisibility(0);
        mockRepoVO.setAppId("app-001");
        mockRepoVO.setSource(0);
        mockRepoVO.setUids(new ArrayList<>());

        // Initialize mock Repo
        mockRepo = new Repo();
        mockRepo.setId(1L);
        mockRepo.setName("Test Repository");
        mockRepo.setDescription("Test Description");
        mockRepo.setTag("AIUI-RAG2");  // Use correct tag value for validation
        mockRepo.setUserId("user-001");
        mockRepo.setCoreRepoId("core-repo-001");
        mockRepo.setOuterRepoId("outer-repo-001");
        mockRepo.setStatus(ProjectContent.REPO_STATUS_CREATED);
        mockRepo.setDeleted(false);
        mockRepo.setVisibility(0);
        mockRepo.setEnableAudit(false);
        mockRepo.setIcon("icon-url");
        mockRepo.setColor("#FF0000");
        mockRepo.setCreateTime(new Date());
        mockRepo.setUpdateTime(new Date());
    }

    /**
     * Clean up after each test method.
     * Clears the RequestContextHolder and closes static mocks to avoid side effects between tests.
     */
    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();

        // Close static mocks to prevent memory leaks
        if (userInfoManagerHandlerMock != null) {
            userInfoManagerHandlerMock.close();
        }
        if (spaceInfoUtilMock != null) {
            spaceInfoUtilMock.close();
        }
    }

    /**
     * Test cases for the createRepo method.
     * Validates repository creation functionality including success scenarios and error handling.
     */
    @Nested
    @DisplayName("createRepo Tests")
    class CreateRepoTests {

        /**
         * Test successful repository creation with AIUI tag.
         */
        @Test
        @DisplayName("Create repository successfully with AIUI tag")
        void testCreateRepo_Success_WithAIUI() {
            // Given
            mockRepoVO.setTag("AIUI-RAG2");

            // Mock selectOne with two parameters (wrapper, throwEx) - MyBatis-Plus uses this signature
            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenAnswer(invocation -> {
                Repo repo = invocation.getArgument(0);
                repo.setId(1L);
                return 1;
            });
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.createRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getName()).isEqualTo("Test Repository");
            assertThat(result.getTag()).isEqualTo("AIUI-RAG2");
            assertThat(result.getDeleted()).isFalse();
            verify(repoMapper, times(1)).insert(any(Repo.class));
            verify(groupVisibilityService, times(1)).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());
        }

        /**
         * Test successful repository creation with CBG tag.
         */
        @Test
        @DisplayName("Create repository successfully with CBG tag")
        void testCreateRepo_Success_WithCBG() {
            // Given
            mockRepoVO.setTag("CBG-RAG");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenAnswer(invocation -> {
                Repo repo = invocation.getArgument(0);
                repo.setId(1L);
                return 1;
            });
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.createRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getTag()).isEqualTo("CBG-RAG");
            verify(repoMapper, times(1)).insert(any(Repo.class));
        }

        /**
         * Test repository creation with duplicate name.
         */
        @Test
        @DisplayName("Create repository - duplicate name")
        void testCreateRepo_DuplicateName() {
            // Given
            Repo existingRepo = new Repo();
            existingRepo.setId(1L);
            existingRepo.setName("Test Repository");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(existingRepo);

            // When & Then
            assertThatThrownBy(() -> repoService.createRepo(mockRepoVO))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NAME_DUPLICATE);

            verify(repoMapper, never()).insert(any(Repo.class));
        }

        /**
         * Test repository creation with invalid tag.
         */
        @Test
        @DisplayName("Create repository - invalid tag")
        void testCreateRepo_InvalidTag() {
            // Given
            mockRepoVO.setTag("INVALID_TAG");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> repoService.createRepo(mockRepoVO))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_TYPE_NOT_MATCH);

            verify(repoMapper, never()).insert(any(Repo.class));
        }

        /**
         * Test repository creation with custom outer repo ID.
         */
        @Test
        @DisplayName("Create repository - with custom outer repo ID")
        void testCreateRepo_WithCustomOuterRepoId() {
            // Given
            mockRepoVO.setOuterRepoId("custom-repo-id");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenAnswer(invocation -> {
                Repo repo = invocation.getArgument(0);
                repo.setId(1L);
                return 1;
            });
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.createRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getCoreRepoId()).isEqualTo("custom-repo-id");
            assertThat(result.getOuterRepoId()).isEqualTo("custom-repo-id");
            verify(repoMapper, times(1)).insert(any(Repo.class));
        }

        /**
         * Test repository creation with visibility set.
         */
        @Test
        @DisplayName("Create repository - with visibility set")
        void testCreateRepo_WithVisibility() {
            // Given
            mockRepoVO.setVisibility(1);
            mockRepoVO.setUids(Arrays.asList("user-001", "user-002"));

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenAnswer(invocation -> {
                Repo repo = invocation.getArgument(0);
                repo.setId(1L);
                return 1;
            });
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.createRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getVisibility()).isEqualTo(1);
            verify(groupVisibilityService, times(1)).setRepoVisibility(eq(1L), eq(1), eq(1), anyList());
        }

        /**
         * Test repository creation with null source (default to 0).
         */
        @Test
        @DisplayName("Create repository - null source defaults to 0")
        void testCreateRepo_NullSource_DefaultsToZero() {
            // Given
            mockRepoVO.setSource(null);

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenAnswer(invocation -> {
                Repo repo = invocation.getArgument(0);
                repo.setId(1L);
                assertThat(repo.getSource()).isEqualTo(0);
                return 1;
            });
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.createRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            verify(repoMapper, times(1)).insert(any(Repo.class));
        }
    }

    /**
     * Test cases for the getOnly methods.
     * Validates repository query functionality with different wrapper types.
     */
    @Nested
    @DisplayName("getOnly Tests")
    class GetOnlyTests {

        /**
         * Test getOnly with QueryWrapper successfully.
         */
        @Test
        @DisplayName("getOnly with QueryWrapper - success")
        void testGetOnly_QueryWrapper_Success() {
            // Given
            QueryWrapper<Repo> wrapper = new QueryWrapper<>();
            wrapper.eq("name", "Test Repository");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(mockRepo);

            // When
            Repo result = repoService.getOnly(wrapper);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getName()).isEqualTo("Test Repository");
            verify(repoMapper, times(1)).selectOne(any(), anyBoolean());
        }

        /**
         * Test getOnly with QueryWrapper - no result found.
         */
        @Test
        @DisplayName("getOnly with QueryWrapper - no result")
        void testGetOnly_QueryWrapper_NoResult() {
            // Given
            QueryWrapper<Repo> wrapper = new QueryWrapper<>();
            wrapper.eq("name", "Nonexistent Repository");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);

            // When
            Repo result = repoService.getOnly(wrapper);

            // Then
            assertThat(result).isNull();
            verify(repoMapper, times(1)).selectOne(any(), anyBoolean());
        }

        /**
         * Test getOnly with LambdaQueryWrapper successfully.
         */
        @Test
        @DisplayName("getOnly with LambdaQueryWrapper - success")
        void testGetOnly_LambdaQueryWrapper_Success() {
            // Given
            LambdaQueryWrapper<Repo> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(Repo::getName, "Test Repository");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(mockRepo);

            // When
            Repo result = repoService.getOnly(wrapper);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getName()).isEqualTo("Test Repository");
            verify(repoMapper, times(1)).selectOne(any(), anyBoolean());
        }

        /**
         * Test getOnly with LambdaQueryWrapper - no result found.
         */
        @Test
        @DisplayName("getOnly with LambdaQueryWrapper - no result")
        void testGetOnly_LambdaQueryWrapper_NoResult() {
            // Given
            LambdaQueryWrapper<Repo> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(Repo::getName, "Nonexistent Repository");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);

            // When
            Repo result = repoService.getOnly(wrapper);

            // Then
            assertThat(result).isNull();
            verify(repoMapper, times(1)).selectOne(any(), anyBoolean());
        }
    }

    /**
     * Test cases for edge cases and boundary conditions.
     */
    @Nested
    @DisplayName("Edge Case Tests")
    class EdgeCaseTests {

        /**
         * Test createRepo with null RepoVO.
         */
        @Test
        @DisplayName("Create repository - null RepoVO")
        void testCreateRepo_NullRepoVO() {
            // When & Then
            assertThatThrownBy(() -> repoService.createRepo(null))
                    .isInstanceOf(NullPointerException.class);
        }

        /**
         * Test createRepo with empty name.
         */
        @Test
        @DisplayName("Create repository - empty name")
        void testCreateRepo_EmptyName() {
            // Given
            mockRepoVO.setName("");

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenAnswer(invocation -> {
                Repo repo = invocation.getArgument(0);
                repo.setId(1L);
                return 1;
            });
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.createRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            verify(repoMapper, times(1)).insert(any(Repo.class));
        }

        /**
         * Test createRepo with very long name.
         */
        @Test
        @DisplayName("Create repository - very long name")
        void testCreateRepo_VeryLongName() {
            // Given
            mockRepoVO.setName("A".repeat(500));

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenAnswer(invocation -> {
                Repo repo = invocation.getArgument(0);
                repo.setId(1L);
                return 1;
            });
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.createRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            verify(repoMapper, times(1)).insert(any(Repo.class));
        }

        /**
         * Test createRepo with null tag.
         */
        @Test
        @DisplayName("Create repository - null tag")
        void testCreateRepo_NullTag() {
            // Given
            mockRepoVO.setTag(null);

            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> repoService.createRepo(mockRepoVO))
                    .isInstanceOf(BusinessException.class);

            verify(repoMapper, never()).insert(any(Repo.class));
        }
    }

    /**
     * Test cases for exception scenarios.
     */
    @Nested
    @DisplayName("Exception Tests")
    class ExceptionTests {

        /**
         * Test createRepo when database insert fails.
         */
        @Test
        @DisplayName("Create repository - database insert fails")
        void testCreateRepo_DatabaseInsertFails() {
            // Given
            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenThrow(new RuntimeException("Database error"));

            // When & Then
            assertThatThrownBy(() -> repoService.createRepo(mockRepoVO))
                    .isInstanceOf(RuntimeException.class)
                    .hasMessageContaining("Database error");

            verify(groupVisibilityService, never()).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());
        }

        /**
         * Test createRepo when visibility service fails.
         */
        @Test
        @DisplayName("Create repository - visibility service fails")
        void testCreateRepo_VisibilityServiceFails() {
            // Given
            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.insert(any(Repo.class))).thenAnswer(invocation -> {
                Repo repo = invocation.getArgument(0);
                repo.setId(1L);  // Must set ID for visibility service call
                return 1;
            });
            doThrow(new RuntimeException("Visibility service error"))
                    .when(groupVisibilityService)
                    .setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When & Then
            assertThatThrownBy(() -> repoService.createRepo(mockRepoVO))
                    .isInstanceOf(RuntimeException.class)
                    .hasMessageContaining("Visibility service error");

            verify(repoMapper, times(1)).insert(any(Repo.class));
        }

        /**
         * Test getOnly with QueryWrapper when database query fails.
         */
        @Test
        @DisplayName("getOnly with QueryWrapper - database query fails")
        void testGetOnly_QueryWrapper_DatabaseQueryFails() {
            // Given
            QueryWrapper<Repo> wrapper = new QueryWrapper<>();
            wrapper.eq("name", "Test Repository");

            when(repoMapper.selectOne(any(), anyBoolean()))
                    .thenThrow(new RuntimeException("Database query error"));

            // When & Then
            assertThatThrownBy(() -> repoService.getOnly(wrapper))
                    .isInstanceOf(RuntimeException.class)
                    .hasMessageContaining("Database query error");
        }
    }

    /**
     * Test cases for the updateRepo method.
     */
    @Nested
    @DisplayName("updateRepo Tests")
    class UpdateRepoTests {

        /**
         * Test successful repository update.
         */
        @Test
        @DisplayName("Update repository successfully")
        void testUpdateRepo_Success() {
            // Given
            mockRepoVO.setId(1L);
            mockRepoVO.setName("Updated Repository");
            mockRepoVO.setDesc("Updated Description");

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.updateById(any(Repo.class))).thenReturn(1);
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.updateRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getName()).isEqualTo("Updated Repository");
            assertThat(result.getDescription()).isEqualTo("Updated Description");
            verify(repoMapper, times(1)).updateById(any(Repo.class));
            verify(groupVisibilityService, times(1)).setRepoVisibility(eq(1L), eq(1), eq(0), anyList());
        }

        /**
         * Test update repository - repository does not exist.
         */
        @Test
        @DisplayName("Update repository - repository not exist")
        void testUpdateRepo_RepoNotExist() {
            // Given
            mockRepoVO.setId(999L);

            when(repoMapper.selectById(999L)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> repoService.updateRepo(mockRepoVO))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NOT_EXIST);

            verify(repoMapper, never()).updateById(any(Repo.class));
        }

        /**
         * Test update repository - duplicate name with another repository.
         */
        @Test
        @DisplayName("Update repository - duplicate name")
        void testUpdateRepo_DuplicateName() {
            // Given
            mockRepoVO.setId(1L);
            mockRepoVO.setName("Duplicate Name");

            Repo anotherRepo = new Repo();
            anotherRepo.setId(2L);
            anotherRepo.setName("Duplicate Name");

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(anotherRepo);

            // When & Then
            assertThatThrownBy(() -> repoService.updateRepo(mockRepoVO))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NAME_DUPLICATE);

            verify(repoMapper, never()).updateById(any(Repo.class));
        }

        /**
         * Test update repository - same name as current repository (should succeed).
         */
        @Test
        @DisplayName("Update repository - same name as self")
        void testUpdateRepo_SameNameAsSelf() {
            // Given
            mockRepoVO.setId(1L);
            mockRepoVO.setName("Test Repository");

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(mockRepo);
            when(repoMapper.updateById(any(Repo.class))).thenReturn(1);
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.updateRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            verify(repoMapper, times(1)).updateById(any(Repo.class));
        }

        /**
         * Test update repository with visibility change.
         */
        @Test
        @DisplayName("Update repository - change visibility")
        void testUpdateRepo_ChangeVisibility() {
            // Given
            mockRepoVO.setId(1L);
            mockRepoVO.setVisibility(1);
            mockRepoVO.setUids(Arrays.asList("user-002", "user-003"));

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(repoMapper.selectOne(any(), anyBoolean())).thenReturn(null);
            when(repoMapper.updateById(any(Repo.class))).thenReturn(1);
            doNothing().when(groupVisibilityService).setRepoVisibility(anyLong(), anyInt(), anyInt(), anyList());

            // When
            Repo result = repoService.updateRepo(mockRepoVO);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getVisibility()).isEqualTo(1);
            verify(groupVisibilityService, times(1)).setRepoVisibility(eq(1L), eq(1), eq(1), anyList());
        }
    }

    /**
     * Test cases for the setTop method.
     */
    @Nested
    @DisplayName("setTop Tests")
    class SetTopTests {

        /**
         * Test setTop - set repository to top.
         */
        @Test
        @DisplayName("setTop - set to top")
        void testSetTop_SetToTop() {
            // Given
            mockRepo.setIsTop(false);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(repoMapper.updateById(any(Repo.class))).thenReturn(1);

            // When
            repoService.setTop(1L);

            // Then
            verify(repoMapper, times(1)).updateById(any(Repo.class));
            assertThat(mockRepo.getIsTop()).isTrue();
        }

        /**
         * Test setTop - unset repository from top.
         */
        @Test
        @DisplayName("setTop - unset from top")
        void testSetTop_UnsetFromTop() {
            // Given
            mockRepo.setIsTop(true);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(repoMapper.updateById(any(Repo.class))).thenReturn(1);

            // When
            repoService.setTop(1L);

            // Then
            verify(repoMapper, times(1)).updateById(any(Repo.class));
            assertThat(mockRepo.getIsTop()).isFalse();
        }

        /**
         * Test setTop - repository does not exist.
         */
        @Test
        @DisplayName("setTop - repository not found")
        void testSetTop_RepoNotFound() {
            // Given
            when(repoMapper.selectById(999L)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> repoService.setTop(999L))
                    .isInstanceOf(NullPointerException.class);

            verify(repoMapper, never()).updateById(any(Repo.class));
        }
    }

    /**
     * Test cases for the enableRepo method.
     */
    @Nested
    @DisplayName("enableRepo Tests")
    class EnableRepoTests {

        /**
         * Test enableRepo - enable from created status.
         */
        @Test
        @DisplayName("enableRepo - enable from created status")
        void testEnableRepo_EnableFromCreated() {
            // Given
            mockRepo.setStatus(ProjectContent.REPO_STATUS_CREATED);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            // When
            repoService.enableRepo(1L, 0);

            // Then
            verify(repoMapper, times(1)).selectById(1L);
        }

        /**
         * Test enableRepo - enable from unpublished status.
         */
        @Test
        @DisplayName("enableRepo - enable from unpublished status")
        void testEnableRepo_EnableFromUnpublished() {
            // Given
            mockRepo.setStatus(ProjectContent.REPO_STATUS_UNPUBLISHED);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            // When
            repoService.enableRepo(1L, 1);

            // Then
            verify(repoMapper, times(1)).selectById(1L);
        }

        /**
         * Test enableRepo - illegal status transition.
         */
        @Test
        @DisplayName("enableRepo - illegal status transition")
        void testEnableRepo_IllegalStatusTransition() {
            // Given
            mockRepo.setStatus(ProjectContent.REPO_STATUS_CREATED);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            // When & Then
            assertThatThrownBy(() -> repoService.enableRepo(1L, 1))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_STATUS_ILLEGAL);
        }

        /**
         * Test enableRepo - repository does not exist.
         */
        @Test
        @DisplayName("enableRepo - repository not exist")
        void testEnableRepo_RepoNotExist() {
            // Given
            when(repoMapper.selectById(999L)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> repoService.enableRepo(999L, 1))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NOT_EXIST);
        }
    }

    /**
     * Test cases for the listFiles method.
     */
    @Nested
    @DisplayName("listFiles Tests")
    class ListFilesTests {

        /**
         * Test listFiles - successful retrieval.
         */
        @Test
        @DisplayName("listFiles - success")
        void testListFiles_Success() {
            // Given
            List<FileInfoV2> mockFiles = new ArrayList<>();
            FileInfoV2 file1 = new FileInfoV2();
            file1.setId(1L);
            file1.setName("file1.txt");
            mockFiles.add(file1);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(fileInfoV2Mapper.listFiles(1L)).thenReturn(mockFiles);

            // When
            Object result = repoService.listFiles(1L);

            // Then
            assertThat(result).isNotNull();
            assertThat(result).isInstanceOf(List.class);
            verify(fileInfoV2Mapper, times(1)).listFiles(1L);
        }

        /**
         * Test listFiles - empty list.
         */
        @Test
        @DisplayName("listFiles - empty list")
        void testListFiles_EmptyList() {
            // Given
            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(fileInfoV2Mapper.listFiles(1L)).thenReturn(new ArrayList<>());

            // When
            Object result = repoService.listFiles(1L);

            // Then
            assertThat(result).isNotNull();
            assertThat(result).isInstanceOf(List.class);
            assertThat(((List<?>) result)).isEmpty();
        }
    }

    /**
     * Test cases for the deleteRepo method.
     */
    @Nested
    @DisplayName("deleteRepo Tests")
    class DeleteRepoTests {

        /**
         * Test deleteRepo - successful deletion.
         */
        @Test
        @DisplayName("deleteRepo - success")
        void testDeleteRepo_Success() {
            // Given
            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(botRepoRelService.count(any())).thenReturn(0L);
            when(repoMapper.updateById(any(Repo.class))).thenReturn(1);
            when(fileInfoV2Mapper.getFileInfoV2ByRepoId(1L)).thenReturn(new ArrayList<>());

            // When
            Object result = repoService.deleteRepo(1L, "AIUI-RAG2", mockRequest);

            // Then
            assertThat(result).isNotNull();
            verify(repoMapper, times(1)).updateById(any(Repo.class));
            assertThat(mockRepo.getDeleted()).isTrue();
        }

        /**
         * Test deleteRepo - repository not exist.
         */
        @Test
        @DisplayName("deleteRepo - repository not exist")
        void testDeleteRepo_RepoNotExist() {
            // Given
            when(repoMapper.selectById(999L)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> repoService.deleteRepo(999L, "AIUI-RAG2", mockRequest))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NOT_EXIST);
        }

        /**
         * Test deleteRepo - repository in use by bots.
         */
        @Test
        @DisplayName("deleteRepo - repository in use")
        void testDeleteRepo_InUse() {
            // Given
            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(botRepoRelService.count(any())).thenReturn(1L);

            // When & Then
            assertThatThrownBy(() -> repoService.deleteRepo(1L, "AIUI-RAG2", mockRequest))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_DELETE_FAILED_BOT_USED);

            verify(repoMapper, never()).updateById(any(Repo.class));
        }
    }

    /**
     * Test cases for the updateRepoStatus method.
     */
    @Nested
    @DisplayName("updateRepoStatus Tests")
    class UpdateRepoStatusTests {

        /**
         * Test updateRepoStatus - always returns true (logic commented out).
         */
        @Test
        @DisplayName("updateRepoStatus - returns true")
        void testUpdateRepoStatus_ReturnsTrue() {
            // Given
            mockRepoVO.setOperType(2);

            // When
            boolean result = repoService.updateRepoStatus(mockRepoVO);

            // Then
            assertThat(result).isTrue();
        }
    }

    /**
     * Test cases for the listHitTestHistoryByPage method.
     */
    @Nested
    @DisplayName("listHitTestHistoryByPage Tests")
    class ListHitTestHistoryByPageTests {

        /**
         * Test listHitTestHistoryByPage - successful retrieval.
         */
        @Test
        @DisplayName("listHitTestHistoryByPage - success")
        void testListHitTestHistoryByPage_Success() {
            // Given
            List<HitTestHistory> mockHistoryList = new ArrayList<>();
            HitTestHistory history1 = new HitTestHistory();
            history1.setId(1L);
            history1.setQuery("test query");
            mockHistoryList.add(history1);

            when(historyService.count(any(LambdaQueryWrapper.class))).thenReturn(1L);
            when(historyService.list(any(LambdaQueryWrapper.class))).thenReturn(mockHistoryList);

            // When
            PageData<HitTestHistory> result = repoService.listHitTestHistoryByPage(1L, 1, 10);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getTotalCount()).isEqualTo(1L);
            assertThat(result.getPageData()).hasSize(1);
        }

        /**
         * Test listHitTestHistoryByPage - empty list.
         */
        @Test
        @DisplayName("listHitTestHistoryByPage - empty list")
        void testListHitTestHistoryByPage_EmptyList() {
            // Given
            when(historyService.count(any(LambdaQueryWrapper.class))).thenReturn(0L);
            when(historyService.list(any(LambdaQueryWrapper.class))).thenReturn(new ArrayList<>());

            // When
            PageData<HitTestHistory> result = repoService.listHitTestHistoryByPage(1L, 1, 10);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getTotalCount()).isEqualTo(0L);
            assertThat(result.getPageData()).isEmpty();
        }
    }

    /**
     * Test cases for the getRepoUseStatus method.
     */
    @Nested
    @DisplayName("getRepoUseStatus Tests")
    class GetRepoUseStatusTests {

        /**
         * Test getRepoUseStatus - repository is in use.
         */
        @Test
        @DisplayName("getRepoUseStatus - in use")
        void testGetRepoUseStatus_InUse() {
            // Given
            List<SparkBotVO> mockBots = new ArrayList<>();
            SparkBotVO bot = new SparkBotVO();
            bot.setUuid("bot-001");
            mockBots.add(bot);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            when(sparkBotMapper.listSparkBotByRepoId(1L, "user-001")).thenReturn(mockBots);
            when(flowRepoRelMapper.selectList(any())).thenReturn(new ArrayList<>());
            when(datasetFileService.getMaasDataset(1L)).thenReturn(new ArrayList<>());

            // When
            Object result = repoService.getRepoUseStatus(1L, mockRequest);

            // Then
            assertThat(result).isNotNull();
            assertThat(result).isInstanceOf(Boolean.class);
            assertThat((Boolean) result).isTrue();
        }

        /**
         * Test getRepoUseStatus - repository is not in use.
         */
        @Test
        @DisplayName("getRepoUseStatus - not in use")
        void testGetRepoUseStatus_NotInUse() {
            // Given
            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            when(sparkBotMapper.listSparkBotByRepoId(1L, "user-001")).thenReturn(new ArrayList<>());
            when(flowRepoRelMapper.selectList(any())).thenReturn(new ArrayList<>());
            when(datasetFileService.getMaasDataset(1L)).thenReturn(new ArrayList<>());

            // When
            Object result = repoService.getRepoUseStatus(1L, mockRequest);

            // Then
            assertThat(result).isNotNull();
            assertThat(result).isInstanceOf(Boolean.class);
            assertThat((Boolean) result).isFalse();
        }
    }

    /**
     * Test cases for the getDetail method.
     */
    @Nested
    @DisplayName("getDetail Tests")
    class GetDetailTests {

        /**
         * Test getDetail - successful retrieval for AIUI tag.
         */
        @Test
        @DisplayName("getDetail - success with AIUI tag")
        void testGetDetail_Success_AIUITag() {
            // Given
            List<FileInfoV2> mockFiles = new ArrayList<>();
            FileInfoV2 file1 = new FileInfoV2();
            file1.setId(1L);
            file1.setUuid("file-uuid-001");
            file1.setCharCount(1000L);
            mockFiles.add(file1);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            doNothing().when(dataPermissionCheckTool).checkRepoVisible(any(Repo.class));
            when(s3UtilClient.getS3Prefix()).thenReturn("https://s3.example.com/");
            when(sparkBotMapper.listSparkBotByRepoId(1L, "user-001")).thenReturn(new ArrayList<>());
            when(fileInfoV2Mapper.getFileInfoV2ByRepoId(1L)).thenReturn(mockFiles);
            when(knowledgeMapper.countByFileId("file-uuid-001")).thenReturn(10L);

            // When
            RepoDto result = repoService.getDetail(1L, "AIUI-RAG2", mockRequest);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getFileCount()).isEqualTo(1L);
            assertThat(result.getCharCount()).isEqualTo(1000L);
            assertThat(result.getKnowledgeCount()).isEqualTo(10L);
            assertThat(result.getTag()).isEqualTo("AIUI-RAG2");
        }

        /**
         * Test getDetail - repository not exist.
         */
        @Test
        @DisplayName("getDetail - repository not exist")
        void testGetDetail_RepoNotExist() {
            // Given
            when(repoMapper.selectById(999L)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> repoService.getDetail(999L, "AIUI-RAG2", mockRequest))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NOT_EXIST);
        }

        /**
         * Test getDetail - empty file list.
         */
        @Test
        @DisplayName("getDetail - empty file list")
        void testGetDetail_EmptyFileList() {
            // Given
            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            doNothing().when(dataPermissionCheckTool).checkRepoVisible(any(Repo.class));
            when(s3UtilClient.getS3Prefix()).thenReturn("https://s3.example.com/");
            when(sparkBotMapper.listSparkBotByRepoId(1L, "user-001")).thenReturn(new ArrayList<>());
            when(fileInfoV2Mapper.getFileInfoV2ByRepoId(1L)).thenReturn(new ArrayList<>());

            // When
            RepoDto result = repoService.getDetail(1L, "AIUI-RAG2", mockRequest);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getFileCount()).isEqualTo(0L);
            assertThat(result.getCharCount()).isEqualTo(0L);
            assertThat(result.getKnowledgeCount()).isEqualTo(0L);
        }
    }

    /**
     * Test cases for the hitTest method.
     */
    @Nested
    @DisplayName("hitTest Tests")
    class HitTestTests {

        /**
         * Test hitTest - successful hit test.
         */
        @Test
        @DisplayName("hitTest - success")
        void testHitTest_Success() {
            // Given
            FileDirectoryTree tree1 = new FileDirectoryTree();
            tree1.setAppId("1");
            tree1.setFileId(1L);
            tree1.setIsFile(1);
            tree1.setHitCount(0L);

            FileInfoV2 file1 = new FileInfoV2();
            file1.setId(1L);
            file1.setUuid("file-uuid-001");
            file1.setEnabled(1);

            ChunkInfo chunk1 = new ChunkInfo();
            chunk1.setDocId("file-uuid-001");
            chunk1.setContent("test content");
            chunk1.setDataIndex("chunk-001");

            // Create JSON response data
            JSONObject chunkJson = new JSONObject();
            chunkJson.put("docId", "file-uuid-001");
            chunkJson.put("content", "test content");
            chunkJson.put("dataIndex", "chunk-001");

            JSONObject respDataJson = new JSONObject();
            respDataJson.put("results", new com.alibaba.fastjson2.JSONArray());
            respDataJson.getJSONArray("results").add(chunkJson);

            KnowledgeResponse knowledgeResponse = new KnowledgeResponse();
            knowledgeResponse.setCode(0);
            knowledgeResponse.setMessage("success");
            knowledgeResponse.setData(respDataJson);

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(directoryTreeService.list(any(LambdaQueryWrapper.class))).thenReturn(Arrays.asList(tree1));
            when(fileInfoV2Service.getById(1L)).thenReturn(file1);
            when(knowledgeV2ServiceCallHandler.knowledgeQuery(any(QueryRequest.class))).thenReturn(knowledgeResponse);
            when(historyService.save(any(HitTestHistory.class))).thenReturn(true);
            when(fileInfoV2Service.getOnly(any(QueryWrapper.class))).thenReturn(file1);
            when(directoryTreeService.getOnly(any(LambdaQueryWrapper.class))).thenReturn(tree1);
            when(directoryTreeService.updateById(any(FileDirectoryTree.class))).thenReturn(true);

            // When
            Object result = repoService.hitTest(1L, "test query", 10, true);

            // Then
            assertThat(result).isNotNull();
            assertThat(result).isInstanceOf(List.class);
            verify(historyService, times(1)).save(any(HitTestHistory.class));
            verify(directoryTreeService, times(1)).updateById(any(FileDirectoryTree.class));
        }

        /**
         * Test hitTest - repository not exist.
         */
        @Test
        @DisplayName("hitTest - repository not exist")
        void testHitTest_RepoNotExist() {
            // Given
            when(repoMapper.selectById(999L)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> repoService.hitTest(999L, "test query", 10, true))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NOT_EXIST);
        }

        /**
         * Test hitTest - no files in directory tree.
         */
        @Test
        @DisplayName("hitTest - no files in directory")
        void testHitTest_NoFiles() {
            // Given
            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(directoryTreeService.list(any(LambdaQueryWrapper.class))).thenReturn(new ArrayList<>());

            // When
            Object result = repoService.hitTest(1L, "test query", 10, true);

            // Then
            assertThat(result).isNotNull();
            assertThat(result).isInstanceOf(com.alibaba.fastjson2.JSONArray.class);
            verify(knowledgeV2ServiceCallHandler, never()).knowledgeQuery(any());
        }

        /**
         * Test hitTest - no enabled files.
         */
        @Test
        @DisplayName("hitTest - no enabled files")
        void testHitTest_NoEnabledFiles() {
            // Given
            FileDirectoryTree tree1 = new FileDirectoryTree();
            tree1.setAppId("1");
            tree1.setFileId(1L);
            tree1.setIsFile(1);

            FileInfoV2 file1 = new FileInfoV2();
            file1.setId(1L);
            file1.setEnabled(0);  // Disabled file

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(directoryTreeService.list(any(LambdaQueryWrapper.class))).thenReturn(Arrays.asList(tree1));
            when(fileInfoV2Service.getById(1L)).thenReturn(file1);

            // When & Then
            assertThatThrownBy(() -> repoService.hitTest(1L, "test query", 10, true))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_DISABLED);
        }

        /**
         * Test hitTest - knowledge query fails.
         */
        @Test
        @DisplayName("hitTest - knowledge query fails")
        void testHitTest_QueryFails() {
            // Given
            FileDirectoryTree tree1 = new FileDirectoryTree();
            tree1.setAppId("1");
            tree1.setFileId(1L);
            tree1.setIsFile(1);

            FileInfoV2 file1 = new FileInfoV2();
            file1.setId(1L);
            file1.setEnabled(1);

            KnowledgeResponse knowledgeResponse = new KnowledgeResponse();
            knowledgeResponse.setCode(1);  // Error code
            knowledgeResponse.setMessage("Query failed");

            when(repoMapper.selectById(1L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(directoryTreeService.list(any(LambdaQueryWrapper.class))).thenReturn(Arrays.asList(tree1));
            when(fileInfoV2Service.getById(1L)).thenReturn(file1);
            when(knowledgeV2ServiceCallHandler.knowledgeQuery(any(QueryRequest.class))).thenReturn(knowledgeResponse);

            // When & Then
            assertThatThrownBy(() -> repoService.hitTest(1L, "test query", 10, true))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_KNOWLEDGE_QUERY_FAILED);
        }
    }
}

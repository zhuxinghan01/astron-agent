package com.iflytek.astron.console.toolkit.service.knowledge;

import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.util.ChatFileHttpClient;
import com.iflytek.astron.console.commons.util.S3ClientUtil;
import com.iflytek.astron.console.commons.util.space.SpaceInfoUtil;
import com.iflytek.astron.console.toolkit.common.constant.ProjectContent;
import com.iflytek.astron.console.toolkit.config.properties.ApiUrl;
import com.iflytek.astron.console.toolkit.entity.table.repo.FileInfoV2;
import com.iflytek.astron.console.toolkit.entity.table.repo.Repo;
import com.iflytek.astron.console.toolkit.entity.table.repo.FileDirectoryTree;
import com.iflytek.astron.console.toolkit.entity.vo.HtmlFileVO;
import com.iflytek.astron.console.toolkit.handler.UserInfoManagerHandler;
import com.iflytek.astron.console.toolkit.mapper.knowledge.KnowledgeMapper;
import com.iflytek.astron.console.toolkit.mapper.knowledge.PreviewKnowledgeMapper;
import com.iflytek.astron.console.toolkit.mapper.repo.FileDirectoryTreeMapper;
import com.iflytek.astron.console.toolkit.mapper.repo.FileInfoV2Mapper;
import com.iflytek.astron.console.toolkit.service.common.ConfigInfoService;
import com.iflytek.astron.console.toolkit.service.repo.*;
import com.iflytek.astron.console.toolkit.service.task.ExtractKnowledgeTaskService;
import com.iflytek.astron.console.toolkit.tool.DataPermissionCheckTool;
import com.iflytek.astron.console.toolkit.tool.FileUploadTool;
import com.iflytek.astron.console.toolkit.util.S3Util;
import jakarta.servlet.http.HttpServletRequest;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.sql.Timestamp;
import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for FileInfoV2Service
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
@DisplayName("FileInfoV2Service Unit Tests")
class FileInfoV2ServiceTest {

    @Mock
    private FileInfoV2Mapper fileInfoV2Mapper;

    @Mock
    private ConfigInfoService configInfoService;

    @Mock
    private S3Util s3UtilClient;

    @Mock
    private RepoService repoService;

    @Mock
    private FileDirectoryTreeMapper fileDirectoryTreeMapper;

    @Mock
    private FileDirectoryTreeService fileDirectoryTreeService;

    @Mock
    private KnowledgeService knowledgeService;

    @Mock
    private ExtractKnowledgeTaskService extractKnowledgeTaskService;

    @Mock
    private KnowledgeMapper knowledgeMapper;

    @Mock
    private PreviewKnowledgeMapper previewKnowledgeMapper;

    @Mock
    private FileUploadTool fileUploadTool;

    @Mock
    private DataPermissionCheckTool dataPermissionCheckTool;

    @Mock
    private ChatFileHttpClient chatFileHttpClient;

    @Mock
    private S3ClientUtil s3ClientUtil;

    @Mock
    private HttpServletRequest request;

    @Mock
    private ApiUrl apiUrl;

    @Spy
    @InjectMocks
    private FileInfoV2Service fileInfoV2Service;

    private FileInfoV2 mockFileInfo;
    private Repo mockRepo;
    private MultipartFile mockFile;
    private MockHttpServletRequest mockRequest;

    // Static mocks for utility classes
    private MockedStatic<UserInfoManagerHandler> userInfoManagerHandlerMock;
    private MockedStatic<SpaceInfoUtil> spaceInfoUtilMock;

    /**
     * Set up test fixtures before each test method.
     * Initializes common test data including mock file and repository objects.
     */
    @BeforeEach
    void setUp() {
        // Mock static utility methods
        userInfoManagerHandlerMock = mockStatic(UserInfoManagerHandler.class);
        userInfoManagerHandlerMock.when(UserInfoManagerHandler::getUserId).thenReturn("user-001");

        spaceInfoUtilMock = mockStatic(SpaceInfoUtil.class);
        spaceInfoUtilMock.when(SpaceInfoUtil::getSpaceId).thenReturn(null);

        // Set baseMapper for ServiceImpl - CRITICAL for MyBatis-Plus ServiceImpl
        ReflectionTestUtils.setField(fileInfoV2Service, "baseMapper", fileInfoV2Mapper);

        // Initialize mock HttpServletRequest
        mockRequest = new MockHttpServletRequest();

        // Initialize mock FileInfoV2
        mockFileInfo = new FileInfoV2();
        mockFileInfo.setId(1L);
        mockFileInfo.setUuid("file-uuid-001");
        mockFileInfo.setLastUuid("file-uuid-001");
        mockFileInfo.setName("test-file.txt");
        mockFileInfo.setRepoId(100L);
        mockFileInfo.setEnabled(1);
        mockFileInfo.setSource("AIUI-RAG2");
        mockFileInfo.setCharCount(1000L);
        mockFileInfo.setAddress("s3://bucket/test-file.txt");
        mockFileInfo.setSize(1024L);
        mockFileInfo.setPid(0L);
        mockFileInfo.setStatus(ProjectContent.FILE_UPLOAD_STATUS);
        mockFileInfo.setCreateTime(new Timestamp(System.currentTimeMillis()));
        mockFileInfo.setUpdateTime(new Timestamp(System.currentTimeMillis()));

        // Initialize mock Repo
        mockRepo = new Repo();
        mockRepo.setId(100L);
        mockRepo.setName("Test Repository");
        mockRepo.setCoreRepoId("core-repo-001");
        mockRepo.setTag("AIUI-RAG2");
        mockRepo.setDeleted(false);
        mockRepo.setCreateTime(new Date());
        mockRepo.setUpdateTime(new Date());

        // Initialize mock MultipartFile
        String fileContent = "Test file content for unit testing";
        mockFile = new MockMultipartFile(
                "file",
                "test-file.txt",
                "text/plain",
                fileContent.getBytes(StandardCharsets.UTF_8)
        );

        // Set field values using ReflectionTestUtils
        ReflectionTestUtils.setField(fileInfoV2Service, "cbgRagMaxCharCount", 1000000L);
    }

    /**
     * Clean up after each test method.
     * Closes static mocks to avoid side effects between tests.
     */
    @AfterEach
    void tearDown() {
        // Close static mocks to prevent memory leaks
        if (userInfoManagerHandlerMock != null) {
            userInfoManagerHandlerMock.close();
        }
        if (spaceInfoUtilMock != null) {
            spaceInfoUtilMock.close();
        }
    }

    /**
     * Test cases for the uploadFile method.
     * Validates file upload functionality including success scenarios and error handling.
     */
    @Nested
    @DisplayName("uploadFile Tests")
    class UploadFileTests {

        /**
         * Test successful file upload with AIUI-RAG2 tag.
         */
        @Test
        @DisplayName("Upload file successfully with AIUI-RAG2 tag")
        void testUploadFile_Success_WithAIUI() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            JSONObject uploadRes = new JSONObject();
            uploadRes.put("s3Key", "s3://bucket/test-file.txt");
            when(fileUploadTool.uploadFile(any(MultipartFile.class), anyString())).thenReturn(uploadRes);

            // Mock save to avoid MyBatis-Plus dependency
            doReturn(true).when(fileInfoV2Service).save(any(FileInfoV2.class));

            // When
            FileInfoV2 result = fileInfoV2Service.uploadFile(mockFile, parentId, repoId, tag, request);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getName()).isEqualTo("test-file.txt");
            verify(fileUploadTool, times(1)).uploadFile(any(MultipartFile.class), eq(tag));
            verify(fileInfoV2Service, times(1)).save(any(FileInfoV2.class));
        }

        /**
         * Test file upload with CBG-RAG tag.
         */
        @Test
        @DisplayName("Upload file successfully with CBG-RAG tag")
        void testUploadFile_Success_WithCBG() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "CBG-RAG";
            mockRepo.setTag("CBG-RAG");

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            JSONObject uploadRes = new JSONObject();
            uploadRes.put("s3Key", "s3://bucket/test-file.txt");
            when(fileUploadTool.uploadFile(any(MultipartFile.class), anyString())).thenReturn(uploadRes);

            // Mock save to avoid MyBatis-Plus dependency
            doReturn(true).when(fileInfoV2Service).save(any(FileInfoV2.class));

            // When
            FileInfoV2 result = fileInfoV2Service.uploadFile(mockFile, parentId, repoId, tag, request);

            // Then
            assertThat(result).isNotNull();
            verify(fileUploadTool, times(1)).uploadFile(any(MultipartFile.class), eq(tag));
            verify(fileInfoV2Service, times(1)).save(any(FileInfoV2.class));
        }

        /**
         * Test file upload with invalid file type (HTML).
         */
        @Test
        @DisplayName("Upload file - invalid file type (HTML)")
        void testUploadFile_InvalidFileType_HTML() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            MultipartFile htmlFile = new MockMultipartFile(
                    "file",
                    "test-file.html",
                    "text/html",
                    "Test content".getBytes(StandardCharsets.UTF_8)
            );

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(htmlFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_UPLOAD_TYPE_NOT_EXIST);

            verify(fileUploadTool, never()).uploadFile(any(MultipartFile.class), anyString());
        }

        /**
         * Test file upload with invalid file type (SVG).
         */
        @Test
        @DisplayName("Upload file - invalid file type (SVG)")
        void testUploadFile_InvalidFileType_SVG() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            MultipartFile svgFile = new MockMultipartFile(
                    "file",
                    "test-file.svg",
                    "image/svg+xml",
                    "Test content".getBytes(StandardCharsets.UTF_8)
            );

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(svgFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_UPLOAD_TYPE_NOT_EXIST);

            verify(fileUploadTool, never()).uploadFile(any(MultipartFile.class), anyString());
        }

        /**
         * Test file upload when repository not found.
         */
        @Test
        @DisplayName("Upload file - repository not found")
        void testUploadFile_RepoNotFound() {
            // Given
            Long parentId = 0L;
            Long repoId = 999L;
            String tag = "AIUI-RAG2";

            when(repoService.getById(anyLong())).thenReturn(null);
            // When repo is null, checkRepoBelong should throw exception
            doThrow(new BusinessException(ResponseEnum.REPO_NOT_EXIST))
                    .when(dataPermissionCheckTool).checkRepoBelong(null);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(mockFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NOT_EXIST);

            verify(fileUploadTool, never()).uploadFile(any(MultipartFile.class), anyString());
        }

        /**
         * Test file upload when upload tool returns null.
         */
        @Test
        @DisplayName("Upload file - upload tool returns null")
        void testUploadFile_UploadToolReturnsNull() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            when(fileUploadTool.uploadFile(any(MultipartFile.class), anyString())).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(mockFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_UPLOAD_FAILED);

            verify(fileInfoV2Mapper, never()).insert(any(FileInfoV2.class));
        }

        /**
         * Test file upload when upload tool returns result without s3Key.
         */
        @Test
        @DisplayName("Upload file - upload tool returns result without s3Key")
        void testUploadFile_UploadToolReturnsResultWithoutS3Key() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            JSONObject uploadRes = new JSONObject();
            uploadRes.put("otherKey", "otherValue");
            when(fileUploadTool.uploadFile(any(MultipartFile.class), anyString())).thenReturn(uploadRes);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(mockFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_UPLOAD_FAILED);

            verify(fileInfoV2Mapper, never()).insert(any(FileInfoV2.class));
        }

        /**
         * Test file upload with empty filename - should throw exception for AIUI-RAG2.
         */
        @Test
        @DisplayName("Upload file - empty filename throws exception")
        void testUploadFile_EmptyFilename() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            MultipartFile emptyNameFile = new MockMultipartFile(
                    "file",
                    "",
                    "text/plain",
                    "Test content".getBytes(StandardCharsets.UTF_8)
            );

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(emptyNameFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_TYPE_EMPTY_XINGCHEN);

            verify(fileUploadTool, never()).uploadFile(any(MultipartFile.class), anyString());
        }

        /**
         * Test file upload with null filename - should throw exception for AIUI-RAG2.
         */
        @Test
        @DisplayName("Upload file - null filename throws exception")
        void testUploadFile_NullFilename() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            MultipartFile nullNameFile = new MockMultipartFile(
                    "file",
                    null,
                    "text/plain",
                    "Test content".getBytes(StandardCharsets.UTF_8)
            );

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(nullNameFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_TYPE_EMPTY_XINGCHEN);

            verify(fileUploadTool, never()).uploadFile(any(MultipartFile.class), anyString());
        }
    }

    /**
     * Test cases for the getOnly method.
     * Validates file query functionality with QueryWrapper.
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
            QueryWrapper<FileInfoV2> wrapper = new QueryWrapper<>();
            wrapper.eq("name", "test-file.txt");

            when(fileInfoV2Mapper.selectOne(any(QueryWrapper.class), anyBoolean())).thenReturn(mockFileInfo);

            // When
            FileInfoV2 result = fileInfoV2Service.getOnly(wrapper);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getName()).isEqualTo("test-file.txt");
            verify(fileInfoV2Mapper, times(1)).selectOne(any(QueryWrapper.class), anyBoolean());
        }

        /**
         * Test getOnly with QueryWrapper - no result found.
         */
        @Test
        @DisplayName("getOnly with QueryWrapper - no result")
        void testGetOnly_QueryWrapper_NoResult() {
            // Given
            QueryWrapper<FileInfoV2> wrapper = new QueryWrapper<>();
            wrapper.eq("name", "nonexistent-file.txt");

            when(fileInfoV2Mapper.selectOne(any(QueryWrapper.class), anyBoolean())).thenReturn(null);

            // When
            FileInfoV2 result = fileInfoV2Service.getOnly(wrapper);

            // Then
            assertThat(result).isNull();
            verify(fileInfoV2Mapper, times(1)).selectOne(any(QueryWrapper.class), anyBoolean());
        }
    }

    /**
     * Test cases for the createFile method.
     */
    @Nested
    @DisplayName("createFile Tests")
    class CreateFileTests {

        /**
         * Test successful file creation.
         */
        @Test
        @DisplayName("Create file - success")
        void testCreateFile_Success() {
            // Given
            Long repoId = 100L;
            String sourceId = "source-001";
            String filename = "test-file.txt";
            Long parentId = 0L;
            String s3Key = "s3://bucket/test.txt";
            Long size = 1024L;
            Long charCount = 500L;
            Integer enable = 1;
            String tag = "AIUI-RAG2";

            // Mock save to avoid MyBatis-Plus dependency
            doReturn(true).when(fileInfoV2Service).save(any(FileInfoV2.class));

            // When
            FileInfoV2 result = fileInfoV2Service.createFile(repoId, sourceId, filename, parentId, s3Key, size, charCount, enable, tag);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getUuid()).isEqualTo(sourceId);
            assertThat(result.getName()).isEqualTo(filename);
            assertThat(result.getRepoId()).isEqualTo(repoId);
            assertThat(result.getAddress()).isEqualTo(s3Key);
            assertThat(result.getSize()).isEqualTo(size);
            assertThat(result.getCharCount()).isEqualTo(charCount);
            assertThat(result.getEnabled()).isEqualTo(enable);
            assertThat(result.getSource()).isEqualTo(tag);
            verify(fileInfoV2Service, times(1)).save(any(FileInfoV2.class));
        }

        /**
         * Test file creation with space ID.
         */
        @Test
        @DisplayName("Create file - with space ID")
        void testCreateFile_WithSpaceId() {
            // Given
            spaceInfoUtilMock.when(SpaceInfoUtil::getSpaceId).thenReturn(123L);

            Long repoId = 100L;
            String sourceId = "source-001";
            String filename = "test-file.txt";

            // Mock save to avoid MyBatis-Plus dependency
            doAnswer(invocation -> {
                FileInfoV2 file = invocation.getArgument(0);
                assertThat(file.getSpaceId()).isEqualTo(123L);
                return true;
            }).when(fileInfoV2Service).save(any(FileInfoV2.class));

            // When
            FileInfoV2 result = fileInfoV2Service.createFile(repoId, sourceId, filename, 0L, "s3://test", 100L, 50L, 1, "AIUI-RAG2");

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getSpaceId()).isEqualTo(123L);
            verify(fileInfoV2Service, times(1)).save(any(FileInfoV2.class));
        }
    }

    /**
     * Test cases for the createHtmlFile method.
     */
    @Nested
    @DisplayName("createHtmlFile Tests")
    class CreateHtmlFileTests {

        /**
         * Test successful HTML file creation.
         */
        @Test
        @DisplayName("Create HTML file - success")
        void testCreateHtmlFile_Success() {
            // Given
            HtmlFileVO htmlFileVO = new HtmlFileVO();
            htmlFileVO.setRepoId(100L);
            htmlFileVO.setParentId(0L);
            htmlFileVO.setHtmlAddressList(Arrays.asList("http://example.com/page1.html", "http://example.com/page2.html"));

            when(repoService.getById(100L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            // Mock saveBatch to avoid MyBatis-Plus dependency
            doReturn(true).when(fileInfoV2Service).saveBatch(anyList());

            // When
            List<FileInfoV2> result = fileInfoV2Service.createHtmlFile(htmlFileVO);

            // Then
            assertThat(result).isNotNull();
            assertThat(result).hasSize(2);
            assertThat(result.get(0).getType()).isEqualTo(ProjectContent.HTML_FILE_TYPE);
            assertThat(result.get(0).getEnabled()).isEqualTo(0);
            verify(fileInfoV2Service, times(1)).saveBatch(anyList());
        }

        /**
         * Test HTML file creation with long URL (truncation).
         */
        @Test
        @DisplayName("Create HTML file - long URL truncation")
        void testCreateHtmlFile_LongUrlTruncation() {
            // Given
            String longUrl = "http://example.com/" + "a".repeat(100) + ".html";
            HtmlFileVO htmlFileVO = new HtmlFileVO();
            htmlFileVO.setRepoId(100L);
            htmlFileVO.setParentId(0L);
            htmlFileVO.setHtmlAddressList(Arrays.asList(longUrl));

            when(repoService.getById(100L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));
            // Mock saveBatch to avoid MyBatis-Plus dependency
            doReturn(true).when(fileInfoV2Service).saveBatch(anyList());

            // When
            List<FileInfoV2> result = fileInfoV2Service.createHtmlFile(htmlFileVO);

            // Then
            assertThat(result).isNotNull();
            assertThat(result).hasSize(1);
            assertThat(result.get(0).getName().length()).isLessThanOrEqualTo(30);
            verify(fileInfoV2Service, times(1)).saveBatch(anyList());
        }

        /**
         * Test HTML file creation - repository not found.
         */
        @Test
        @DisplayName("Create HTML file - repository not found")
        void testCreateHtmlFile_RepoNotFound() {
            // Given
            HtmlFileVO htmlFileVO = new HtmlFileVO();
            htmlFileVO.setRepoId(999L);
            htmlFileVO.setHtmlAddressList(Arrays.asList("http://example.com/page.html"));

            when(repoService.getById(999L)).thenReturn(null);
            // When repo is null, checkRepoBelong should throw exception
            doThrow(new BusinessException(ResponseEnum.REPO_NOT_EXIST))
                    .when(dataPermissionCheckTool).checkRepoBelong(null);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.createHtmlFile(htmlFileVO))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_NOT_EXIST);
        }

        /**
         * Test HTML file creation with empty list.
         */
        @Test
        @DisplayName("Create HTML file - empty list")
        void testCreateHtmlFile_EmptyList() {
            // Given
            HtmlFileVO htmlFileVO = new HtmlFileVO();
            htmlFileVO.setRepoId(100L);
            htmlFileVO.setHtmlAddressList(Collections.emptyList());

            when(repoService.getById(100L)).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            // When
            List<FileInfoV2> result = fileInfoV2Service.createHtmlFile(htmlFileVO);

            // Then
            assertThat(result).isEmpty();
        }
    }

    /**
     * Test cases for the enableFile method.
     */
    @Nested
    @DisplayName("enableFile Tests")
    class EnableFileTests {

        /**
         * Test enable file successfully.
         */
        @Test
        @DisplayName("Enable file - success")
        void testEnableFile_Success() {
            // Given
            Long id = 1L;
            Integer enabled = 1;

            FileDirectoryTree tree = new FileDirectoryTree();
            tree.setId(id);
            tree.setFileId(1L);
            tree.setIsFile(1);

            when(fileDirectoryTreeService.getById(id)).thenReturn(tree);
            when(fileInfoV2Mapper.selectById(1L)).thenReturn(mockFileInfo);
            doNothing().when(dataPermissionCheckTool).checkFileBelong(any(FileInfoV2.class));
            // Mock updateById to avoid MyBatis-Plus dependency
            doReturn(true).when(fileInfoV2Service).updateById(any(FileInfoV2.class));
            doNothing().when(knowledgeService).enableDoc(anyLong(), anyInt());

            // When
            fileInfoV2Service.enableFile(id, enabled);

            // Then
            verify(fileInfoV2Service, times(1)).updateById(any(FileInfoV2.class));
            verify(knowledgeService, times(1)).enableDoc(1L, enabled);
        }

        /**
         * Test enable file - directory tree not found.
         */
        @Test
        @DisplayName("Enable file - directory tree not found")
        void testEnableFile_DirectoryTreeNotFound() {
            // Given
            Long id = 999L;
            Integer enabled = 1;

            when(fileDirectoryTreeService.getById(id)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.enableFile(id, enabled))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_NOT_EXIST);
        }

        /**
         * Test enable file - not a file (is folder).
         */
        @Test
        @DisplayName("Enable file - not a file (is folder)")
        void testEnableFile_NotAFile() {
            // Given
            Long id = 1L;
            Integer enabled = 1;

            FileDirectoryTree tree = new FileDirectoryTree();
            tree.setId(id);
            tree.setIsFile(0);  // It's a folder

            when(fileDirectoryTreeService.getById(id)).thenReturn(tree);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.enableFile(id, enabled))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_NOT_EXIST);
        }

        /**
         * Test enable file - file info not found.
         */
        @Test
        @DisplayName("Enable file - file info not found")
        void testEnableFile_FileInfoNotFound() {
            // Given
            Long id = 1L;
            Integer enabled = 1;

            FileDirectoryTree tree = new FileDirectoryTree();
            tree.setId(id);
            tree.setFileId(1L);
            tree.setIsFile(1);

            when(fileDirectoryTreeService.getById(id)).thenReturn(tree);
            when(fileInfoV2Mapper.selectById(1L)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.enableFile(id, enabled))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_NOT_EXIST);
        }

        /**
         * Test disable file successfully.
         */
        @Test
        @DisplayName("Disable file - success")
        void testDisableFile_Success() {
            // Given
            Long id = 1L;
            Integer enabled = 0;

            FileDirectoryTree tree = new FileDirectoryTree();
            tree.setId(id);
            tree.setFileId(1L);
            tree.setIsFile(1);

            when(fileDirectoryTreeService.getById(id)).thenReturn(tree);
            when(fileInfoV2Mapper.selectById(1L)).thenReturn(mockFileInfo);
            doNothing().when(dataPermissionCheckTool).checkFileBelong(any(FileInfoV2.class));
            // Mock updateById to avoid MyBatis-Plus dependency
            doReturn(true).when(fileInfoV2Service).updateById(any(FileInfoV2.class));
            doNothing().when(knowledgeService).enableDoc(anyLong(), anyInt());

            // When
            fileInfoV2Service.enableFile(id, enabled);

            // Then
            verify(fileInfoV2Service, times(1)).updateById(any(FileInfoV2.class));
            verify(knowledgeService, times(1)).enableDoc(1L, enabled);
        }
    }

    /**
     * Test cases for the deleteFile method.
     */
    @Nested
    @DisplayName("deleteFile Tests")
    class DeleteFileTests {

        /**
         * Test delete file successfully.
         */
        @Test
        @DisplayName("Delete file - success")
        void testDeleteFile_Success() {
            // Given
            Long fileId = 1L;

            when(fileDirectoryTreeService.remove(any(LambdaQueryWrapper.class))).thenReturn(true);
            doNothing().when(knowledgeService).deleteDoc(anyList());

            // When
            fileInfoV2Service.deleteFile(fileId);

            // Then
            verify(fileDirectoryTreeService, times(1)).remove(any(LambdaQueryWrapper.class));
            verify(knowledgeService, times(1)).deleteDoc(anyList());
        }
    }

    /**
     * Test cases for the deleteFolder method.
     */
    @Nested
    @DisplayName("deleteFolder Tests")
    class DeleteFolderTests {

        /**
         * Test delete folder - folder not found.
         */
        @Test
        @DisplayName("Delete folder - folder not found")
        void testDeleteFolder_FolderNotFound() {
            // Given
            Long folderId = 999L;

            when(fileDirectoryTreeService.getById(folderId)).thenReturn(null);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.deleteFolder(folderId))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FOLDER_NOT_EXIST);
        }

        /**
         * Test delete folder - not a folder (is file).
         */
        @Test
        @DisplayName("Delete folder - not a folder (is file)")
        void testDeleteFolder_NotAFolder() {
            // Given
            Long folderId = 1L;

            FileDirectoryTree tree = new FileDirectoryTree();
            tree.setId(folderId);
            tree.setIsFile(1);  // It's a file

            when(fileDirectoryTreeService.getById(folderId)).thenReturn(tree);

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.deleteFolder(folderId))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FOLDER_NOT_EXIST);
        }
    }

    /**
     * Test cases for the getFileInfoV2BySourceId method.
     */
    @Nested
    @DisplayName("getFileInfoV2BySourceId Tests")
    class GetFileInfoV2BySourceIdTests {

        /**
         * Test get file by source ID successfully.
         */
        @Test
        @DisplayName("Get file by source ID - success")
        void testGetFileInfoV2BySourceId_Success() {
            // Given
            String sourceId = "file-uuid-001";

            when(fileInfoV2Mapper.selectOne(any(QueryWrapper.class), anyBoolean())).thenReturn(mockFileInfo);
            doNothing().when(dataPermissionCheckTool).checkFileBelong(any(FileInfoV2.class));

            // When
            FileInfoV2 result = fileInfoV2Service.getFileInfoV2BySourceId(sourceId);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getUuid()).isEqualTo(sourceId);
            verify(fileInfoV2Mapper, times(1)).selectOne(any(QueryWrapper.class), anyBoolean());
        }

        /**
         * Test get file by source ID - not found.
         */
        @Test
        @DisplayName("Get file by source ID - not found")
        void testGetFileInfoV2BySourceId_NotFound() {
            // Given
            String sourceId = "nonexistent-uuid";

            when(fileInfoV2Mapper.selectOne(any(QueryWrapper.class), anyBoolean())).thenReturn(null);

            // When
            FileInfoV2 result = fileInfoV2Service.getFileInfoV2BySourceId(sourceId);

            // Then
            assertThat(result).isNull();
        }

        /**
         * Test get file by source ID with space ID.
         */
        @Test
        @DisplayName("Get file by source ID - with space ID")
        void testGetFileInfoV2BySourceId_WithSpaceId() {
            // Given
            spaceInfoUtilMock.when(SpaceInfoUtil::getSpaceId).thenReturn(123L);
            String sourceId = "file-uuid-001";

            when(fileInfoV2Mapper.selectOne(any(QueryWrapper.class), anyBoolean())).thenReturn(mockFileInfo);

            // When
            FileInfoV2 result = fileInfoV2Service.getFileInfoV2BySourceId(sourceId);

            // Then
            assertThat(result).isNotNull();
            verify(dataPermissionCheckTool, never()).checkFileBelong(any(FileInfoV2.class));
        }
    }

    /**
     * Test cases for edge cases and boundary conditions.
     */
    @Nested
    @DisplayName("Edge Case Tests")
    class EdgeCaseTests {

        /**
         * Test uploadFile with very large file for CBG-RAG.
         */
        @Test
        @DisplayName("Upload file - very large file for CBG-RAG exceeds limit")
        void testUploadFile_VeryLargeFile_CBG_ExceedsLimit() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "CBG-RAG";
            mockRepo.setTag("CBG-RAG");

            // Create a mock file that simulates size > 20MB for non-image files
            byte[] largeContent = new byte[21 * 1024 * 1024]; // 21MB
            MultipartFile largeFile = new MockMultipartFile(
                    "file",
                    "large-file.txt",
                    "text/plain",
                    largeContent
            );

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(largeFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_UPLOAD_FAILED_FILE_20MB);

            verify(fileUploadTool, never()).uploadFile(any(MultipartFile.class), anyString());
        }

        /**
         * Test uploadFile with large image file for CBG-RAG exceeds limit.
         */
        @Test
        @DisplayName("Upload file - large image file for CBG-RAG exceeds 5MB limit")
        void testUploadFile_LargeImageFile_CBG_Exceeds5MB() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "CBG-RAG";
            mockRepo.setTag("CBG-RAG");

            // Create a mock image file that simulates size > 5MB
            byte[] largeContent = new byte[6 * 1024 * 1024]; // 6MB
            MultipartFile largeImageFile = new MockMultipartFile(
                    "file",
                    "large-image.jpg",
                    "image/jpeg",
                    largeContent
            );

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(largeImageFile, parentId, repoId, tag, request))
                    .isInstanceOf(BusinessException.class)
                    .extracting("responseEnum")
                    .isEqualTo(ResponseEnum.REPO_FILE_UPLOAD_FAILED_PIC_5MB);

            verify(fileUploadTool, never()).uploadFile(any(MultipartFile.class), anyString());
        }

        /**
         * Test uploadFile with file that has special characters in name.
         */
        @Test
        @DisplayName("Upload file - filename with special characters")
        void testUploadFile_FilenameWithSpecialCharacters() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            MultipartFile specialNameFile = new MockMultipartFile(
                    "file",
                    "测试文件@#$%^&*().txt",
                    "text/plain",
                    "Test content".getBytes(StandardCharsets.UTF_8)
            );

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            JSONObject uploadRes = new JSONObject();
            uploadRes.put("s3Key", "s3://bucket/test-file.txt");
            when(fileUploadTool.uploadFile(any(MultipartFile.class), anyString())).thenReturn(uploadRes);

            // Mock save to avoid MyBatis-Plus dependency
            doReturn(true).when(fileInfoV2Service).save(any(FileInfoV2.class));

            // When
            FileInfoV2 result = fileInfoV2Service.uploadFile(specialNameFile, parentId, repoId, tag, request);

            // Then
            assertThat(result).isNotNull();
            verify(fileUploadTool, times(1)).uploadFile(any(MultipartFile.class), eq(tag));
            verify(fileInfoV2Service, times(1)).save(any(FileInfoV2.class));
        }
    }

    /**
     * Test cases for exception scenarios.
     */
    @Nested
    @DisplayName("Exception Tests")
    class ExceptionTests {

        /**
         * Test uploadFile when database insert fails.
         */
        @Test
        @DisplayName("Upload file - database insert fails")
        void testUploadFile_DatabaseInsertFails() {
            // Given
            Long parentId = 0L;
            Long repoId = 100L;
            String tag = "AIUI-RAG2";

            when(repoService.getById(anyLong())).thenReturn(mockRepo);
            doNothing().when(dataPermissionCheckTool).checkRepoBelong(any(Repo.class));

            JSONObject uploadRes = new JSONObject();
            uploadRes.put("s3Key", "s3://bucket/test-file.txt");
            when(fileUploadTool.uploadFile(any(MultipartFile.class), anyString())).thenReturn(uploadRes);

            // Mock save to throw exception
            doThrow(new RuntimeException("Database error")).when(fileInfoV2Service).save(any(FileInfoV2.class));

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.uploadFile(mockFile, parentId, repoId, tag, request))
                    .isInstanceOf(RuntimeException.class)
                    .hasMessageContaining("Database error");

            verify(fileUploadTool, times(1)).uploadFile(any(MultipartFile.class), eq(tag));
            verify(fileInfoV2Service, times(1)).save(any(FileInfoV2.class));
        }

        /**
         * Test getOnly when database query fails.
         */
        @Test
        @DisplayName("getOnly - database query fails")
        void testGetOnly_DatabaseQueryFails() {
            // Given
            QueryWrapper<FileInfoV2> wrapper = new QueryWrapper<>();
            wrapper.eq("name", "test-file.txt");

            when(fileInfoV2Mapper.selectOne(any(QueryWrapper.class), anyBoolean()))
                    .thenThrow(new RuntimeException("Database query error"));

            // When & Then
            assertThatThrownBy(() -> fileInfoV2Service.getOnly(wrapper))
                    .isInstanceOf(RuntimeException.class)
                    .hasMessageContaining("Database query error");
        }
    }

    /**
     * Test cases for static utility methods.
     */
    @Nested
    @DisplayName("Static Utility Method Tests")
    class StaticUtilityTests {

        /**
         * Test getFileFormat with various file extensions.
         */
        @Test
        @DisplayName("getFileFormat - various extensions")
        void testGetFileFormat() {
            assertThat(FileInfoV2Service.getFileFormat("test.txt")).isEqualTo("txt");
            assertThat(FileInfoV2Service.getFileFormat("test.pdf")).isEqualTo("pdf");
            assertThat(FileInfoV2Service.getFileFormat("test.doc")).isEqualTo("doc");
            assertThat(FileInfoV2Service.getFileFormat("test.docx")).isEqualTo("docx");
            assertThat(FileInfoV2Service.getFileFormat("test")).isEqualTo("");
            assertThat(FileInfoV2Service.getFileFormat("")).isEqualTo("");
        }

        /**
         * Test checkIsPic method.
         */
        @Test
        @DisplayName("checkIsPic - image file detection")
        void testCheckIsPic() {
            assertThat(FileInfoV2Service.checkIsPic("image.jpg")).isTrue();
            assertThat(FileInfoV2Service.checkIsPic("image.png")).isTrue();
            assertThat(FileInfoV2Service.checkIsPic("document.pdf")).isFalse();
            assertThat(FileInfoV2Service.checkIsPic("document.txt")).isFalse();
        }
    }
}

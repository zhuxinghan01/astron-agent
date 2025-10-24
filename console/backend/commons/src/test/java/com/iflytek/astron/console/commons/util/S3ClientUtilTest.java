package com.iflytek.astron.console.commons.util;

import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import io.minio.BucketExistsArgs;
import io.minio.MakeBucketArgs;
import io.minio.MinioClient;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Duration;
import okhttp3.OkHttpClient;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.DisabledIf;
import org.springframework.test.util.ReflectionTestUtils;

/**
 * S3ClientUtil Integration Tests
 *
 * Requires MinIO test environment to run these tests
 *
 * Test configuration: - MinIO connection details configurable via environment variables Environment
 * variables: - MINIO_TEST_ENDPOINT: MinIO server endpoint (default: http://localhost:9000) -
 * MINIO_TEST_REMOTE_ENDPOINT: Remote endpoint for external access (default: http://localhost:9000)
 * - MINIO_TEST_ACCESS_KEY: Access key for authentication (default: minioadmin) -
 * MINIO_TEST_SECRET_KEY: Secret key for authentication (default: minioadmin) - MINIO_TEST_BUCKET:
 * Bucket name for testing (default: astron-project) - MINIO_INVALID_ACCESS_KEY: Invalid access key
 * for negative testing (default: invalid-user) - MINIO_INVALID_SECRET_KEY: Invalid secret key for
 * negative testing (default: invalid-secret)
 *
 * Note: If MinIO service is unavailable, some tests will be skipped
 */
class S3ClientUtilTest {

    private S3ClientUtil s3ClientUtil;

    // MinIO test environment configuration - from environment variables
    private static final String TEST_ENDPOINT = System.getenv().getOrDefault("MINIO_TEST_ENDPOINT", "http://localhost:9000");
    private static final String TEST_REMOTE_ENDPOINT = System.getenv().getOrDefault("MINIO_TEST_REMOTE_ENDPOINT", "http://localhost:9000");
    private static final String TEST_ACCESS_KEY = System.getenv().getOrDefault("MINIO_TEST_ACCESS_KEY", "minioadmin");
    private static final String TEST_SECRET_KEY = System.getenv().getOrDefault("MINIO_TEST_SECRET_KEY", "minioadmin");
    private static final String TEST_BUCKET = System.getenv().getOrDefault("MINIO_TEST_BUCKET", "astron-project");

    // Configuration for testing invalid credentials
    private static final String INVALID_ACCESS_KEY = System.getenv().getOrDefault("MINIO_INVALID_ACCESS_KEY", "invalid-user");
    private static final String INVALID_SECRET_KEY = System.getenv().getOrDefault("MINIO_INVALID_SECRET_KEY", "invalid-secret");

    private static boolean minioAvailable = true;

    static {
        // Check MinIO availability at class loading time
        try {
            URL url = new URL(TEST_ENDPOINT + "/minio/health/live");
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(2000);
            connection.setReadTimeout(2000);
            connection.connect();
            int responseCode = connection.getResponseCode();
            connection.disconnect();

            if (responseCode != 200) {
                minioAvailable = false;
                System.out.println("Warning: MinIO service is unavailable, related tests will be skipped");
            }
        } catch (Exception e) {
            minioAvailable = false;
            System.out.println("Warning: MinIO service is unavailable, related tests will be skipped");
        }
    }

    @BeforeEach
    void setUp() throws Exception {
        s3ClientUtil = new S3ClientUtil();

        // Use real MinIO test environment configuration
        ReflectionTestUtils.setField(s3ClientUtil, "endpoint", TEST_ENDPOINT);
        ReflectionTestUtils.setField(s3ClientUtil, "remoteEndpoint", TEST_REMOTE_ENDPOINT);
        ReflectionTestUtils.setField(s3ClientUtil, "accessKey", TEST_ACCESS_KEY);
        ReflectionTestUtils.setField(s3ClientUtil, "secretKey", TEST_SECRET_KEY);
        ReflectionTestUtils.setField(s3ClientUtil, "defaultBucket", TEST_BUCKET);
        ReflectionTestUtils.setField(s3ClientUtil, "presignExpirySeconds", 600);
        ReflectionTestUtils.setField(s3ClientUtil, "enablePublicRead", false);

        // Initialize MinIO client - handle BusinessException from @PostConstruct method
        try {
            s3ClientUtil.init();
        } catch (BusinessException e) {
            // If initialization fails due to MinIO unavailability, mark it as unavailable
            minioAvailable = false;
            System.out.println("Warning: MinIO service is unavailable during initialization, related tests will be skipped");
            return; // Skip the rest of setup if MinIO is unavailable
        }

        // Try to ensure test bucket exists, mark MinIO unavailable if failed
        try {
            ensureBucketExists();
        } catch (Exception e) {
            minioAvailable = false;
            System.out.println("Warning: MinIO service is unavailable, related tests will be skipped");
        }
    }

    private void ensureBucketExists() throws Exception {
        OkHttpClient httpClient = new OkHttpClient.Builder()
                .connectTimeout(Duration.ofSeconds(2))
                .writeTimeout(Duration.ofSeconds(2))
                .readTimeout(Duration.ofSeconds(2))
                .build();

        MinioClient client = MinioClient.builder()
                .endpoint(TEST_ENDPOINT)
                .credentials(TEST_ACCESS_KEY, TEST_SECRET_KEY)
                .httpClient(httpClient)
                .build();

        boolean bucketExists = client.bucketExists(BucketExistsArgs.builder()
                .bucket(TEST_BUCKET)
                .build());

        if (!bucketExists) {
            client.makeBucket(MakeBucketArgs.builder()
                    .bucket(TEST_BUCKET)
                    .build());
        }
    }

    static boolean isMinioUnavailable() {
        return !minioAvailable;
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_success() {
        // Prepare test data
        String objectKey = "test/upload_success_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        byte[] testContent = "Hello MinIO Test!".getBytes();
        InputStream inputStream = new ByteArrayInputStream(testContent);

        // Execute test
        String result = s3ClientUtil.uploadObject(TEST_BUCKET, objectKey, contentType, inputStream, testContent.length, -1);

        // Verify returned URL format is correct
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, result);
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_withNullContentType() {
        // Prepare test data
        String objectKey = "test/upload_null_content_type_" + System.currentTimeMillis() + ".txt";
        byte[] testContent = "Test content with null content type".getBytes();
        InputStream inputStream = new ByteArrayInputStream(testContent);

        // Execute test - contentType is null
        String result = s3ClientUtil.uploadObject(TEST_BUCKET, objectKey, null, inputStream, testContent.length, -1);

        // Verify returned URL
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, result);
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_withEmptyContentType() {
        // Prepare test data
        String objectKey = "test/upload_empty_content_type_" + System.currentTimeMillis() + ".txt";
        byte[] testContent = "Test content with empty content type".getBytes();
        InputStream inputStream = new ByteArrayInputStream(testContent);

        // Execute test - contentType is empty string
        String result = s3ClientUtil.uploadObject(TEST_BUCKET, objectKey, "", inputStream, testContent.length, -1);

        // Verify returned URL
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, result);
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_withInvalidCredentials() {
        // Create an S3ClientUtil using invalid credentials
        S3ClientUtil invalidS3ClientUtil = new S3ClientUtil();
        ReflectionTestUtils.setField(invalidS3ClientUtil, "endpoint", TEST_ENDPOINT);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "remoteEndpoint", TEST_REMOTE_ENDPOINT);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "accessKey", INVALID_ACCESS_KEY);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "secretKey", INVALID_SECRET_KEY);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "defaultBucket", TEST_BUCKET);

        // @PostConstruct method may throw BusinessException during initialization with invalid credentials
        try {
            invalidS3ClientUtil.init();
        } catch (BusinessException e) {
            // If initialization fails, verify it's the expected error
            Assertions.assertEquals(ResponseEnum.INTERNAL_SERVER_ERROR.getCode(), e.getCode());
            return; // Test passes - initialization correctly failed with invalid credentials
        }

        String objectKey = "test/should_fail.txt";
        String contentType = "text/plain";
        InputStream inputStream = new ByteArrayInputStream("test content".getBytes());

        // If initialization didn't fail, then upload should fail
        BusinessException exception = Assertions.assertThrows(BusinessException.class,
                () -> invalidS3ClientUtil.uploadObject(TEST_BUCKET, objectKey, contentType, inputStream, 12, -1));

        Assertions.assertEquals(ResponseEnum.S3_UPLOAD_ERROR.getCode(), exception.getCode());
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void generatePresignedPutUrl_success() {
        // Prepare test data
        String objectKey = "test/presigned_" + System.currentTimeMillis() + ".txt";
        int expirySeconds = 3600;

        // Execute test
        String actualUrl = s3ClientUtil.generatePresignedPutUrl(TEST_BUCKET, objectKey, expirySeconds);

        // Verify result contains necessary components
        Assertions.assertNotNull(actualUrl);
        Assertions.assertTrue(actualUrl.startsWith(TEST_ENDPOINT));
        Assertions.assertTrue(actualUrl.contains(TEST_BUCKET));
        Assertions.assertTrue(actualUrl.contains(objectKey));
        Assertions.assertTrue(actualUrl.contains("X-Amz-Algorithm=AWS4-HMAC-SHA256"));
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void generatePresignedPutUrl_withInvalidCredentials() {
        // Create an S3ClientUtil using invalid credentials
        S3ClientUtil invalidS3ClientUtil = new S3ClientUtil();
        ReflectionTestUtils.setField(invalidS3ClientUtil, "endpoint", TEST_ENDPOINT);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "remoteEndpoint", TEST_REMOTE_ENDPOINT);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "accessKey", INVALID_ACCESS_KEY);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "secretKey", INVALID_SECRET_KEY);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "defaultBucket", TEST_BUCKET);

        // @PostConstruct method may throw BusinessException during initialization with invalid credentials
        try {
            invalidS3ClientUtil.init();
        } catch (BusinessException e) {
            // If initialization fails, verify it's the expected error
            Assertions.assertEquals(ResponseEnum.INTERNAL_SERVER_ERROR.getCode(), e.getCode());
            return; // Test passes - initialization correctly failed with invalid credentials
        }

        String objectKey = "test/should_fail.txt";
        int expirySeconds = 3600;

        // If initialization didn't fail, then presigned URL generation should fail
        BusinessException exception = Assertions.assertThrows(BusinessException.class,
                () -> invalidS3ClientUtil.generatePresignedPutUrl(TEST_BUCKET, objectKey, expirySeconds));

        Assertions.assertEquals(ResponseEnum.S3_PRESIGN_ERROR.getCode(), exception.getCode());
    }

    @Test
    void getDefaultBucket_success() {
        // Verify getter method
        String defaultBucket = s3ClientUtil.getDefaultBucket();
        Assertions.assertEquals(TEST_BUCKET, defaultBucket);
    }

    @Test
    void getPresignExpirySeconds_success() {
        // Verify getter method
        int presignExpirySeconds = s3ClientUtil.getPresignExpirySeconds();
        Assertions.assertEquals(600, presignExpirySeconds);
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_withDefaultBucket_success() {
        // Additional runtime check since @DisabledIf is evaluated at class loading time
        if (isMinioUnavailable()) {
            System.out.println("Skipping test - MinIO is unavailable");
            return;
        }

        // Prepare test data
        String objectKey = "test/default_bucket_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        byte[] testContent = "Test with default bucket".getBytes();
        InputStream inputStream = new ByteArrayInputStream(testContent);

        // Execute test - using default bucket
        String result = s3ClientUtil.uploadObject(objectKey, contentType, inputStream, testContent.length, -1);

        // Verify returned URL
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, result);
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void generatePresignedPutUrl_withDefaultBucketAndExpiry_success() {
        // Prepare test data
        String objectKey = "test/presigned_default_" + System.currentTimeMillis() + ".txt";

        // Execute test - using default bucket and expiry time
        String actualUrl = s3ClientUtil.generatePresignedPutUrl(objectKey);

        // Verify result
        Assertions.assertNotNull(actualUrl);
        Assertions.assertTrue(actualUrl.startsWith(TEST_ENDPOINT));
        Assertions.assertTrue(actualUrl.contains(TEST_BUCKET));
        Assertions.assertTrue(actualUrl.contains(objectKey));
        Assertions.assertTrue(actualUrl.contains("X-Amz-Algorithm=AWS4-HMAC-SHA256"));
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_withByteArray_success() {
        // Prepare test data
        String objectKey = "test/byte_array_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        byte[] data = "Test content from byte array".getBytes();

        // Execute test
        String result = s3ClientUtil.uploadObject(TEST_BUCKET, objectKey, contentType, data);

        // Verify returned URL
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, result);
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_simplified_success() {
        // Prepare test data
        String objectKey = "test/simplified_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        InputStream inputStream = new ByteArrayInputStream("Test simplified upload".getBytes());

        // Execute test - simplified version (auto detect size)
        String result = s3ClientUtil.uploadObject(TEST_BUCKET, objectKey, contentType, inputStream);

        // Verify returned URL
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, result);
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_toDefaultBucketWithByteArray_success() {
        // Prepare test data
        String objectKey = "test/default_bucket_byte_array_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        byte[] data = "Test content to default bucket from byte array".getBytes();

        // Execute test - upload to default bucket using byte array
        String result = s3ClientUtil.uploadObject(objectKey, contentType, data);

        // Verify returned URL
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, result);
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_toDefaultBucketSimplified_success() {
        // Prepare test data
        String objectKey = "test/default_bucket_simplified_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        InputStream inputStream = new ByteArrayInputStream("Test simplified upload to default bucket".getBytes());

        // Execute test - simplified version upload to default bucket
        String result = s3ClientUtil.uploadObject(objectKey, contentType, inputStream);

        // Verify returned URL
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, result);
    }

    // URL availability test helper method
    private boolean isUrlAccessible(String urlString) {
        try {
            URL url = new URL(urlString);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("HEAD");
            connection.setConnectTimeout(2000);
            connection.setReadTimeout(2000);
            int responseCode = connection.getResponseCode();
            connection.disconnect();
            return responseCode == 200;
        } catch (IOException e) {
            return false;
        }
    }

    private String readFromUrl(String urlString) throws IOException {
        URL url = new URL(urlString);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        connection.setConnectTimeout(2000);
        connection.setReadTimeout(2000);

        try (InputStream inputStream = connection.getInputStream()) {
            return new String(inputStream.readAllBytes());
        } finally {
            connection.disconnect();
        }
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_generatedUrlIsAccessible() {
        // Prepare test data
        String objectKey = "test/url_accessible_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        String testContent = "Test content for URL accessibility";
        byte[] testContentBytes = testContent.getBytes();
        InputStream inputStream = new ByteArrayInputStream(testContentBytes);

        // Execute upload
        String generatedUrl = s3ClientUtil.uploadObject(TEST_BUCKET, objectKey, contentType, inputStream, testContentBytes.length, -1);

        // Verify URL format (should be remote endpoint)
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, generatedUrl);

        // For testing actual access, use internal endpoint if remote endpoint is not accessible
        String accessUrl = TEST_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;

        // Verify if URL is accessible
        Assertions.assertTrue(isUrlAccessible(accessUrl),
                "Generated URL should be accessible: " + accessUrl);

        // Verify correct content can be read through URL
        try {
            String downloadedContent = readFromUrl(accessUrl);
            Assertions.assertEquals(testContent, downloadedContent,
                    "Content downloaded via URL should match uploaded content");
        } catch (IOException e) {
            Assertions.fail("Failed to read content via URL: " + e.getMessage());
        }
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_withByteArray_generatedUrlIsAccessible() {
        // Prepare test data
        String objectKey = "test/byte_array_url_accessible_" + System.currentTimeMillis() + ".txt";
        String contentType = "application/json";
        String testContent = "{\"message\": \"Hello from S3 byte array upload\", \"timestamp\": " + System.currentTimeMillis() + "}";
        byte[] data = testContent.getBytes();

        // Execute test
        String generatedUrl = s3ClientUtil.uploadObject(TEST_BUCKET, objectKey, contentType, data);

        // Verify URL format (should be remote endpoint)
        String expectedUrl = TEST_REMOTE_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertEquals(expectedUrl, generatedUrl);

        // For testing actual access, use internal endpoint if remote endpoint is not accessible
        String accessUrl = TEST_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;

        // Verify if URL is accessible
        Assertions.assertTrue(isUrlAccessible(accessUrl),
                "Generated URL should be accessible: " + accessUrl);

        // Verify correct content can be read through URL
        try {
            String downloadedContent = readFromUrl(accessUrl);
            Assertions.assertEquals(testContent, downloadedContent,
                    "Content downloaded via URL should match uploaded content");
        } catch (IOException e) {
            Assertions.fail("Failed to read content via URL: " + e.getMessage());
        }
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void generatePresignedPutUrl_canBeUsedForUpload() throws IOException {
        // Prepare test data
        String objectKey = "test/presigned_upload_" + System.currentTimeMillis() + ".txt";
        String testContent = "Content uploaded via presigned URL";
        byte[] testContentBytes = testContent.getBytes();

        // Generate presigned URL
        String presignedUrl = s3ClientUtil.generatePresignedPutUrl(TEST_BUCKET, objectKey, 600);

        // Verify presigned URL format
        Assertions.assertNotNull(presignedUrl);
        Assertions.assertTrue(presignedUrl.startsWith(TEST_ENDPOINT));
        Assertions.assertTrue(presignedUrl.contains(TEST_BUCKET));
        Assertions.assertTrue(presignedUrl.contains(objectKey));
        Assertions.assertTrue(presignedUrl.contains("X-Amz-Algorithm=AWS4-HMAC-SHA256"));

        // Upload file using presigned URL
        URL url = new URL(presignedUrl);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("PUT");
        connection.setDoOutput(true);
        connection.setRequestProperty("Content-Type", "text/plain");
        connection.setConnectTimeout(2000);
        connection.setReadTimeout(2000);

        try {
            connection.getOutputStream().write(testContentBytes);
            int responseCode = connection.getResponseCode();
            Assertions.assertEquals(200, responseCode,
                    "Presigned URL upload should succeed, response code should be 200");
        } finally {
            connection.disconnect();
        }

        // Verify uploaded file can be accessed via direct URL
        String directUrl = TEST_ENDPOINT + "/" + TEST_BUCKET + "/" + objectKey;
        Assertions.assertTrue(isUrlAccessible(directUrl),
                "Uploaded file should be accessible via direct URL");

        // Verify uploaded content is correct
        try {
            String downloadedContent = readFromUrl(directUrl);
            Assertions.assertEquals(testContent, downloadedContent,
                    "Content downloaded via direct URL should match uploaded content");
        } catch (IOException e) {
            Assertions.fail("Failed to read content via direct URL: " + e.getMessage());
        }
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void uploadObject_invalidUrl_shouldNotBeAccessible() {
        // Construct a non-existent URL (using internal endpoint for actual access test)
        String invalidUrl = TEST_ENDPOINT + "/" + TEST_BUCKET + "/nonexistent/file_" + System.currentTimeMillis() + ".txt";

        // Verify non-existent URL is not accessible
        Assertions.assertFalse(isUrlAccessible(invalidUrl),
                "Non-existent file URL should not be accessible");
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void generatePresignedGetUrl_success() {
        // First upload a test file
        String objectKey = "test/presigned_get_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        String testContent = "Test content for presigned GET URL";
        byte[] testContentBytes = testContent.getBytes();

        s3ClientUtil.uploadObject(TEST_BUCKET, objectKey, contentType, testContentBytes);

        // Generate presigned GET URL
        int expirySeconds = 3600;
        String presignedGetUrl = s3ClientUtil.generatePresignedGetUrl(TEST_BUCKET, objectKey, expirySeconds);

        // Verify presigned GET URL format
        Assertions.assertNotNull(presignedGetUrl);
        Assertions.assertTrue(presignedGetUrl.startsWith(TEST_ENDPOINT));
        Assertions.assertTrue(presignedGetUrl.contains(TEST_BUCKET));
        Assertions.assertTrue(presignedGetUrl.contains(objectKey));
        Assertions.assertTrue(presignedGetUrl.contains("X-Amz-Algorithm=AWS4-HMAC-SHA256"));

        // Verify can read content via presigned GET URL
        try {
            String downloadedContent = readFromUrl(presignedGetUrl);
            Assertions.assertEquals(testContent, downloadedContent,
                    "Content downloaded via presigned GET URL should match uploaded content");
        } catch (IOException e) {
            Assertions.fail("Failed to read content via presigned GET URL: " + e.getMessage());
        }
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void generatePresignedGetUrl_withDefaultBucketAndExpiry_success() {
        // First upload a test file to default bucket
        String objectKey = "test/presigned_get_default_" + System.currentTimeMillis() + ".txt";
        String contentType = "text/plain";
        String testContent = "Test content for presigned GET URL with defaults";
        byte[] testContentBytes = testContent.getBytes();

        s3ClientUtil.uploadObject(objectKey, contentType, testContentBytes);

        // Generate presigned GET URL using default bucket and expiry
        String presignedGetUrl = s3ClientUtil.generatePresignedGetUrl(objectKey);

        // Verify presigned GET URL format
        Assertions.assertNotNull(presignedGetUrl);
        Assertions.assertTrue(presignedGetUrl.startsWith(TEST_ENDPOINT));
        Assertions.assertTrue(presignedGetUrl.contains(TEST_BUCKET));
        Assertions.assertTrue(presignedGetUrl.contains(objectKey));
        Assertions.assertTrue(presignedGetUrl.contains("X-Amz-Algorithm=AWS4-HMAC-SHA256"));

        // Verify can read content via presigned GET URL
        try {
            String downloadedContent = readFromUrl(presignedGetUrl);
            Assertions.assertEquals(testContent, downloadedContent,
                    "Content downloaded via presigned GET URL should match uploaded content");
        } catch (IOException e) {
            Assertions.fail("Failed to read content via presigned GET URL: " + e.getMessage());
        }
    }

    @Test
    @DisabledIf("isMinioUnavailable")
    void generatePresignedGetUrl_withInvalidCredentials() {
        // Create an S3ClientUtil using invalid credentials
        S3ClientUtil invalidS3ClientUtil = new S3ClientUtil();
        ReflectionTestUtils.setField(invalidS3ClientUtil, "endpoint", TEST_ENDPOINT);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "remoteEndpoint", TEST_REMOTE_ENDPOINT);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "accessKey", INVALID_ACCESS_KEY);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "secretKey", INVALID_SECRET_KEY);
        ReflectionTestUtils.setField(invalidS3ClientUtil, "defaultBucket", TEST_BUCKET);

        // @PostConstruct method may throw BusinessException during initialization with invalid credentials
        try {
            invalidS3ClientUtil.init();
        } catch (BusinessException e) {
            // If initialization fails, verify it's the expected error
            Assertions.assertEquals(ResponseEnum.INTERNAL_SERVER_ERROR.getCode(), e.getCode());
            return; // Test passes - initialization correctly failed with invalid credentials
        }

        String objectKey = "test/should_fail.txt";
        int expirySeconds = 3600;

        // If initialization didn't fail, then presigned GET URL generation should fail
        BusinessException exception = Assertions.assertThrows(BusinessException.class,
                () -> invalidS3ClientUtil.generatePresignedGetUrl(TEST_BUCKET, objectKey, expirySeconds));

        Assertions.assertEquals(ResponseEnum.S3_PRESIGN_ERROR.getCode(), exception.getCode());
    }
}

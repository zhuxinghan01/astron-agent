package com.iflytek.astron.console.commons.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ResourceBundleMessageSource;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;

import java.io.InputStream;
import java.util.Locale;
import java.util.Properties;

/**
 * Debug configuration to check i18n resources at startup
 */
@Component
public class I18nDebugConfig implements CommandLineRunner {
    private static final Logger log = LoggerFactory.getLogger(I18nDebugConfig.class);

    private final ApplicationContext applicationContext;

    public I18nDebugConfig(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }

    @Override
    public void run(String... args) throws Exception {
        log.info("=== I18n Debug Information ===");
        
        // Check system encoding
        log.info("System file.encoding: {}", System.getProperty("file.encoding"));
        log.info("System console.encoding: {}", System.getProperty("console.encoding"));
        log.info("Default charset: {}", java.nio.charset.Charset.defaultCharset());
        log.info("System locale: {}", java.util.Locale.getDefault());
        
        // Check available message source beans
        String[] messageSourceBeans = applicationContext.getBeanNamesForType(org.springframework.context.MessageSource.class);
        log.info("Available MessageSource beans: {}", java.util.Arrays.toString(messageSourceBeans));
        
        // Check ResourceBundleMessageSource specifically
        try {
            ResourceBundleMessageSource rbms = applicationContext.getBean(ResourceBundleMessageSource.class);
            log.info("Found ResourceBundleMessageSource: {}", rbms.getClass().getName());
        } catch (Exception e) {
            log.info("No ResourceBundleMessageSource bean found: {}", e.getMessage());
        }
        
        // Check resource files existence and content
        checkResourceFile("classpath:messages.properties", "Default messages");
        checkResourceFile("classpath:messages_en.properties", "English messages");
        checkResourceFile("classpath:messages_zh_CN.properties", "Chinese messages");
        checkResourceFile("classpath:messages_zh.properties", "Chinese (generic) messages");
        
        // Test message resolution
        testMessageResolution();
        
        log.info("=== End I18n Debug Information ===");
    }
    
    private void checkResourceFile(String location, String description) {
        try {
            Resource resource = applicationContext.getResource(location);
            if (resource.exists()) {
                log.info("{} found at: {}", description, location);
                
                // Try to read a sample property
                try (InputStream is = resource.getInputStream()) {
                    Properties props = new Properties();
                    props.load(is);
                    String sampleValue = props.getProperty("database.table.delete.failed.cited");
                    log.info("{} - sample property 'database.table.delete.failed.cited': {}", 
                             description, sampleValue);
                } catch (Exception e) {
                    log.warn("Failed to read content from {}: {}", location, e.getMessage());
                }
            } else {
                log.info("{} NOT found at: {}", description, location);
            }
        } catch (Exception e) {
            log.warn("Error checking {}: {}", location, e.getMessage());
        }
    }
    
    private void testMessageResolution() {
        try {
            String testKey = "database.table.delete.failed.cited";
            
            // Test with different locales
            Locale[] testLocales = {
                Locale.SIMPLIFIED_CHINESE,
                Locale.forLanguageTag("zh-CN"),
                Locale.ENGLISH,
                Locale.US,
                Locale.forLanguageTag("zh")
            };
            
            for (Locale locale : testLocales) {
                try {
                    String message = applicationContext.getMessage(testKey, null, testKey, locale);
                    log.info("Message for locale {}: {}", locale, message);
                } catch (Exception e) {
                    log.warn("Failed to get message for locale {}: {}", locale, e.getMessage());
                }
            }
            
        } catch (Exception e) {
            log.error("Error during message resolution test", e);
        }
    }
}

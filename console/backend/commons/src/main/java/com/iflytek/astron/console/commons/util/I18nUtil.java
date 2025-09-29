package com.iflytek.astron.console.commons.util;

import org.springframework.context.ApplicationContext;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.servlet.LocaleResolver;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Locale;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Internationalization utility class for message retrieval and locale operations.
 *
 * The class relies on Spring's ApplicationContext for message resolution and HTTP request context
 * for locale information.
 *
 * @author Astron Console Team
 * @since 1.0
 */
public class I18nUtil {
    private static final Logger log = LoggerFactory.getLogger(I18nUtil.class);

    private I18nUtil() {}

    /**
     * Retrieve internationalization message by key
     *
     * @param msgKey the message key to look up in the resource bundle
     * @return the localized message string corresponding to the key, or the key itself if no message is
     *         found for the current locale
     */
    public static String getMessage(String msgKey) {
        return getMessage(msgKey, null);
    }

    /**
     * Retrieve internationalization message by key with arguments for placeholder substitution
     *
     * @param msgKey the message key to look up in the resource bundle
     * @param args array of arguments to substitute into message placeholders (e.g., {0}, {1}, {2}) Can
     *        be null if no arguments are needed
     * @return the localized message string with arguments substituted into placeholders, or the key
     *         itself if no message is found for the current locale
     */
    public static String getMessage(String msgKey, String[] args) {
        try {
            Locale locale = getRequestLocale();
            log.info("I18nUtil.getMessage - msgKey: {}, resolved locale: {}, args: {}",
                    msgKey, locale, args != null ? java.util.Arrays.toString(args) : "null");

            ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
            if (applicationContext != null) {
                try {
                    String message = applicationContext.getMessage(msgKey, args, msgKey, locale);
                    log.info("I18nUtil.getMessage - resolved message: {}", message);

                    // Additional debug: try to get the same message with different locales
                    try {
                        String zhMessage = applicationContext.getMessage(msgKey, args, msgKey, java.util.Locale.SIMPLIFIED_CHINESE);
                        String enMessage = applicationContext.getMessage(msgKey, args, msgKey, java.util.Locale.ENGLISH);
                        log.info("I18nUtil.getMessage - DEBUG: zh message: {}, en message: {}", zhMessage, enMessage);
                    } catch (Exception debugEx) {
                        log.warn("I18nUtil.getMessage - DEBUG failed: {}", debugEx.getMessage());
                    }

                    return message;
                } catch (org.springframework.context.NoSuchMessageException e) {
                    log.warn("I18nUtil.getMessage - NoSuchMessageException for key: {} with locale: {}, falling back to key", msgKey, locale);
                    return msgKey;
                }
            } else {
                log.warn("I18nUtil.getMessage - ApplicationContext is null, returning msgKey: {}", msgKey);
            }
        } catch (Exception e) {
            log.warn("Failed to get message for key: {}, falling back to key itself", msgKey, e);
        }
        return msgKey;
    }

    /**
     * Get the current user's language code from HTTP request Accept-Language header
     *
     * @return Possible language codes include but are not limited to: - "zh" (Chinese) - "en" (English)
     *         - "ja" (Japanese) - "ko" (Korean) - "fr" (French) - "de" (German) - "es" (Spanish) - "ru"
     *         (Russian) - "ar" (Arabic) and other ISO 639-1 standard two-letter lowercase language
     *         codes
     */
    public static String getLanguage() {
        return getRequestLocale().getLanguage().toLowerCase();
    }

    /**
     * Get the locale from the current HTTP request context This method retrieves the locale using
     * Spring's LocaleResolver, which respects both Accept-Language header and configured defaults
     *
     * @return the locale from request context, or configured default locale as fallback
     */
    private static Locale getRequestLocale() {
        try {
            ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            if (attributes != null) {
                HttpServletRequest request = attributes.getRequest();

                // Log request headers for debugging
                String acceptLanguage = request.getHeader("Accept-Language");
                String langParam = request.getParameter("lang");
                log.info("I18nUtil.getRequestLocale - Accept-Language header: {}, lang param: {}",
                        acceptLanguage, langParam);

                ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
                if (applicationContext != null) {
                    try {
                        LocaleResolver localeResolver = applicationContext.getBean(LocaleResolver.class);
                        Locale resolvedLocale = localeResolver.resolveLocale(request);
                        log.info("I18nUtil.getRequestLocale - LocaleResolver resolved locale: {}, resolver type: {}",
                                resolvedLocale, localeResolver.getClass().getSimpleName());
                        return resolvedLocale;
                    } catch (Exception e) {
                        log.warn("Failed to get LocaleResolver, falling back to request.getLocale()", e);
                        Locale requestLocale = request.getLocale();
                        log.info("I18nUtil.getRequestLocale - request.getLocale() returned: {}", requestLocale);
                        return requestLocale;
                    }
                } else {
                    log.warn("I18nUtil.getRequestLocale - ApplicationContext is null");
                    Locale requestLocale = request.getLocale();
                    log.info("I18nUtil.getRequestLocale - request.getLocale() returned: {}", requestLocale);
                    return requestLocale;
                }
            } else {
                log.warn("I18nUtil.getRequestLocale - ServletRequestAttributes is null");
            }
        } catch (Exception e) {
            log.warn("Failed to get locale from request context, falling back to en_US", e);
        }
        Locale fallbackLocale = Locale.US;
        log.info("I18nUtil.getRequestLocale - falling back to: {}", fallbackLocale);
        return fallbackLocale;
    }
}

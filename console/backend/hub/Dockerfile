FROM artifacts.iflytek.com/cbg-docker-private/xfyun_webdev/eclipse-temurin:21-jre
WORKDIR /app

# Set timezone to China mainland timezone
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/"$TZ" /etc/localtime && echo "$TZ" > /etc/timezone

# Set Chinese UTF-8 environment
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8

# Change apt source to USTC mirror and install Chinese language pack and fonts
#RUN apt-get update && \
#    apt-get install -y fonts-dejavu-core fonts-wqy-microhei locales && \
#    sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen && \
#    locale-gen && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*

COPY console/backend/hub/target/hub-0.0.1.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]



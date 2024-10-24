package com.ohgiraffers.apirequest.config;

// Spring의 설정 클래스를 나타내는 어노테이션
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.client.WebClient;

// WebClientConfig 클래스는 WebClient를 구성하는 설정 클래스입니다.
@Configuration
public class WebClientConfig {

    // WebClient.Builder 빈을 생성하는 메서드
    @Bean
    public WebClient.Builder webClientBuilder() {
        // WebClient.Builder를 초기화하고 기본 헤더를 설정
        return WebClient.builder()
                // 모든 요청에 대해 Content-Type 헤더를 JSON으로 설정
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE);
    }
}

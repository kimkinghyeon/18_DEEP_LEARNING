package com.ohgiraffers.apirequest.section02;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class TextService {

    private final WebClient webClient;

    public TextService(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
    }

    public Mono<TextResponse> summarizeText(String text) {
        return this.webClient.post()
                .uri("/en-summarize/")
                .bodyValue(new TextRequest(text))  // 요청 본문 설정
                .retrieve()
                .onStatus(status -> status.is4xxClientError(), response ->
                        Mono.error(new RuntimeException("Client error: " + response.statusCode()))
                )
                .onStatus(status -> status.is5xxServerError(), response ->
                        Mono.error(new RuntimeException("Server error: " + response.statusCode()))
                )
                .bodyToMono(TextResponse.class)  // 응답을 TextResponse 클래스로 변환
                .onErrorResume(e -> {
                    // 에러 발생 시 처리할 로직
                    return Mono.just(new TextResponse("Error occurred: " + e.getMessage(), null));
                });
    }

    // 응답에 사용할 DTO 클래스
    public static class TextResponse {
        private String summary;
        private String translated_summary;

        public TextResponse() {
        }

        public TextResponse(String summary, String translated_summary) {
            this.summary = summary;
            this.translated_summary = translated_summary;
        }

        public void setSummary(String summary) {
            this.summary = summary;
        }

        public void setTranslated_summary(String translated_summary) {
            this.translated_summary = translated_summary;
        }

        public String getSummary() {
            return summary;
        }

        public String getTranslated_summary() {
            return translated_summary;
        }
    }

    // 요청에 사용할 DTO 클래스
    public static class TextRequest {
        private String text;

        public TextRequest(String text) {
            this.text = text;
        }

        public String getText() {
            return text;
        }

        public void setText(String text) {
            this.text = text;
        }
    }
}

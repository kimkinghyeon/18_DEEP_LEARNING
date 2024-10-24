package com.ohgiraffers.apirequest.section02;

import com.ohgiraffers.apirequest.section02.dto.RequestDTO;
import com.ohgiraffers.apirequest.section02.dto.ResponseDTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

/*
* spring 에서 외부 api 요청 및 처리
*
* 대표적인 라이브러리
* - HttpClient
* - RestTemplate
* - WebClient
* - OpenFeign
*
* 주의할점
* - request 와 response 가 외부 서버와 맞게 설정되어있는지 확인!
* */

@RestController
@RequestMapping("/translate")
@Slf4j
public class TransactionController {

    private final TextService textService;

    public TransactionController( TextService textService) {

        this.textService = textService;
    }

    // 생성자 주입

    // WebClient를 사용하는 API 호출
    @PostMapping("/webclient")
    public Mono<ResponseDTO> translateByWebClient(@RequestBody String text) {
        log.info("번역[WebClient] Controller 요청 들어옴...");
        log.info("text: {}", text);

        // WebClient를 사용한 비동기 처리
        return textService.summarizeText(text)
                .map(response -> new ResponseDTO(response));
    }
}


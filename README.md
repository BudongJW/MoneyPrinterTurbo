# MoneyPrinterTurbo - 자동 숏폼 영상 생성 파이프라인

주제(키워드)만 입력하면 **영상 문안 → 스톡 영상 → TTS 음성 → 자막 → BGM** 을 자동 생성하고,
TikTok까지 자동 업로드하는 파이프라인.

> 원본: [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) (v1.2.6)

---

## 구성

| 구성 요소 | 역할 | 비용 |
|---|---|---|
| Pollinations AI | 영상 스크립트 생성 (LLM) | 무료 |
| Pexels API | 스톡 영상 소싱 | 무료 |
| Edge TTS | 음성 합성 (en-US-AriaNeural) | 무료 |
| social-auto-upload | TikTok 자동 업로드 (Playwright) | 무료 |

## 사전 준비

1. **Python 3.10+** 설치
2. **ImageMagick** 설치 (자막 합성용)
3. **ffmpeg** 설치 및 PATH 등록

```bash
# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (TikTok 업로드용)
playwright install chromium
```

## 설정

`config.toml` 주요 항목:

```toml
[app]
llm_provider = "pollinations"        # 무료 LLM
video_language = "en-US"

[app.pollinations]
pollinations_base_url = "https://text.pollinations.ai/openai"
pollinations_model_name = "openai-fast"

[app.pexels]
pexels_api_keys = ["YOUR_PEXELS_KEY"]   # https://www.pexels.com/api/ 에서 발급
```

## 실행 방법

### 1. WebUI (수동)

```bash
streamlit run webui/Main.py
```

브라우저에서 `http://localhost:8501` 접속 → 주제 입력 → 영상 생성

### 2. 자동 파이프라인 (영상 생성 + TikTok 업로드)

```bash
# 랜덤 주제로 실행
python auto_pipeline.py

# 주제 지정
python auto_pipeline.py Why cats make the best pets
```

또는 `run_pipeline.bat` 더블클릭.

### 3. 스케줄러 (매일 자동 실행)

```bash
# 관리자 권한으로 실행 → 매일 10:00 자동 실행 등록
setup_scheduler.bat
```

Windows 작업 스케줄러에 `AutoVideoPipeline` 태스크가 등록됨.

## 파이프라인 흐름

```
auto_pipeline.py
  │
  ├─ [1/3] 영상 생성 (MoneyPrinterTurbo)
  │    └─ Pollinations AI → 스크립트 생성
  │    └─ Pexels API → 스톡 영상 다운로드
  │    └─ Edge TTS → 음성 합성
  │    └─ MoviePy → 영상 합성 (1080x1920, 9:16)
  │
  ├─ [2/3] 업로드 준비
  │    └─ 영상 파일 복사 → social-auto-upload/videos/
  │    └─ 메타데이터 .txt 생성 (제목 + 해시태그)
  │
  └─ [3/3] TikTok 업로드
       └─ Playwright 헤드리스 → TikTok Studio 자동 업로드
```

## TikTok 쿠키 설정 (최초 1회)

```bash
cd ../social-auto-upload
python -c "
import asyncio
from uploader.tk_uploader.main_chrome import tiktok_setup
asyncio.run(tiktok_setup('cookies/tk_uploader/account.json', handle=True))
"
```

브라우저가 열리면 TikTok 로그인 → 디버거 ▶ 버튼 클릭 → 쿠키 저장됨.

## 수정 사항 (원본 대비)

- **Edge TTS 7.x 호환**: `CompatSubMaker` 래퍼 (6.x/7.x 동시 지원)
- **VideoTransitionMode None 크래시 수정**
- **한국어 WebUI 지원** (`webui/i18n/ko.json`)
- **auto_pipeline.py**: 영상 생성 → TikTok 업로드 통합 스크립트
- **Pollinations AI 연동**: 무료 LLM (API 키 불필요)

## 디렉토리 구조

```
MoneyPrinterTurbo/
├── auto_pipeline.py       # 자동 파이프라인 (생성→업로드)
├── run_pipeline.bat       # 실행 배치
├── setup_scheduler.bat    # 스케줄러 등록 배치
├── config.toml            # 설정 파일
├── app/
│   └── services/
│       ├── voice.py       # TTS (Edge TTS 7.x 호환)
│       └── video.py       # 영상 합성
└── webui/
    ├── Main.py            # Streamlit WebUI
    └── i18n/ko.json       # 한국어 번역
```

## 라이선스

MIT License - 원본 프로젝트 라이선스를 따름.

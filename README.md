# MoneyPrinterTurbo - 자동 숏폼 영상 생성 파이프라인

주제(키워드)만 입력하면 **영상 문안 → 스톡 영상 → TTS 음성 → 자막 → BGM** 을 자동 생성하고,
TikTok까지 자동 업로드하는 파이프라인.

> 원본: [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) (v1.2.6)

---

## 전체 구성도

```
부모 폴더/
├── MoneyPrinterTurbo/      ← 이 레포 (영상 생성)
└── social-auto-upload/     ← TikTok 업로드 레포 (같은 폴더에 클론)
```

두 레포는 반드시 **같은 부모 폴더** 아래에 나란히 위치해야 합니다.
`auto_pipeline.py`가 상대경로(`../social-auto-upload`)로 업로드 레포를 참조합니다.

## 사용하는 API (전부 무료)

| 구성 요소 | 역할 | 비용 | 키 필요 |
|---|---|---|---|
| Pollinations AI | 영상 스크립트 생성 (LLM) | 무료 | X |
| Pexels API | 스톡 영상 소싱 | 무료 | O (무료 발급) |
| Edge TTS | 음성 합성 (en-US-AriaNeural) | 무료 | X |
| social-auto-upload | TikTok 자동 업로드 (Playwright) | 무료 | X |

---

## 처음부터 세팅하기 (Step by Step)

### Step 1. 사전 설치

아래 3개가 시스템에 설치되어 있어야 합니다.

| 프로그램 | 설치 방법 | 확인 명령 |
|---|---|---|
| Python 3.10~3.12 | [python.org](https://www.python.org/downloads/) 다운로드. 설치 시 **Add to PATH** 체크 | `python --version` |
| ImageMagick | [imagemagick.org](https://imagemagick.org/script/download.php#windows) → Windows Binary 설치. 설치 시 **Install legacy utilities** 체크 | `magick --version` |
| ffmpeg | [ffmpeg.org](https://ffmpeg.org/download.html) → Windows builds 다운로드 → `bin/` 폴더를 시스템 PATH에 추가 | `ffmpeg -version` |

### Step 2. 두 레포 클론

```bash
# 원하는 폴더에서 실행 (예: C:\Projects)
git clone https://github.com/BudongJW/MoneyPrinterTurbo.git
git clone https://github.com/BudongJW/social-auto-upload.git
```

> 두 폴더가 **같은 부모 디렉토리**에 나란히 있어야 합니다.

### Step 3. MoneyPrinterTurbo 의존성 설치

```bash
cd MoneyPrinterTurbo

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 의존성 설치
pip install -r requirements.txt
```

### Step 4. social-auto-upload 의존성 설치

```bash
cd ../social-auto-upload

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate        # Windows

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### Step 5. Pexels API 키 발급 (무료)

1. [pexels.com/api](https://www.pexels.com/api/) 접속
2. **Join** 클릭 → 회원가입 (구글 로그인 가능)
3. **Your API Key** 페이지에서 키 복사

### Step 6. MoneyPrinterTurbo 설정 (config.toml)

```bash
cd ../MoneyPrinterTurbo

# 예제 설정 파일 복사
copy config.example.toml config.toml     # Windows
# cp config.example.toml config.toml     # Mac/Linux
```

`config.toml`을 열어서 아래 항목만 수정:

```toml
[app]
llm_provider = "pollinations"          # ← 이것으로 변경 (무료, 키 불필요)

[app.pollinations]
pollinations_base_url = "https://text.pollinations.ai/openai"
pollinations_model_name = "openai-fast"

[app.pexels]
pexels_api_keys = ["여기에_Pexels_API_키_붙여넣기"]
```

> 나머지 설정은 기본값 그대로 두면 됩니다.

### Step 7. social-auto-upload 설정 (conf.py)

```bash
cd ../social-auto-upload

# 예제 설정 파일 복사
copy conf.example.py conf.py            # Windows
# cp conf.example.py conf.py            # Mac/Linux
```

`conf.py`를 열어서 확인:

```python
LOCAL_CHROME_PATH = ""          # 빈 문자열 = Playwright 내장 Chromium 사용 (수정 불필요)
LOCAL_CHROME_HEADLESS = True    # True = 헤드리스 자동화 모드
```

### Step 8. TikTok 로그인 (최초 1회)

```bash
cd social-auto-upload

python -c "
import asyncio
from uploader.tk_uploader.main_chrome import tiktok_setup
asyncio.run(tiktok_setup('cookies/tk_uploader/account.json', handle=True))
"
```

1. Chromium 브라우저가 열림 (헤드리스가 아닌 일반 모드로 열림)
2. TikTok에 로그인 (구글/이메일/전화번호 등)
3. 로그인 완료 후 Playwright Inspector 창에서 **▶ Resume** 버튼 클릭
4. `cookies/tk_uploader/account.json`에 쿠키가 저장됨

> 쿠키가 만료되면 이 과정을 다시 실행하면 됩니다.

---

## 실행 방법

### 방법 1. 자동 파이프라인 (영상 생성 + TikTok 업로드)

```bash
cd MoneyPrinterTurbo
venv\Scripts\activate

# 랜덤 주제로 실행
python auto_pipeline.py

# 주제 지정
python auto_pipeline.py Why cats make the best pets
```

또는 `run_pipeline.bat` 더블클릭.

### 방법 2. WebUI (수동, 영상 생성만)

```bash
cd MoneyPrinterTurbo
venv\Scripts\activate
streamlit run webui/Main.py
```

브라우저에서 `http://localhost:8501` 접속 → 주제 입력 → 영상 생성.

### 방법 3. 매일 자동 실행 (Windows 작업 스케줄러)

```bash
# 관리자 권한으로 실행
setup_scheduler.bat
```

매일 오전 10시에 `AutoVideoPipeline` 태스크가 자동 실행됨.

---

## 파이프라인 흐름

```
auto_pipeline.py
  │
  ├─ [1/3] 영상 생성 (MoneyPrinterTurbo)
  │    ├─ Pollinations AI → 스크립트 생성
  │    ├─ Pexels API → 스톡 영상 다운로드
  │    ├─ Edge TTS → 음성 합성
  │    └─ MoviePy → 영상 합성 (1080x1920, 9:16)
  │
  ├─ [2/3] 업로드 준비
  │    ├─ 영상 파일 복사 → social-auto-upload/videos/
  │    └─ 메타데이터 .txt 생성 (제목 + 해시태그)
  │
  └─ [3/3] TikTok 업로드
       └─ Playwright 헤드리스 → TikTok Studio 자동 업로드
```

## 환경변수 (선택)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `SOCIAL_UPLOAD_DIR` | `../social-auto-upload` | social-auto-upload 경로가 다른 위치일 때 지정 |

## 트러블슈팅

| 증상 | 해결 |
|---|---|
| `magick: command not found` | ImageMagick 설치 후 터미널 재시작 |
| `ffmpeg: command not found` | ffmpeg PATH 등록 후 터미널 재시작 |
| 영상 생성 시 Pexels 에러 | config.toml의 `pexels_api_keys` 확인 |
| TikTok 업로드 실패 | 쿠키 만료 → Step 8 다시 실행 |
| `ENOENT` 에러 | `conf.py`의 `LOCAL_CHROME_PATH = ""` 확인 |
| 영상은 생성되지만 업로드 안 됨 | 두 레포가 같은 부모 폴더에 있는지 확인 |

## 수정 사항 (원본 대비)

- **Edge TTS 7.x 호환**: `CompatSubMaker` 래퍼 (6.x/7.x 동시 지원)
- **VideoTransitionMode None 크래시 수정**
- **한국어 WebUI 지원** (`webui/i18n/ko.json`)
- **auto_pipeline.py**: 영상 생성 → TikTok 업로드 통합 스크립트
- **Pollinations AI 연동**: 무료 LLM (API 키 불필요)
- **UPLOAD_DIR 상대경로**: 하드코딩 → `../social-auto-upload` 기본값

## 디렉토리 구조

```
MoneyPrinterTurbo/
├── auto_pipeline.py       # 자동 파이프라인 (생성→업로드)
├── run_pipeline.bat       # 실행 배치
├── setup_scheduler.bat    # 스케줄러 등록 배치
├── config.toml            # 설정 파일 (config.example.toml에서 복사)
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

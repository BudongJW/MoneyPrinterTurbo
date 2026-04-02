# MoneyPrinterTurbo - 자동 숏폼 영상 생성 + TikTok & YouTube Shorts 업로드 파이프라인

주제(키워드)만 입력하면 **영상 스크립트 → 스톡 영상 → TTS 음성 → BGM** 을 자동 생성하고,
**TikTok + YouTube Shorts**까지 자동 업로드한 뒤 **임시 파일을 전부 삭제**하는 완전 자동 파이프라인.

**모든 API 무료** / 별도 서버 불필요 / Windows 배치파일 더블클릭으로 실행

> 원본: [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) (v1.2.6) + [dreammis/social-auto-upload](https://github.com/dreammis/social-auto-upload)

---

## 전체 구성도

```
부모 폴더/
├── MoneyPrinterTurbo/      ← 이 레포 (영상 생성 + 파이프라인)
└── social-auto-upload/     ← TikTok & YouTube 업로드 레포 (같은 폴더에 클론)
```

두 레포는 반드시 **같은 부모 폴더** 아래에 나란히 위치해야 합니다.

## 사용하는 API (전부 무료)

| 구성 요소 | 역할 | 비용 | 키 필요 | 가입 링크 |
|---|---|---|---|---|
| [Pollinations AI](https://pollinations.ai/) | 영상 스크립트 생성 (LLM) | 무료 | X | 가입 불필요 |
| [Pexels API](https://www.pexels.com/api/) | 스톡 영상 소싱 | 무료 | **O** | [가입 및 키 발급](https://www.pexels.com/api/new/) |
| [Edge TTS](https://github.com/rany2/edge-tts) | 음성 합성 (Microsoft) | 무료 | X | 가입 불필요 |
| [Playwright](https://playwright.dev/) | TikTok & YouTube 자동 업로드 | 무료 | X | 가입 불필요 |

> Pexels API 키만 발급받으면 됩니다. 나머지는 설치만 하면 동작합니다.

---

## 설정 가이드 (Step by Step)

### Step 1. 사전 설치 프로그램 3개

| 프로그램 | 다운로드 링크 | 설치 시 주의사항 | 설치 확인 |
|---|---|---|---|
| **Python 3.10~3.12** | [python.org/downloads](https://www.python.org/downloads/) | 설치 시 **"Add Python to PATH"** 반드시 체크 | `python --version` |
| **ImageMagick** | [imagemagick.org (Windows)](https://imagemagick.org/script/download.php#windows) | 설치 시 **"Install legacy utilities (e.g. convert)"** 체크 | `magick --version` |
| **ffmpeg** | [gyan.dev/ffmpeg (권장)](https://www.gyan.dev/ffmpeg/builds/) → `ffmpeg-release-essentials.zip` | 압축 해제 후 `bin/` 폴더를 [시스템 PATH에 추가](https://dora-guide.com/ffmpeg-install/) | `ffmpeg -version` |

> Python 3.13 이상은 일부 라이브러리 호환 문제가 있을 수 있습니다. **3.10~3.12 권장**.

### Step 2. 두 레포 클론

```bash
# 원하는 폴더에서 실행 (예: C:\Projects)
git clone https://github.com/BudongJW/MoneyPrinterTurbo.git
git clone https://github.com/BudongJW/social-auto-upload.git
```

> Git이 없다면: [git-scm.com](https://git-scm.com/download/win) 에서 설치하세요.

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

# Playwright 브라우저 설치 (Chromium 자동 다운로드)
playwright install chromium
```

### Step 5. Pexels API 키 발급 (무료, 1분 소요)

1. **[pexels.com/api/new](https://www.pexels.com/api/new/)** 접속
2. 회원가입 (구글 로그인 가능) → 간단한 설문 응답
3. **API Key** 페이지에서 키 복사 (예: `RCy2zYHh...`)

> Pexels는 월 200회 무료 요청을 제공합니다. 숏폼 1개 만들 때 약 15회 사용하므로, 매일 1개씩 만들어도 충분합니다.

### Step 6. MoneyPrinterTurbo 설정 (config.toml)

```bash
cd ../MoneyPrinterTurbo

# 예제 설정 파일 복사
copy config.example.toml config.toml     # Windows
# cp config.example.toml config.toml     # Mac/Linux
```

`config.toml`을 메모장이나 에디터로 열어서 **아래 3곳만 수정**:

```toml
# 1) LLM 프로바이더를 pollinations로 변경 (무료, 키 불필요)
[app]
llm_provider = "pollinations"

# 2) Pollinations 기본 URL 확인 (보통 이미 설정되어 있음)
[app.pollinations]
pollinations_base_url = "https://text.pollinations.ai/openai"
pollinations_model_name = "openai-fast"

# 3) Pexels API 키 입력 (Step 5에서 복사한 키)
[app.pexels]
pexels_api_keys = ["여기에_Pexels_API_키_붙여넣기"]
```

> 나머지 설정은 **기본값 그대로** 두면 됩니다.

### Step 7. social-auto-upload 설정 (conf.py)

```bash
cd ../social-auto-upload

# 예제 설정 파일 복사
copy conf.example.py conf.py            # Windows
# cp conf.example.py conf.py            # Mac/Linux
```

`conf.py`에서 아래 2줄만 확인:

```python
LOCAL_CHROME_PATH = ""          # 빈 문자열 그대로 두기 (Playwright 내장 Chromium 사용)
LOCAL_CHROME_HEADLESS = True    # True = 백그라운드 자동 업로드
```

> 수정할 게 없으면 복사만 하면 됩니다.

### Step 8. TikTok 로그인 (최초 1회)

```bash
cd social-auto-upload
venv\Scripts\activate

python -c "
import asyncio
from uploader.tk_uploader.main_chrome import tiktok_setup
asyncio.run(tiktok_setup('cookies/tk_uploader/account.json', handle=True))
"
```

1. Chromium 브라우저가 열리고 [TikTok](https://www.tiktok.com/) 로그인 페이지로 이동
2. **구글/이메일/전화번호** 등으로 로그인
3. 로그인 완료 후 Playwright Inspector 창(작은 컨트롤 패널)에서 **▶ Resume** 버튼 클릭
4. `cookies/tk_uploader/account.json`에 세션 쿠키가 저장됨

> 쿠키가 만료되면(보통 며칠~2주) 이 과정을 다시 실행하면 됩니다.
> 만료 증상: 실행 시 "Cookie expired. Re-login required." 메시지 출력.

### Step 9. YouTube Shorts 로그인 (선택사항, 최초 1회)

YouTube Shorts에도 동시 업로드하고 싶다면 아래 과정을 진행하세요.
**건너뛰면 TikTok만 업로드됩니다.**

```bash
cd social-auto-upload
venv\Scripts\activate

python -c "
import asyncio
from uploader.yt_uploader.main_chrome import youtube_setup
asyncio.run(youtube_setup('cookies/yt_uploader/account.json', handle=True))
"
```

1. Chromium 브라우저가 열리고 [Google 로그인](https://accounts.google.com/) 페이지로 이동
2. YouTube 채널이 연결된 **Google 계정**으로 로그인
3. 로그인 완료 후 Playwright Inspector 창에서 **▶ Resume** 버튼 클릭
4. `cookies/yt_uploader/account.json`에 세션 쿠키가 저장됨

> YouTube 쿠키도 만료 시 이 과정을 다시 실행하면 됩니다.
> YouTube 채널이 없으면 [YouTube Studio](https://studio.youtube.com/)에서 먼저 채널을 만드세요.

---

## 실행 방법

### 방법 1. 배치파일 더블클릭 (가장 간단)

```
MoneyPrinterTurbo 폴더 → run_pipeline.bat 더블클릭
```

venv 자동 감지 → 랜덤 주제 선택 → 영상 생성 → TikTok 업로드 → YouTube Shorts 업로드(쿠키 있으면) → 파일 정리 → 자동 종료.

### 방법 2. 터미널에서 실행

```bash
cd MoneyPrinterTurbo
venv\Scripts\activate

# 랜덤 주제로 실행
python auto_pipeline.py

# 주제 직접 지정
python auto_pipeline.py Top 10 life hacks everyone should know
```

### 방법 3. WebUI (영상 생성만, 업로드 없음)

```bash
cd MoneyPrinterTurbo
venv\Scripts\activate
streamlit run webui/Main.py
```

브라우저에서 `http://localhost:8501` 접속 → 주제 입력 → 영상 생성.

### 방법 4. 매일 자동 실행 (Windows 작업 스케줄러)

```bash
# 관리자 권한으로 실행
setup_scheduler.bat
```

매일 오전 10시에 자동 실행됨. 스케줄 변경: 작업 스케줄러 → `AutoVideoPipeline` 편집.

---

## 파이프라인 흐름

```
run_pipeline.bat (또는 python auto_pipeline.py)
  │
  ├─ [1/4] 영상 생성 (~3분)
  │    ├─ Pollinations AI → 스크립트 자동 생성
  │    ├─ Pexels API → 스톡 영상 15개 내외 다운로드
  │    ├─ Edge TTS → 영어 여성 음성 합성
  │    └─ MoviePy → 클립 합성 (1080x1920, 9:16 세로)
  │
  ├─ [2/4] 업로드 준비
  │    ├─ 영상 파일 복사 → social-auto-upload/videos/
  │    └─ 메타데이터 .txt 생성 (제목 + 해시태그)
  │
  ├─ [3/4] TikTok 업로드 (~30초)
  │    └─ Playwright 헤드리스 → TikTok Studio 자동 업로드
  │
  ├─ [4/4] YouTube Shorts 업로드 (~1분, 쿠키 있을 때만)
  │    └─ Playwright 헤드리스 → YouTube Studio 자동 업로드
  │
  └─ [완료] 자동 정리 (~300MB 임시 파일 삭제)
```

## 주제 커스터마이징

`auto_pipeline.py`의 `TOPICS` 리스트를 수정하면 원하는 주제로 변경 가능:

```python
TOPICS = [
    "Top 5 iconic Kpop dance moves everyone should learn",
    "Why Korean school uniforms became a global fashion trend",
    "Best Kpop girl group choreography of 2024",
    # ... 원하는 주제를 영어로 추가
]
```

> 주제는 **영어**로 작성해야 Pexels에서 관련 영상을 잘 찾습니다.

## 환경변수 (선택)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `SOCIAL_UPLOAD_DIR` | `../social-auto-upload` | social-auto-upload 경로가 다른 위치일 때 지정 |

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `python` 명령이 안 됨 | Python PATH 미등록 | 재설치 시 **Add to PATH** 체크, 또는 `py` 명령 사용 |
| `magick: command not found` | ImageMagick 미설치/PATH 미등록 | [ImageMagick 재설치](https://imagemagick.org/script/download.php#windows) 후 터미널 재시작 |
| `ffmpeg: command not found` | ffmpeg PATH 미등록 | [ffmpeg PATH 등록 가이드](https://dora-guide.com/ffmpeg-install/) 참고 |
| `pip install` 에러 | Python 버전 문제 | Python 3.10~3.12 사용 권장 |
| 영상 생성 시 Pexels 에러 | API 키 미입력/잘못됨 | `config.toml`의 `pexels_api_keys` 확인 |
| TikTok 업로드 실패 | 쿠키 만료 | Step 8 다시 실행 |
| YouTube 업로드 실패 | 쿠키 만료 | Step 9 다시 실행 |
| YouTube 채널 없음 | 채널 미생성 | [YouTube Studio](https://studio.youtube.com/)에서 채널 생성 |
| `ENOENT` 에러 | Chrome 경로 문제 | `conf.py`의 `LOCAL_CHROME_PATH = ""` 확인 |
| 영상 생성 OK, 업로드 안 됨 | 폴더 구조 문제 | 두 레포가 같은 부모 폴더에 있는지 확인 |
| `playwright install` 실패 | 네트워크/권한 문제 | 관리자 권한 터미널에서 재시도 |
| 영상이 안 만들어짐 | Pollinations AI 일시 장애 | 몇 분 후 재시도 |

## FAQ

**Q. 비용이 정말 0원인가요?**
A. 네. Pollinations AI, Pexels, Edge TTS 모두 무료입니다. TikTok 계정만 있으면 됩니다.

**Q. YouTube Shorts도 같이 올라가나요?**
A. Step 9에서 YouTube 로그인을 완료했다면, 파이프라인 실행 시 TikTok과 YouTube Shorts에 **동시 업로드**됩니다. YouTube 로그인을 안 했으면 TikTok만 업로드됩니다.

**Q. 하루에 몇 개까지 올릴 수 있나요?**
A. TikTok/YouTube 정책상 과도한 업로드는 제한될 수 있습니다. 하루 1~3개 정도가 안전합니다.

**Q. Mac/Linux에서도 되나요?**
A. 영상 생성은 됩니다. `run_pipeline.bat`은 Windows 전용이므로 터미널에서 `python auto_pipeline.py`로 실행하세요.

**Q. 주제를 한국어로 쓸 수 있나요?**
A. 가능하지만, Pexels 스톡 영상 검색이 영어 기반이라 영어 주제가 더 좋은 결과를 줍니다.

---

## 수정 사항 (원본 대비)

- **Edge TTS 7.x 호환**: `CompatSubMaker` 래퍼 (6.x/7.x 동시 지원)
- **VideoTransitionMode None 크래시 수정**
- **한국어 WebUI 지원** (`webui/i18n/ko.json`)
- **auto_pipeline.py**: 영상 생성 → TikTok + YouTube Shorts 업로드 → 자동 정리 통합 스크립트
- **Pollinations AI 연동**: 무료 LLM (API 키 불필요)
- **자동 파일 정리**: 업로드 완료 후 임시 파일 자동 삭제 (~300MB/회)
- **배치파일**: venv 자동 감지, 완료 후 자동 종료

## 디렉토리 구조

```
MoneyPrinterTurbo/
├── auto_pipeline.py          # 자동 파이프라인 (생성→업로드→정리)
├── run_pipeline.bat          # 실행 배치 (더블클릭)
├── setup_scheduler.bat       # Windows 스케줄러 등록
├── config.toml               # 설정 파일 (config.example.toml에서 복사)
├── config.example.toml       # 설정 예제
├── storage/                  # 임시 파일 (자동 삭제됨)
├── app/services/             # 핵심 로직 (voice.py, video.py, llm.py)
└── webui/                    # Streamlit WebUI
```

## 라이선스

MIT License - 원본 프로젝트 라이선스를 따름.

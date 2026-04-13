# arxiv2md 레포지토리 구조 분석

> **기여자를 위한 가이드** — 코드 기여 전에 이 문서를 읽어 레포의 전체 구조와 각 구성요소의 역할을 파악하세요.

---

## 목차

1. [개요](#개요)
2. [디렉토리 구조](#디렉토리-구조)
3. [핵심 라이브러리 (`src/arxiv2md/`)](#핵심-라이브러리-srcarxiv2md)
4. [웹 서버 (`src/server/`)](#웹-서버-srcserver)
5. [정적 파일 (`src/static/`)](#정적-파일-srcstatic)
6. [테스트 (`tests/`)](#테스트-tests)
7. [배포 및 인프라 파일](#배포-및-인프라-파일)
8. [데이터 흐름 다이어그램](#데이터-흐름-다이어그램)
9. [코드 수정 후 테스트 방법](#코드-수정-후-테스트-방법)

---

## 개요

`arxiv2md`는 arXiv 논문을 깔끔한 마크다운으로 변환하는 도구입니다. PDF 파싱 대신 arXiv가 제공하는 구조화된 HTML을 직접 파싱하여 수식(MathML → LaTeX), 표, 섹션 구조를 정확하게 변환합니다.

세 가지 인터페이스를 제공합니다:

| 인터페이스 | 위치 | 설명 |
|-----------|------|------|
| **Python 라이브러리** | `src/arxiv2md/` | `ingest_paper()`, `ingest_paper_sync()` 함수 |
| **CLI** | `src/arxiv2md/__main__.py` | `arxiv2md <arXiv-ID>` 커맨드 |
| **웹 앱 / REST API** | `src/server/` | FastAPI 기반 웹 서버 |

---

## 디렉토리 구조

```
arxiv2md/
├── src/                            # 소스 코드 루트
│   ├── arxiv2md/                   # 핵심 라이브러리 패키지 (pip 배포 대상)
│   │   ├── __init__.py             # 공개 API 정의
│   │   ├── __main__.py             # CLI 진입점
│   │   ├── cache.py                # 캐시 관리 (삭제/만료 처리)
│   │   ├── config.py               # 환경변수 기반 설정값
│   │   ├── fetch.py                # arXiv HTML 다운로드 (재시도/캐싱)
│   │   ├── html_parser.py          # HTML → 구조화된 섹션 트리 파싱
│   │   ├── ingestion.py            # 전체 수집 파이프라인 조율
│   │   ├── markdown.py             # HTML 섹션 → 마크다운 변환기
│   │   ├── output_formatter.py     # 최종 출력 조합 (TOC·요약·frontmatter)
│   │   ├── query_parser.py         # arXiv ID/URL 파싱 및 정규화
│   │   ├── sections.py             # 섹션 필터링 (include/exclude 모드)
│   │   ├── schemas/                # Pydantic 데이터 모델
│   │   │   ├── __init__.py
│   │   │   ├── ingestion.py        # IngestionResult 스키마
│   │   │   ├── query.py            # ArxivQuery 스키마
│   │   │   └── sections.py         # SectionNode 스키마
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logging_config.py   # loguru 기반 로깅 설정
│   │
│   ├── server/                     # FastAPI 웹 서버 패키지
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── main.py                 # FastAPI 앱 초기화 & 라우터 등록
│   │   ├── models.py               # API 요청/응답 Pydantic 모델
│   │   ├── query_processor.py      # 쿼리 처리 & digest 파일 저장
│   │   ├── routers_utils.py        # 공통 라우터 유틸리티
│   │   ├── server_config.py        # 서버 설정 (템플릿 경로, 예시 목록 등)
│   │   ├── form_types.py           # FastAPI Form 타입 별칭 정의
│   │   ├── routers/                # API 엔드포인트 라우터
│   │   │   ├── __init__.py
│   │   │   ├── dynamic.py          # 동적 URL 라우터 (arXiv URL 직접 접근)
│   │   │   ├── index.py            # 홈 페이지 (GET /)
│   │   │   ├── ingest.py           # POST /api/ingest, GET /api/{user}/{repo}
│   │   │   └── markdown_api.py     # GET /api/json, GET /api/markdown
│   │   └── templates/              # Jinja2 HTML 템플릿
│   │       ├── arxiv.jinja         # 메인 페이지 템플릿
│   │       ├── base_arxiv.jinja    # 기본 레이아웃 템플릿
│   │       └── components/         # 재사용 가능한 UI 컴포넌트
│   │
│   └── static/                     # 정적 웹 파일 (JS, 이미지, 아이콘 등)
│       ├── js/                     # 클라이언트 측 JavaScript
│       ├── svg/                    # SVG 아이콘
│       ├── favicons/               # 파비콘
│       ├── llms.txt                # LLM 크롤러 안내 파일
│       └── robots.txt              # 검색엔진 크롤러 안내 파일
│
├── tests/                          # 단위 테스트
│   ├── conftest.py                 # pytest 공통 설정 (sys.path 조정)
│   ├── test_html_parser.py         # HTML 파서 테스트
│   ├── test_markdown.py            # 마크다운 변환 테스트
│   ├── test_output_formatter.py    # 출력 포매터 테스트
│   └── test_query_parser.py        # 쿼리 파서 테스트
│
├── assets/                         # README 등 문서용 이미지
├── .github/                        # GitHub Actions 워크플로우
├── Dockerfile                      # Docker 이미지 빌드 정의
├── docker-compose.yml              # 로컬 Docker Compose 설정
├── nginx.conf                      # Nginx 리버스 프록시 설정
├── arxiv2md.service                # systemd 서비스 유닛 파일
├── deploy.sh                       # 운영 배포 스크립트
├── update.sh                       # 운영 업데이트 스크립트
├── pyproject.toml                  # Python 패키지 & 프로젝트 메타데이터
├── requirements.txt                # pip 의존성 목록
├── uv.lock                         # uv 패키지 매니저 락 파일
├── env.example                     # 환경변수 예시 파일
├── README.md                       # 프로젝트 소개 및 사용법
└── LICENSE                         # MIT 라이선스
```

---

## 핵심 라이브러리 (`src/arxiv2md/`)

`pip install arxiv2markdown`으로 배포되는 패키지의 실제 구현체입니다. 웹 서버 없이 독립적으로 사용할 수 있습니다.

### `__init__.py` — 공개 API

외부에 노출되는 두 함수를 정의합니다:

- `ingest_paper(arxiv_id, ...)` — 비동기(async) 버전
- `ingest_paper_sync(arxiv_id, ...)` — 동기 버전 (내부적으로 `asyncio.run()` 사용)

두 함수 모두 `IngestionResult`를 반환하며, `result.content`로 마크다운 본문에 접근합니다.

### `__main__.py` — CLI 진입점

`arxiv2md` 커맨드를 실행하면 이 모듈이 호출됩니다. `argparse`로 커맨드라인 인자를 처리하고 내부적으로 `ingestion.ingest_paper()`를 호출합니다.

주요 옵션:
- `--remove-refs` / `--remove-toc` / `--remove-inline-citations` — 불필요한 내용 제거
- `--sections` / `--section-filter-mode` — 특정 섹션만 포함하거나 제외
- `--frontmatter` — YAML 메타데이터 헤더 추가
- `-o` / `--output` — 출력 파일 지정 (`-`이면 표준출력)

### `config.py` — 설정값

환경변수를 읽어 설정값을 정의합니다. `.env` 파일이나 시스템 환경변수로 동작을 제어할 수 있습니다.

| 환경변수 | 기본값 | 설명 |
|---------|--------|------|
| `ARXIV2MD_CACHE_PATH` | `.arxiv2md_cache` | 캐시 저장 경로 |
| `ARXIV2MD_CACHE_TTL_SECONDS` | `86400` (24시간) | 캐시 유효 기간 |
| `ARXIV2MD_CACHE_MAX_SIZE_MB` | `500` | 캐시 최대 크기 |
| `ARXIV2MD_FETCH_TIMEOUT_S` | `10.0` | HTTP 요청 타임아웃 |
| `ARXIV2MD_FETCH_MAX_RETRIES` | `2` | 최대 재시도 횟수 |

### `query_parser.py` — 쿼리 파싱

사용자가 입력한 arXiv ID 또는 URL을 `ArxivQuery` 객체로 변환합니다.

지원하는 입력 형식:
- `2501.11120` (ID만)
- `2501.11120v1` (버전 포함)
- `https://arxiv.org/abs/2501.11120` (전체 URL)
- `https://arxiv.org/pdf/2501.11120v2.pdf` (PDF URL)
- `cs/9901001v2` (구형 ID 형식)

### `fetch.py` — HTML 다운로드

arXiv HTML 페이지를 가져옵니다. 기본적으로 `arxiv.org/html/{id}`를 시도하고, 404가 반환되면 `ar5iv.labs.arxiv.org/html/{id}`로 폴백합니다.

- **캐싱**: 한 번 다운로드한 HTML은 로컬 파일로 캐시되어 재사용됩니다.
- **재시도**: 429/5xx 오류 시 지수 백오프(exponential backoff)로 자동 재시도합니다.

### `html_parser.py` — HTML 파싱

BeautifulSoup으로 arXiv HTML을 파싱하여 구조화된 데이터를 추출합니다:

- **제목** (`ltx_title_document` 클래스)
- **저자** (`ltx_authors` → `ltx_text ltx_font_bold` 스팬)
- **초록** (`ltx_abstract` 클래스)
- **섹션 트리** (h1~h6 태그 기반, `SectionNode` 트리 구조)

각 `SectionNode`는 제목, 레벨, HTML 내용, 하위 섹션(children) 목록을 가집니다.

### `sections.py` — 섹션 필터링

`filter_sections()` 함수로 섹션 트리를 필터링합니다:

- **include 모드**: 지정한 섹션만 포함
- **exclude 모드**: 지정한 섹션을 제외 (기본값)

섹션 제목 비교 시 대소문자, 앞의 번호(예: "1.", "2.1")는 무시합니다.

### `markdown.py` — 마크다운 변환

HTML 섹션을 마크다운으로 변환하는 핵심 직렬화기입니다:

- **수식**: MathML의 `<annotation encoding="application/x-tex">` 태그에서 LaTeX 소스를 추출하여 `$...$` 형식으로 변환
- **표**: `ltx_tabular` 클래스 표 → GFM(GitHub Flavored Markdown) 표
- **수식 블록**: `ltx_equationgroup` 등 → `$$...$$` 형식
- **인용 링크**: `remove_inline_citations=True`이면 인용 링크 제거, `False`이면 텍스트만 유지
- **이미지**: 상대 경로를 절대 URL로 변환

### `ingestion.py` — 수집 파이프라인

위의 모든 모듈을 조율하는 중심 함수 `ingest_paper()`를 포함합니다. 호출 순서:

1. `fetch.fetch_arxiv_html()` — HTML 다운로드
2. `html_parser.parse_arxiv_html()` — HTML 파싱
3. `sections.filter_sections()` — 섹션 필터링
4. `markdown.convert_fragment_to_markdown()` — 마크다운 변환
5. `output_formatter.format_paper()` — 최종 결과물 생성

### `output_formatter.py` — 출력 포매터

파싱된 섹션들을 하나의 마크다운 문서로 조합합니다:

- **목차(TOC)** 생성
- **요약(summary)** — 제목, arXiv ID, 저자, 섹션 수, 토큰 추정치
- **YAML frontmatter** — `include_frontmatter=True`일 때 문서 상단에 메타데이터 추가
- **토큰 추정**: `tiktoken` 라이브러리로 GPT 토큰 수 추정

### `schemas/` — 데이터 모델

| 모델 | 파일 | 설명 |
|------|------|------|
| `ArxivQuery` | `query.py` | 파싱된 입력 (arXiv ID, 버전, URL 등) |
| `SectionNode` | `sections.py` | 섹션 트리의 노드 (제목, 레벨, HTML, 자식) |
| `IngestionResult` | `ingestion.py` | 최종 결과 (content, summary, sections_tree, frontmatter) |

### `utils/logging_config.py` — 로깅 설정

`loguru` 기반 로깅을 설정합니다:
- **개발 환경**: 색상 있는 사람 읽기 쉬운 형식 (stderr 출력)
- **Kubernetes/운영 환경**: JSON 구조화 로그 (stdout 출력)

환경변수 `LOG_FORMAT` (`human`/`json`)과 `LOG_LEVEL`로 제어합니다.

---

## 웹 서버 (`src/server/`)

FastAPI 기반 웹 애플리케이션입니다. `pip install arxiv2markdown[server]`로 설치합니다.

### `main.py` — FastAPI 앱 진입점

- FastAPI 앱 인스턴스 생성 및 설정
- 정적 파일 마운트 (`/static`)
- slowapi 기반 rate limiter 등록 (IP당 30req/min)
- 공통 엔드포인트: `/health`, `/robots.txt`, `/llms.txt`, `/api` (OpenAPI 스키마)
- 각 라우터 등록: `index`, `ingest`, `markdown_api`, `dynamic`

### `routers/` — API 라우터

| 파일 | 엔드포인트 | 설명 |
|------|-----------|------|
| `index.py` | `GET /` | 웹 앱 홈 페이지 렌더링 |
| `ingest.py` | `POST /api/ingest` | 웹 앱 폼 제출 처리 (JSON 응답) |
| `ingest.py` | `GET /api/{user}/{repo}` | 레거시 GET 엔드포인트 |
| `ingest.py` | `GET /api/download/file/{id}` | digest 파일 다운로드 |
| `markdown_api.py` | `GET /api/json` | arXiv → JSON (마크다운 + 메타데이터) |
| `markdown_api.py` | `GET /api/markdown` | arXiv → 마크다운 텍스트 (rate limited) |
| `dynamic.py` | `GET /{arxiv_path:path}` | arXiv URL 직접 접근 (예: `/abs/2501.11120`) |

### `models.py` — API 모델

| 모델 | 설명 |
|------|------|
| `IngestRequest` | `POST /api/ingest` 요청 본문 |
| `IngestSuccessResponse` | 성공 응답 |
| `IngestErrorResponse` | 오류 응답 |
| `MarkdownJsonResponse` | `/api/json` 응답 (간략화) |
| `SectionFilterMode` | 섹션 필터 모드 열거형 (`include`/`exclude`) |

### `query_processor.py` — 쿼리 처리

웹 서버 요청을 처리하고 핵심 라이브러리의 `ingest_paper()`를 호출합니다. 결과물(digest)을 로컬 파일로 저장하고 다운로드 URL을 반환합니다.

### `server_config.py` — 서버 설정

- Jinja2 템플릿 디렉토리 설정
- 예시 arXiv 논문 목록 (`EXAMPLE_REPOS`)
- 앱 버전 정보 (환경변수 `APP_VERSION`에서 읽음)

---

## 정적 파일 (`src/static/`)

웹 앱의 정적 에셋입니다. FastAPI의 `StaticFiles`로 `/static` 경로에 서빙됩니다.

| 경로 | 내용 |
|------|------|
| `js/` | 클라이언트 측 JavaScript (섹션 선택, 슬라이더 등) |
| `svg/` | UI에서 사용하는 SVG 아이콘 |
| `favicons/` | 파비콘 파일 |
| `llms.txt` | LLM 크롤러에 사이트 정보 제공 |
| `robots.txt` | 검색엔진 크롤러 안내 |

---

## 테스트 (`tests/`)

`pytest` 기반의 단위 테스트입니다. `conftest.py`가 `src/` 디렉토리를 Python 경로에 추가합니다.

| 파일 | 테스트 대상 | 내용 |
|------|------------|------|
| `test_html_parser.py` | `html_parser.py` | 제목·저자·초록·섹션 추출 검증 |
| `test_markdown.py` | `markdown.py` | 수식·표·인용 마크다운 변환 검증 |
| `test_output_formatter.py` | `output_formatter.py` | frontmatter·TOC·요약 생성 검증 |
| `test_query_parser.py` | `query_parser.py` | 다양한 arXiv ID/URL 파싱 검증 |

---

## 배포 및 인프라 파일

| 파일 | 역할 |
|------|------|
| `Dockerfile` | Python 앱을 Docker 이미지로 패키징 |
| `docker-compose.yml` | 로컬 개발용 Docker Compose (앱 + nginx) |
| `nginx.conf` | Nginx 리버스 프록시 설정 (HTTPS 종단, 정적 파일 서빙) |
| `arxiv2md.service` | systemd 유닛 파일 (Linux 서비스로 등록) |
| `deploy.sh` | 운영 서버 최초 배포 스크립트 |
| `update.sh` | 운영 서버 업데이트 스크립트 |
| `pyproject.toml` | 패키지 메타데이터, 의존성, pytest/setuptools 설정 |
| `uv.lock` | `uv` 패키지 매니저의 재현 가능한 의존성 락 파일 |
| `env.example` | 환경변수 예시 (`.env` 파일 생성 시 참고) |

---

## 데이터 흐름 다이어그램

아래는 arXiv 논문이 마크다운으로 변환되는 전체 과정입니다.

```
┌────────────────────────────────────────────────────────────┐
│                    사용자 입력                               │
│  CLI: arxiv2md 2501.11120v1                                 │
│  API: GET /api/markdown?url=2501.11120                      │
│  Lib: ingest_paper("2501.11120v1")                          │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│  query_parser.py                                          │
│  • arXiv ID / URL 파싱 및 정규화                           │
│  • ArxivQuery 생성 (arxiv_id, version, html_url, ...)     │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│  fetch.py                                                 │
│  • 로컬 캐시 확인 (신선도 검사)                             │
│  • arxiv.org/html/{id} 에서 HTML 다운로드                  │
│  • 404 시 ar5iv.labs.arxiv.org 로 폴백                     │
│  • 429/5xx 시 지수 백오프 재시도                            │
│  • 캐시에 저장                                             │
└──────────────────────────┬───────────────────────────────┘
                           │ HTML 텍스트
                           ▼
┌──────────────────────────────────────────────────────────┐
│  html_parser.py                                           │
│  • BeautifulSoup으로 HTML 파싱                             │
│  • 제목, 저자, 초록 추출                                   │
│  • h1~h6 태그 기반 섹션 트리(SectionNode) 구축             │
└──────────────────────────┬───────────────────────────────┘
                           │ ParsedArxivHtml
                           ▼
┌──────────────────────────────────────────────────────────┐
│  sections.py                                              │
│  • include/exclude 모드로 섹션 필터링                       │
│  • 참고문헌 섹션 자동 제거 (remove_refs=True 시)            │
└──────────────────────────┬───────────────────────────────┘
                           │ 필터링된 SectionNode 목록
                           ▼
┌──────────────────────────────────────────────────────────┐
│  markdown.py                                              │
│  • 각 섹션의 HTML → 마크다운 변환                           │
│  • MathML → LaTeX ($...$, $$...$$)                        │
│  • ltx_tabular 표 → GFM 마크다운 표                        │
│  • 인용 링크 처리 (제거 또는 텍스트만 유지)                  │
│  • 이미지 상대 경로 → 절대 URL 변환                         │
└──────────────────────────┬───────────────────────────────┘
                           │ SectionNode.markdown 채워짐
                           ▼
┌──────────────────────────────────────────────────────────┐
│  output_formatter.py                                      │
│  • 섹션들을 하나의 마크다운 문서로 조합                       │
│  • 목차(TOC) 생성 (include_toc=True 시)                    │
│  • 요약(summary) 생성 (제목, 저자, 토큰 수 등)               │
│  • YAML frontmatter 생성 (include_frontmatter=True 시)     │
└──────────────────────────┬───────────────────────────────┘
                           │ IngestionResult
                           ▼
┌──────────────────────────────────────────────────────────┐
│                      최종 출력                             │
│  result.content      — 마크다운 본문                       │
│  result.summary      — 요약 정보 (제목, 저자, 토큰 수 등)   │
│  result.sections_tree — 섹션 목록 텍스트                   │
│  result.frontmatter  — YAML 헤더 (선택적)                  │
└──────────────────────────────────────────────────────────┘
```

### 웹 서버 요청 처리 흐름

```
클라이언트 요청
    │
    ▼
main.py (FastAPI 앱)
    │  rate limit 검사 (slowapi)
    ▼
routers/
    ├── markdown_api.py  →  /api/json, /api/markdown
    ├── ingest.py        →  /api/ingest (웹 폼)
    ├── dynamic.py       →  /{arxiv_path} (URL 직접 접근)
    └── index.py         →  / (홈 페이지)
         │
         ▼
    query_processor.py
         │  parse_arxiv_input() 호출
         │  ingest_paper() 호출 (핵심 파이프라인)
         │  digest 파일 로컬 저장
         ▼
    JSON / 마크다운 / HTML 응답 반환
```

---

## 코드 수정 후 테스트 방법

### 1. 환경 설정

**개발 의존성 설치** (테스트 실행에 필요):

```bash
# 핵심 + 개발 의존성 설치
pip install -e .[dev]

# 서버 기능까지 포함하여 풀 개발 환경 설정
pip install -e .[server,dev]
```

또는 `uv`를 사용하는 경우:

```bash
uv sync --all-extras
```

### 2. 테스트 실행

```bash
# 전체 테스트 실행
pytest tests/

# 자세한 출력과 함께 실행
pytest tests/ -v

# 특정 테스트 파일만 실행
pytest tests/test_html_parser.py
pytest tests/test_markdown.py
pytest tests/test_output_formatter.py
pytest tests/test_query_parser.py

# 특정 테스트 함수만 실행
pytest tests/test_query_parser.py::test_parse_arxiv_inputs

# 키워드로 테스트 필터링
pytest tests/ -k "markdown"
```

### 3. 로컬 웹 서버 실행

```bash
pip install -e .[server]
uvicorn server.main:app --reload --app-dir src
# → http://localhost:8000 에서 확인
```

### 4. CLI 동작 확인

```bash
# 기본 사용법 (실제 논문 다운로드)
arxiv2md 2501.11120v1 -o /tmp/test.md

# 출력을 표준출력으로 확인
arxiv2md 2501.11120v1 -o -

# 섹션 필터링 테스트
arxiv2md 2501.11120v1 --section-filter-mode include --sections "Abstract,Introduction" -o -
```

### 5. 수정 영역별 테스트 가이드

| 수정 영역 | 관련 테스트 파일 | 주요 확인 사항 |
|-----------|----------------|---------------|
| `query_parser.py` | `test_query_parser.py` | 다양한 URL/ID 형식 파싱 정확도 |
| `html_parser.py` | `test_html_parser.py` | 제목·저자·섹션 추출 정확도 |
| `markdown.py` | `test_markdown.py` | 수식·표·링크 변환 정확도 |
| `output_formatter.py` | `test_output_formatter.py` | frontmatter·TOC·요약 형식 |
| `sections.py` | `test_query_parser.py`에 일부 포함 | include/exclude 필터링 동작 |
| `fetch.py` | (단위 테스트 없음, mock 권장) | 재시도 로직, 캐시 동작 |
| `server/` | (단위 테스트 없음, 수동 확인) | 로컬 서버 기동 후 확인 |

### 6. 새 테스트 추가 방법

기존 테스트 스타일에 맞게 `tests/` 디렉토리에 파일을 추가합니다.

```python
# tests/test_새기능.py 예시
from __future__ import annotations

from arxiv2md.새모듈 import 새함수


def test_새기능_설명() -> None:
    # Arrange
    입력값 = "..."

    # Act
    결과 = 새함수(입력값)

    # Assert
    assert 결과 == 예상값
```

비동기 함수 테스트:

```python
import pytest

@pytest.mark.asyncio
async def test_비동기_함수() -> None:
    결과 = await 비동기함수(입력값)
    assert 결과 == 예상값
```

> `pyproject.toml`에 `asyncio_mode = "auto"`가 설정되어 있어 `@pytest.mark.asyncio` 데코레이터 없이도 `async def test_*` 함수가 자동으로 실행됩니다.

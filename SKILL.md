---
name: threads-post
description: >
  Meta Threads 소셜 미디어에 글을 게시합니다. 사용자가 "Threads에 올려줘",
  "Threads 포스팅해줘", "쓰레드에 글 써줘", "post to Threads", "share on Threads"
  같은 요청을 할 때 반드시 이 스킬을 사용하세요. 텍스트 게시, 답글 달기를 지원합니다.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - THREADS_ACCESS_TOKEN
        - THREADS_USER_ID
      bins:
        - python3
    primaryEnv: THREADS_ACCESS_TOKEN
---

# Threads Post Skill

이 스킬은 Meta Threads API를 통해 텍스트 게시물을 올립니다.

## 환경 변수 설정

처음 사용하기 전에 `~/.openclaw/.env` 파일에 다음을 추가해야 합니다:

```
THREADS_ACCESS_TOKEN=your_long_lived_access_token_here
THREADS_USER_ID=your_numeric_user_id_here
```

액세스 토큰 발급 방법은 아래 "초기 설정" 섹션을 참고하세요.

---

## 사용 방법

### 기본 게시 (텍스트)

사용자가 Threads에 글을 올리라고 하면 `{skill_dir}/scripts/post.py`를 실행하세요:

```bash
python3 {skill_dir}/scripts/post.py "게시할 내용"
```

### 답글 달기

특정 게시물에 답글을 달 경우:

```bash
python3 {skill_dir}/scripts/post.py --reply-to <post_id> "답글 내용"
```

### 긴 텍스트 (따옴표 충돌 주의)

내용에 따옴표나 특수문자가 포함된 경우, Python으로 직접 호출하세요:

```python
import subprocess, os
result = subprocess.run(
    ["python3", "{skill_dir}/scripts/post.py"],
    input="게시할 내용을 여기에",
    capture_output=True, text=True,
    env={**os.environ}
)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
```

---

## 성공 응답 예시

```
📝 게시물 준비 중...
🚀 Threads에 게시 중...
✅ 게시 완료!
   Post ID: 18047234567890123
   내용: 오늘 날씨가 정말 좋네요! ☀️
```

---

## 오류 대응

| 오류 메시지 | 원인 | 해결 방법 |
|---|---|---|
| `THREADS_ACCESS_TOKEN 환경 변수가 설정되지 않았습니다` | .env 미설정 | `~/.openclaw/.env`에 토큰 추가 |
| `API 오류 (코드 190)` | 토큰 만료 | 아래 "토큰 갱신" 참고 |
| `API 오류 (코드 32)` | 권한 없음 | Meta 앱에서 threads_content_publish 권한 확인 |
| 텍스트 500자 초과 경고 | Threads 글자 제한 | 내용을 500자 이하로 줄이세요 |

---

## 초기 설정 — 액세스 토큰 발급

### 1. Meta 개발자 앱 설정

1. [Meta for Developers](https://developers.facebook.com) 접속
2. 앱 생성 → "Threads" 제품 추가
3. Threads API 사용 권한 신청:
   - `threads_basic`
   - `threads_content_publish`

### 2. 단기 토큰 발급

```
https://threads.net/oauth/authorize
  ?client_id={app_id}
  &redirect_uri={redirect_uri}
  &scope=threads_basic,threads_content_publish
  &response_type=code
```

인증 후 받은 `code`로 단기 토큰을 교환:

```bash
curl -X POST "https://graph.threads.net/oauth/access_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=YOUR_REDIRECT_URI" \
  -d "code=YOUR_AUTH_CODE"
```

### 3. 장기 토큰으로 교환 (60일 유효)

```bash
curl "https://graph.threads.net/access_token
  ?grant_type=th_exchange_token
  &client_secret=YOUR_APP_SECRET
  &access_token=SHORT_LIVED_TOKEN"
```

### 4. User ID 확인

```bash
curl "https://graph.threads.net/v1.0/me?access_token=YOUR_TOKEN"
```

응답의 `id` 값이 `THREADS_USER_ID`입니다.

---

## 토큰 갱신 (만료 전 60일마다)

장기 토큰은 만료 전에 갱신해야 합니다:

```bash
curl "https://graph.threads.net/refresh_access_token
  ?grant_type=th_refresh_token
  &access_token=YOUR_LONG_LIVED_TOKEN"
```

새 토큰을 `~/.openclaw/.env`의 `THREADS_ACCESS_TOKEN`에 업데이트하세요.

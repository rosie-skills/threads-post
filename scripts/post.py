#!/usr/bin/env python3
"""
Threads Post Script
Meta Threads API를 통해 텍스트 게시물을 올립니다.

사용법:
  python3 post.py "게시할 내용"
  python3 post.py --text "게시할 내용"
  python3 post.py --reply-to <post_id> "답글 내용"

환경 변수:
  THREADS_ACCESS_TOKEN  - Meta 개발자 포털에서 발급받은 액세스 토큰
  THREADS_USER_ID       - Threads 계정의 User ID (숫자)
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "https://graph.threads.net/v1.0"


def get_credentials():
    token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("THREADS_USER_ID")

    if not token:
        print("❌ 오류: THREADS_ACCESS_TOKEN 환경 변수가 설정되지 않았습니다.")
        print("   ~/.openclaw/.env 파일에 THREADS_ACCESS_TOKEN=your_token 을 추가하세요.")
        sys.exit(1)

    if not user_id:
        print("❌ 오류: THREADS_USER_ID 환경 변수가 설정되지 않았습니다.")
        print("   ~/.openclaw/.env 파일에 THREADS_USER_ID=your_user_id 를 추가하세요.")
        sys.exit(1)

    return token, user_id


def api_post(url, params):
    """POST 요청을 보내고 JSON 응답을 반환합니다."""
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_json = json.loads(error_body)
            msg = error_json.get("error", {}).get("message", error_body)
            code = error_json.get("error", {}).get("code", e.code)
            print(f"❌ API 오류 (코드 {code}): {msg}")
        except Exception:
            print(f"❌ HTTP 오류 {e.code}: {error_body}")
        sys.exit(1)


def create_container(user_id, token, text, reply_to_id=None):
    """1단계: 미디어 컨테이너(초안) 생성"""
    url = f"{BASE_URL}/{user_id}/threads"
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": token,
    }
    if reply_to_id:
        params["reply_to_id"] = reply_to_id

    result = api_post(url, params)
    return result.get("id")


def publish_container(user_id, token, creation_id):
    """2단계: 컨테이너를 실제로 게시"""
    url = f"{BASE_URL}/{user_id}/threads_publish"
    params = {
        "creation_id": creation_id,
        "access_token": token,
    }
    result = api_post(url, params)
    return result.get("id")


def post_to_threads(text, reply_to_id=None):
    token, user_id = get_credentials()

    print(f"📝 게시물 준비 중...")
    creation_id = create_container(user_id, token, text, reply_to_id)

    if not creation_id:
        print("❌ 컨테이너 생성에 실패했습니다.")
        sys.exit(1)

    print(f"🚀 Threads에 게시 중...")
    post_id = publish_container(user_id, token, creation_id)

    if post_id:
        print(f"✅ 게시 완료!")
        print(f"   Post ID: {post_id}")
        print(f"   내용: {text[:80]}{'...' if len(text) > 80 else ''}")
        return post_id
    else:
        print("❌ 게시에 실패했습니다.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Meta Threads에 글 게시")
    parser.add_argument("text", nargs="?", help="게시할 텍스트 내용")
    parser.add_argument("--text", "-t", dest="text_flag", help="게시할 텍스트 (플래그 방식)")
    parser.add_argument("--reply-to", "-r", help="답글 달 게시물의 ID")

    args = parser.parse_args()

    text = args.text or args.text_flag

    if not text:
        # stdin에서 읽기 (파이프 입력 지원)
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()
        else:
            print("❌ 게시할 내용을 입력해주세요.")
            print("   사용법: python3 post.py '게시할 내용'")
            sys.exit(1)

    if len(text) > 500:
        print(f"⚠️  경고: 텍스트가 500자를 초과합니다 ({len(text)}자). Threads 글자 제한에 걸릴 수 있습니다.")

    post_to_threads(text, reply_to_id=args.reply_to)


if __name__ == "__main__":
    main()

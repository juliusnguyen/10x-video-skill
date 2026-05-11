     1|#!/usr/bin/env python3
     2|"""YouTube upload script with scheduler, channel rules, dry-run, and upload history.
     3|Based on Flow Kit workflow patterns.
     4|"""
     5|import subprocess
     6|import sys
     7|import os
     8|import json
     9|import time
    10|from datetime import datetime, timedelta, timezone
    11|from pathlib import Path
    12|
    13|from google.oauth2.credentials import Credentials
    14|from googleapiclient.discovery import build
    15|from googleapiclient.http import MediaFileUpload
    16|from google.auth.transport.requests import Request as AuthRequest
    17|
    18|# OAuth2 credentials
    19|CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "YOUR_CLIENT_ID.apps.googleusercontent.com")
    20|CLIENT_SECRET=os.env...ET", "YOUR_CLIENT_SECRET_HERE")
    21|REFRESH_TOKEN=os.env...EN", "YOUR_REFRESH_TOKEN_HERE")
    22|
    23|SCOPES = [
    24|    "https://www.googleapis.com/auth/youtube.upload",
    25|    "https://www.googleapis.com/auth/youtube.force-ssl",
    26|    "https://www.googleapis.com/auth/youtube",
    27|]
    28|
    29|PROJECT_DIR = Path(__file__).parent
    30|CHANNELS_DIR = PROJECT_DIR / "youtube" / "channels"
    31|
    32|
    33|def get_credentials():
    34|    """Get OAuth2 credentials from refresh token."""
    35|    creds = Credentials(
    36|        token=None,
    37|        refresh_token=REFRESH_TOKEN,
    38|        client_id=CLIENT_ID,
    39|        client_secret=CLIENT_SECRET,
    40|        token_uri="https://oauth2.googleapis.com/token",
    41|        scopes=SCOPES,
    42|    )
    43|    creds.refresh(AuthRequest())
    44|    return creds
    45|
    46|
    47|def load_channel_rules(channel_name="default"):
    48|    """Load channel rules JSON."""
    49|    rules_path = CHANNELS_DIR / channel_name / "channel_rules.json"
    50|    if rules_path.exists():
    51|        with open(rules_path) as f:
    52|            return json.load(f)
    53|    print(f"⚠️ No channel rules for '{channel_name}', using defaults")
    54|    return {
    55|        "name": channel_name,
    56|        "seo": {
    57|            "niche": "technology-ai",
    58|            "title_max_chars": 65,
    59|            "default_category": "28",
    60|            "default_tags": ["ai", "technology"],
    61|            "always_include_hashtags": ["#AI2026"],
    62|            "hashtag_language": "mixed_vi_en",
    63|            "ai_disclosure": "AI visuals generated with AI tools.",
    64|        },
    65|        "upload": {
    66|            "max_per_day": 3,
    67|            "optimal_times": ["07:00", "12:00", "17:00"],
    68|            "min_gap_hours": 5,
    69|            "avoid_hours": [0, 1, 2, 3, 4, 5],
    70|            "timezone": "Asia/Ho_Chi_Minh",
    71|            "default_privacy": "public",
    72|        },
    73|    }
    74|
    75|
    76|def load_upload_history(channel_name="default"):
    77|    """Load upload history from JSON file."""
    78|    history_path = CHANNELS_DIR / channel_name / "upload_history.json"
    79|    if history_path.exists():
    80|        with open(history_path) as f:
    81|            return json.load(f)
    82|    return {"uploads": []}
    83|
    84|
    85|def save_upload_history(channel_name, history):
    86|    """Save upload history to JSON file."""
    87|    history_path = CHANNELS_DIR / channel_name / "upload_history.json"
    88|    history_path.parent.mkdir(parents=True, exist_ok=True)
    89|    with open(history_path, "w") as f:
    90|        json.dump(history, f, ensure_ascii=False, indent=2)
    91|
    92|
    93|def get_tz(rules):
    94|    """Get timezone from channel rules."""
    95|    tz_name = rules.get("upload", {}).get("timezone", "UTC")
    96|    try:
    97|        from zoneinfo import ZoneInfo
    98|        return ZoneInfo(tz_name)
    99|    except Exception:
   100|        return timezone.utc
   101|
   102|
   103|def detect_video_type(video_path):
   104|    """Detect if a video is Short or Long form."""
   105|    result = subprocess.run(
   106|        ["ffprobe", "-v", "quiet", "-print_format", "json",
   107|         "-show_streams", "-show_format", video_path],
   108|        capture_output=True, text=True
   109|    )
   110|    info = json.loads(result.stdout)
   111|    duration = float(info.get("format", {}).get("duration", 0))
   112|    is_vertical = False
   113|    for stream in info.get("streams", []):
   114|        if stream.get("codec_type") == "video":
   115|            w = int(stream.get("width", 0))
   116|            h = int(stream.get("height", 0))
   117|            if h > w:
   118|                is_vertical = True
   119|                break
   120|    is_short = duration <= 61 and is_vertical
   121|    return ("short" if is_short else "long", "vertical" if is_vertical else "horizontal", duration)
   122|
   123|
   124|def validate_upload(channel_name, schedule_at, is_short, rules=None):
   125|    """Validate upload against channel rules."""
   126|    if not rules:
   127|        rules = load_channel_rules(channel_name)
   128|    upload_rules = rules.get("upload", {})
   129|    tz = get_tz(rules)
   130|    if schedule_at.tzinfo is None:
   131|        schedule_at = schedule_at.replace(tzinfo=timezone.utc)
   132|    local_time = schedule_at.astimezone(tz)
   133|    local_date = local_time.strftime("%Y-%m-%d")
   134|    local_hour = local_time.hour
   135|    history = load_upload_history(channel_name)
   136|    avoid = upload_rules.get("avoid_hours", [])
   137|    if local_hour in avoid:
   138|        next_ok = min(h for h in range(24) if h not in avoid and h > local_hour)
   139|        return False, f"Avoid hour {local_hour}:00 — next slot at {next_ok:02d}:00"
   140|    max_per_day = upload_rules.get("max_per_day", 3)
   141|    today_uploads = [u for u in history["uploads"]
   142|                     if u.get("scheduled_date") == local_date]
   143|    if len(today_uploads) >= max_per_day:
   144|        return False, f"Max {max_per_day} uploads/day reached for {local_date}"
   145|    min_gap = upload_rules.get("min_gap_hours", 4)
   146|    if history["uploads"]:
   147|        last_upload_time = datetime.fromisoformat(history["uploads"][-1]["scheduled_at"])
   148|        gap = (schedule_at - last_upload_time).total_seconds() / 3600
   149|        if gap < min_gap:
   150|            next_available = last_upload_time + timedelta(hours=min_gap)
   151|            return False, f"Min gap {min_gap}h not met — next at {next_available.strftime('%H:%M')}"
   152|    return True, "OK"
   153|
   154|
   155|def sanitize_description(desc):
   156|    """Remove characters that cause YouTube API 400 invalidDescription."""
   157|    import re
   158|    # Replace em dash with hyphen
   159|    desc = desc.replace('\u2014', '-').replace('\u2013', '-')
   160|    # Remove emoji compound characters (emoji with modifiers like ⏱️, 🔔)
   161|    # Keep basic emojis that YouTube accepts, remove ZWJ sequences and skin-tone modifiers
   162|    desc = re.sub(r'[\U0001F3FB-\U0001F3FF]', '', desc)  # skin tone modifiers
   163|    desc = re.sub(r'\ufe0f', '', desc)  # variation selectors (VS16)
   164|    # Replace problematic emoji with text equivalents
   165|    desc = desc.replace('\u23f1\ufe0f', 'Timer:')   # ⏱️
   166|    desc = desc.replace('\u23f1', 'Timer:')
   167|    desc = desc.replace('\U0001F4D6', '')             # 📖
   168|    desc = desc.replace('\U0001F514', '')              # 🔔
   169|    # Remove $, &, > which trigger invalidDescription
   170|    desc = desc.replace('$', '')
   171|    desc = desc.replace('&', 'va')  # Vietnamese "and"
   172|    desc = desc.replace('>', 'hon')  # Vietnamese "more than"
   173|    return desc.strip()
   174|
   175|
   176|def upload_video(video_path, title, description, tags, category_id="28",
   177|                 thumbnail_path=None, privacy="public", schedule_at=None,
   178|                 is_short=False, channel_name="default", dry_run=False):
   179|    """Upload a video to YouTube with SEO metadata."""
   180|    if not os.path.exists(video_path):
   181|        print(f"❌ Video file not found: {video_path}")
   182|        return None
   183|
   184|    # Sanitize description to avoid YouTube API 400 errors
   185|    description = sanitize_description(description)
   186|
   187|    print(f"\n🎬 Uploading: {title[:50]}...")
   188|    print(f"   File: {video_path} ({os.path.getsize(video_path)/1024/1024:.1f} MB)")
   189|
   190|    if dry_run:
   191|        print(f"\n📋 DRY RUN — would upload:")
   192|        print(f"   Title: {title}")
   193|        print(f"   Description: {description[:200]}...")
   194|        print(f"   Tags: {tags}")
   195|        print(f"   Privacy: {privacy}")
   196|        print(f"   Schedule: {schedule_at or 'now'}")
   197|        print(f"   Thumbnail: {thumbnail_path}")
   198|        print(f"   Is Short: {is_short}")
   199|        vtype, orient, dur = detect_video_type(video_path)
   200|        print(f"   Type: {vtype} ({orient}, {dur:.1f}s)")
   201|        return "DRY_RUN"
   202|    if schedule_at:
   203|        tz = get_tz(load_channel_rules(channel_name))
   204|        local_time = schedule_at.astimezone(tz) if schedule_at.tzinfo else schedule_at
   205|        print(f"   Schedule: {local_time.strftime('%Y-%m-%d %H:%M %Z')}")
   206|    creds = get_credentials()
   207|    youtube = build("youtube", "v3", credentials=creds)
   208|    if is_short and "#Shorts" not in title:
   209|        title = f"{title} #Shorts"
   210|    body = {
   211|        "snippet": {
   212|            "title": title,
   213|            "description": description,
   214|            "tags": tags,
   215|            "categoryId": category_id,
   216|            "defaultLanguage": "en",
   217|        },
   218|        "status": {
   219|            "privacyStatus": privacy if not schedule_at else "private",
   220|            "selfDeclaredMadeForKids": False,
   221|        },
   222|    }
   223|    if schedule_at:
   224|        body["status"]["publishAt"] = schedule_at.isoformat()
   225|        body["status"]["privacyStatus"] = "private"
   226|    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
   227|    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
   228|    print("   Uploading... ", end="", flush=True)
   229|    response = None
   230|    while response is None:
   231|        try:
   232|            status, response = request.next_chunk()
   233|            if status:
   234|                print(f"\r   Uploading... {int(status.progress()*100)}%", end="", flush=True)
   235|        except Exception as e:
   236|            print(f"\n   ⚠️ Retry: {e}")
   237|            time.sleep(5)
   238|            continue
   239|    video_id = response["id"]
   240|    print(f"\n   ✅ Uploaded! ID: {video_id}")
   241|    if thumbnail_path and os.path.exists(thumbnail_path):
   242|        print("   Thumbnail... ", end="", flush=True)
   243|        try:
   244|            youtube.thumbnails().set(
   245|                videoId=video_id,
   246|                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg", resumable=True)
   247|            ).execute()
   248|            print("✅")
   249|        except Exception as e:
   250|            print(f"⚠️ {e}")
   251|    print(f"   🔗 https://youtu.be/{video_id}")
   252|    history = load_upload_history(channel_name)
   253|    tz = get_tz(load_channel_rules(channel_name))
   254|    if schedule_at and schedule_at.tzinfo:
   255|        local_time = schedule_at.astimezone(tz)
   256|    else:
   257|        local_time = datetime.now(tz)
   258|    history["uploads"].append({
   259|        "video_id": video_id,
   260|        "title": title,
   261|        "video_path": video_path,
   262|        "type": "short" if is_short else "long",
   263|        "privacy": privacy,
   264|        "scheduled_at": (schedule_at or datetime.now(timezone.utc)).isoformat(),
   265|        "scheduled_date": local_time.strftime("%Y-%m-%d"),
   266|        "scheduled_time": local_time.strftime("%H:%M"),
   267|        "uploaded_at": datetime.now(timezone.utc).isoformat(),
   268|    })
   269|    save_upload_history(channel_name, history)
   270|    return video_id
   271|
   272|
   273|if __name__ == "__main__":
   274|    import argparse
   275|    parser = argparse.ArgumentParser(description="YouTube Upload with Scheduling")
   276|    parser.add_argument("video_number", nargs="?", help="Single video: 1..15")
   277|    parser.add_argument("--batch", action="store_true", help="Upload all videos in batch mode")
   278|    parser.add_argument("--channel", default="default", help="Channel name (default: default)")
   279|    parser.add_argument("--schedule", help="Schedule time (ISO format, e.g., 2026-04-17T12:00:00)")
   280|    parser.add_argument("--privacy", default="public", help="Privacy: public, unlisted, private")
   281|    parser.add_argument("--dry-run", action="store_true", help="Show schedule without uploading")
   282|
   283|    args = parser.parse_args()
   284|
   285|    VIDEOS = {
   286|        "1": {
   287|            "file": str(PROJECT_DIR / "output/video1_agent.mp4"),
   288|            "thumbnail": str(PROJECT_DIR / "thumbnails/video1_agent_thumbnail.jpg"),
   289|            "title": "Agentic AI — Không Chỉ Là Chatbot | AI Tự Hành Động 2026 #Shorts",
   290|            "description": "Agentic AI — Hệ thống AI không chỉ trả lời mà tự hành động.",
   291|            "tags": ["agentic ai", "ai agent", "ai 2026"],
   292|        },
   293|        "2": {
   294|            "file": str(PROJECT_DIR / "output/video2_opensource.mp4"),
   295|            "thumbnail": str(PROJECT_DIR / "thumbnails/video2_opensource_thumbnail.jpg"),
   296|            "title": "Dùng AI Miễn Phí 100% | OpenSource AI — Vũ Khí Bí Mật #Shorts",
   297|            "description": "Open source AI tools — Ollama, Dify và hơn nữa.",
   298|            "tags": ["open source ai", "ollama", "dify"],
   299|        },
   300|        "3": {
   301|            "file": str(PROJECT_DIR / "output/video3_agent_opensource.mp4"),
   302|            "thumbnail": str(PROJECT_DIR / "thumbnails/video3_agent_opensource_thumbnail.jpg"),
   303|            "title": "Agent + OpenSource = Siêu Năng Lực | AI Đỉnh Nhất 2026 #Shorts",
   304|            "description": "Agent + OpenSource kết hợp tạo sức mạnh AI vượt trội.",
   305|            "tags": ["agentic ai", "open source", "ollama"],
   306|        },
   307|        "4": {
   308|            "file": str(PROJECT_DIR / "output/video4_claude_code.mp4"),
   309|            "thumbnail": str(PROJECT_DIR / "thumbnails/video4_claude_code_thumbnail.jpg"),
   310|            "title": "Claude Code — Đồng Đội Không Ngủ | AI Coding Assistant #Shorts",
   311|            "description": "Claude Code — AI coding assistant không ngừng nghỉ.",
   312|            "tags": ["claude code", "ai coding", "anthropic"],
   313|        },
   314|        "5": {
   315|            "file": str(PROJECT_DIR / "output/video5_hermes.mp4"),
   316|            "thumbnail": str(PROJECT_DIR / "output/thumbnail.jpg"),
   317|            "title": "Hermes AI — AI Tự Hành Động: Research • Code • Automate #Shorts",
   318|            "description": """Hermes AI — Hệ thống tự hành động giúp research, viết code và tự động deploy.
   319|
   320|🔧 3 Năng Lực Siêu Việt:
   321|• Research — Tìm Google, đọc file, phân tích data
   322|• Code — Viết, sửa, test, deploy tự động
   323|• Automate — Cron job, schedule, chạy 24/7
   324|
   325|🧠 Persistent Memory — Nhớ bạn, nhớ project, nhớ preferences
   326|📅 Tự Lập Lịch — 5h sáng chấm market, 12h trưa tóm tắt email, 5h chiều upload YouTube
   327|🤖 Điều Phối 3 SubAgent — 1 câu lệnh → 3 agent chạy song song
   328|🔗 Kết Nối Trực Tiếp — Telegram, Discord, Home Assistant, GitHub
   329|
   330|Video này render bởi Hermes AI — TTS + Puppeteer + ffmpeg — TOÀN TỰ ĐỘNG
   331|
   332|⏱️ Chapters:
   333|0:00 — Bạn đang chat với AI
   334|0:04 — Hermes HÀNH ĐỘNG
   335|0:09 — 3 Năng Lực Siêu Việt
   336|0:15 — Persistent Memory
   337|0:20 — Tự Lập Lịch
   338|0:25 — Điều Phối SubAgent
   339|0:30 — Kết Nối Trực Tiếp
   340|0:34 — Video render bởi Hermes
   341|0:37 — 2026 rồi — Dùng Hermes AI!
   342|
   343|#HermesAI #AIAgent #Automation #AITựĐộng #AgenticAI #Shorts""",
   344|            "tags": ["hermes ai", "ai tự động", "automation", "ai agent", "agentic ai", "ai workflow", "tts vietnamese", "ai devops", "ai 2026"],
   345|        },
   346|        "6": {
   347|            "file": str(PROJECT_DIR / "output/video6_claude_tips.mp4"),
   348|            "thumbnail": str(PROJECT_DIR / "output/thumbnail.jpg"),
   349|            "title": "Claude Code — Khởi động 60s: Dev loop siêu nhanh | Tips cho người mới #Shorts",
   350|            "description": "Khởi động Dev loop siêu nhanh với Claude Code: plan → patch → test → commit. Mẹo cho người mới để giữ tốc độ mà đảm bảo chất lượng.",
   351|            "tags": ["claude code", "dev tips", "ai coding", "claude"],
   352|        },
   353|        "7": {
   354|            "file": str(PROJECT_DIR / "output/video7_planmode.mp4"),
   355|            "thumbnail": str(PROJECT_DIR / "thumbnails/video7_planmode_thumbnail.jpg"),
   356|            "title": "Claude Plan Mode — Đừng Edit ngay! Tách 2 bước, giảm bug cực mạnh #Shorts",
   357|            "description": """Claude Code Plan Mode — Mẹo quan trọng nhất cho người mới!
   358|
   359|Tránh over-edit bằng cách tách Plan và Edit thành 2 bước riêng biệt.
   360|
   361|1\uFE0F\u20E3 Bật Brain Mode (Plan Mode)
   362|• Phân tích bug, liệt kê file liên quan
   363|• Đánh giá rủi ro trước khi chạm code
   364|• Gợi ý cách test sau khi sửa
   365|
   366|2\uFE0F\u20E3 Duyệt rồi mới Edit
   367|• Plan → định hướng rõ ràng
   368|• Edit → thực thi chính xác
   369|• Tách 2 bước = giảm over-edit cực mạnh
   370|
   371|Bonus: Thấy reasoning trước diff → hiểu codebase nhanh hơn
   372|
   373|Plan để định hướng, Edit để thực thi. Nhớ nhé!
   374|
   375|⏱️ Chapters:
   376|00:00 — Đừng để Claude sửa code ngay!
   377|00:06 — Bật Brain Mode
   378|00:12 — Prompt mẫu Plan Mode
   379|00:18 — Duyệt rồi Edit
   380|00:23 — Bonus + CTA
   381|
   382|#ClaudeCode #PlanMode #AITips #AgenticAI #DevTips #AI2026 #CongNghe #Shorts""",
   383|            "tags": ["claude code", "plan mode", "ai tips", "dev tips", "claude", "agentic ai", "coding assistant", "ai 2026"],
   384|        },
   385|        "8": {
   386|            "file": str(PROJECT_DIR / "output/video8_claude-code.mp4"),
   387|            "thumbnail": str(PROJECT_DIR / "thumbnails/video8_claude-code_thumbnail.jpg"),
   388|            "title": "Claude Code — ĐỪNG BỎ LỠ! Trending tool dev phải biết (Dành cho người mới)",
   389|            "description": """Claude Code đang làm mưa làm gió trong cộng đồng dev — tự động viết code, sửa lỗi, tạo test, review PR. Nếu bạn chưa thử, bạn đang bỏ lỡ!
   390|
   391|3 tính năng chính:
   392|• Generate — Viết code từ yêu cầu ngay trong terminal
   393|• Test & Fix — Tạo test, sửa lỗi tự động
   394|• Review PR — Review code nhanh chóng
   395|
   396|Dành cho người mới: Claude Code dạy bạn từng bước, giải thích từng dòng code và cho ví dụ chạy được ngay.
   397|
   398|Cảnh báo: Luôn kiểm tra kết quả — AI có thể sai!
   399|
   400|Cài đặt: npm install -g @anthropic-ai/claude-code
   401|
   402|Timestamps:
   403|0:00 — Claude Code đang trending
   404|0:07 — Claude Code là gì?
   405|0:18 — 3 tính năng chính
   406|0:29 — Cho người mới bắt đầu
   407|0:42 — Lợi ích cụ thể
   408|0:53 — Cảnh báo quan trọng
   409|1:03 — Hướng dẫn bắt đầu
   410|1:12 — CTA: Đừng bỏ lỡ!
   411|
   412|#ClaudeCode #AITrending #DevTools #CodingAI #AITips #NguoiMoi #Dev2026 #Shorts""",
   413|            "tags": ["claude code", "ai trending", "dev tools", "coding ai", "ai tips", "claude", "anthropic", "terminal", "ai 2026", "nguoi moi", "coding assistant", "ai dev", "review code", "auto test"],
   414|        },
   415|        "9": {
   416|            "file": str(PROJECT_DIR / "output/video9_remotion.mp4"),
   417|            "thumbnail": str(PROJECT_DIR / "thumbnails/video9_remotion_thumbnail.jpg"),
   418|            "title": "Claude + Remotion — AI Tạo Video Animation Bằng Code! SHOCKING 2026",
   419|            "description": """Claude Code + Remotion = Combo sản xuất video animation hoàn toàn mới! AI viết code, Remotion renders — không cần After Effects.
   420|
   421|Remotion là framework React tạo video bằng code: Timeline, Composition, Spring Animation — từng frame được kiểm soát chính xác 100%.
   422|
   423|Claude Code viết component Remotion tự động từ prompt: useCurrentFrame, interpolate, spring config — tất cả chỉ bằng 1 câu lệnh.
   424|
   425|3 lợi ích chính:
   426|• Tốc độ — Từ ý tưởng đến video chỉ vài phút
   427|• Lặp lại — Đổi text, đổi data, video tự cập nhật
   428|• Chất lượng — Animation mượt như After Effects nhưng bằng code
   429|
   430|⚠️ Lưu ý: Claude có thể tạo animation bị giật — luôn preview trước khi render!
   431|
   432|Timestamps:
   433|0:00 — AI tạo video animation?
   434|0:09 — Remotion là gì?
   435|0:20 — Remotion Timeline
   436|0:33 — Claude + Remotion Flow
   437|0:46 — Spring + Interpolate
   438|0:58 — 3 Lợi ích chính
   439|1:08 — So sánh thời gian
   440|1:18 — Lưu ý quan trọng
   441|1:25 — CTA: Thử ngay!
   442|
   443|#Remotion #ClaudeCode #AIVideo #ReactAnimation #CodeVideo #RemotionJS #SpringAnimation #Interpolate #DevTools2026 #AITrending #CongNghe #Shorts""",
   444|            "tags": ["remotion", "claude code", "ai video", "react animation", "code video", "remotion js", "spring animation", "interpolate", "dev tools 2026", "ai trending", "video automation", "programmatic video", "after effects alternative", "ai 2026"],
   445|        },
   446|        "10": {
   447|            "file": str(PROJECT_DIR / "output/video10_kimi26.mp4"),
   448|            "thumbnail": str(PROJECT_DIR / "thumbnails/video10_kimi26.jpg"),
   449|            "title": "Kimi K2.6: Model Open-Source Dinh Vuot GPT-5",
   450|            "description": """Kimi K2.6 vua ra mat - model open-source dau tien thuc su de doa SOTA! Code 13 tieng lien tuc, 300 Agent Swarm, chi 0.95/1M tokens.\n\nTimestamps:\n00:00 - Kimi K2.6: Open-Source SOTA moi\n00:08 - Long-Horizon Coding: 13 tieng khong nghi\n00:25 - Agent Swarm: 300 sub-agents dong thoi\n00:42 - Proactive Agent: Chay 5 ngay autonomous\n00:55 - Benchmark so sanh GPT-5 va Claude 4.6\n01:10 - Gia ca va Architecture: 1T MoE, chi 0.95/1M\n01:22 - Endurance hon Power\n01:33 - Thu mien phi tai kimi.com\n\nKimi K2.6 (thang 4/2026) la model open-source MoE 1T/32B tu Moonshot AI, vuot GPT-5 va Claude Opus 4.6 o HLE, BrowseComp, SWE-Bench Pro. Agent Swarm scale ngang toi 300 sub-agents. Long-horizon coding chay lien tuc 13 gio refactor hon 4000 dong code.\n\nAI visuals generated with AI tools. Content based on real technology trends.\n\n#KimiK26 #OpenSourceAI #AIAgent #CongNghe #TechVietnam #MoonshotAI #LongHorizonCoding #AgentSwarm #AICoding #VLLM #MoE #VietnameseAI #MLops #AIModel2026 #LangChain #AICodingAgent""",
   451|            "tags": ["Kimi K2.6", "Moonshot AI", "open-source AI model", "AI coding agent", "long-horizon coding", "Agent Swarm", "SWE-Bench Pro", "HLE benchmark", "MoE 1T parameters", "AI model 2026", "Vietnamese AI video", "autonomous agent", "cheap AI API", "AI coding", "CongNghe"],
   452|        },
   453|        "12": {
   454|            "file": str(PROJECT_DIR / "output/video12_qwen36.mp4"),
   455|            "thumbnail": str(PROJECT_DIR / "thumbnails/video12_qwen36.jpg"),
   456|            "title": "Qwen 3.6-27B: 27 Ti Danh Bai 397 Ti | AI Trend 2026",
   457|            "description": """Qwen 3.6-27B - Model chi 27 ti parameters danh bai model 397 ti cua chinh Qwen! Day khong phai typo.
   458|
   459|27 ti dense model, deploy don gian. 397 ti MoE routing phuc tap, inference cham.
   460|Va 27 ti thang o moi benchmark coding: SWE-bench Verified 77.2%, Terminal-Bench 59.3%, SkillsBench 48.2.
   461|
   462|Tai sao can model khong lo khi model nho da du manh?
   463|
   464|Timestamps:
   465|00:00 - Qwen 3.6-27B: 27 ti danh bai 397 ti
   466|00:08 - Khong phai typo - 27 ti thang that
   467|00:20 - Benchmark coding vuot troi
   468|00:32 - Trend moi: Small Powerful Model
   469|00:42 - Single GPU deploy, nhanh 10x
   470|00:55 - Open-source mien phi
   471|01:07 - Performance per parameter la vua
   472|
   473|Qwen 3.6-27B (thang 4/2026) la model dense 27B tu Alibaba, vuot Qwen3-235B-A22B (397 ti MoE) o SWE-bench Verified, Terminal-Bench va SkillsBench. Deploy tren single GPU, inference nhanh hon 10x, chi phi giam cap so. Open-source, download chay local ngay.
   474|
   475|AI visuals generated with AI tools. Content based on real technology trends.
   476|
   477|#Qwen36 #Qwen27B #AI2026 #TechVietnam #CongNghe #SmallModel #OpenSourceAI #AlibabaAI #AICoding #SWEbench #TerminalBench #PerformancePerParameter #AIModel2026 #VLLM #DenseModel""",
   478|            "tags": ["Qwen 3.6", "Qwen 27B", "AI model 2026", "small model", "open-source AI", "dense model", "SWE-bench", "Terminal-Bench", "SkillsBench", "coding AI", "single GPU", "Alibaba AI", "tech vietnam", "AI coding benchmark", "performance per parameter"],
   479|        },
   480|        "17": {
   481|            "file": str(PROJECT_DIR / "output/video17_levelup.mp4"),
   482|            "thumbnail": str(PROJECT_DIR / "thumbnails/video17_levelup.jpg"),
   483|            "title": "Claude Code Level Up: 8 Thuat Thu Nang Cap AI Dev 2026",
   484|            "description": """Claude Code Level Up - 8 thuat thu nang cap cho developer su dung Claude Code hieu qua hon.
   485|
   486|Timestamps:
   487|00:00 - Claude Code Level Up: 8 thuat thu nang cap
   488|00:08 - Resume: Tiep tuc task dang lam giua chang
   489|00:16 - Hooks: Tu dong chay script truoc/sau command
   490|00:24 - Slash Commands: Shortcut cho workflow pho bien
   491|00:32 - MCP: Ket noi tool ben ngoai vao Claude Code
   492|00:40 - Memory: Luu context xuyen session
   493|00:48 - Multi-file Edit: Sua nhieu file cung luc
   494|00:56 - Permission: Quan ly quyen truy cap
   495|01:04 - Export: Xuat code, log, config nhanh chong
   496|
   497|Claude Code tu Anthropic la AI coding assistant manh me. 8 thuat thu nay giup ban tang hieu suat gap nhieu lan: resume session, tu dong hooks, slash commands, MCP integration, memory xuyen session, multi-file edit, permission va export.
   498|
   499|AI visuals generated with AI tools. Content based on real technology trends and documented capabilities.
   500|
   501|
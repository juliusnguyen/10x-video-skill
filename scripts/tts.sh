#!/bin/bash
# Generate TTS voiceovers via VieNeu Python SDK (Default) or iterA102 API
# Usage: ./tts.sh <video_number> [vieneu|minimax|elevenlabs]

set -e
cd "$(dirname "$0")/.."

# Video number (e.g., 2)
VNUM="${1:?Usage: tts.sh <number> [provider]}"
PROVIDER="${2:-vieneu}"

# Format number to 5 digits (e.g., 00002)
VPADDED=$(printf "%05d" "$VNUM")

# Find the video directory
VDIR=$(find production_videos -maxdepth 1 -name "${VPADDED}-*" -type d | head -n 1)

if [ -z "$VDIR" ]; then
    echo "❌ Video directory for ${VPADDED} not found!"
    exit 1
fi

# Get the full name from the directory (e.g., video2_5_SKILL_AI_HUU_ICH)
# We assume the HTML file exists in the directory and use its name
HTML_FILE=$(ls "$VDIR"/*.html 2>/dev/null | head -n 1)
if [ -z "$HTML_FILE" ]; then
    # Fallback: look for the txt file to determine name
    TXT_FILE=$(ls "$VDIR/voices"/*.txt 2>/dev/null | head -n 1)
    NAME=$(basename "$TXT_FILE" .txt)
else
    NAME=$(basename "$HTML_FILE" .html)
fi

OUTDIR="$VDIR/voices"
mkdir -p "$OUTDIR"

generate() {
    local text_file="$OUTDIR/${NAME}.txt"
    local out_file="$OUTDIR/${NAME}_podcast.mp3"

    if [ ! -f "$text_file" ]; then
        echo "  ❌ Text file not found: $text_file"
        return 1
    fi

    if [ "$PROVIDER" = "vieneu" ]; then
        echo "🎤 Generating $NAME with VieNeu (local) in $VDIR..."
        ./.venv/bin/python3 scripts/tts_vieneu.py --file "$text_file" --output "$out_file" --mode standard --emotion natural
    else
        # Legacy ITERA102 logic
        API_KEY="${ITERA102_API_KEY:-}"
        if [ -z "$API_KEY" ]; then echo "❌ Error: ITERA102_API_KEY not set"; exit 1; fi
        BASE_URL="${ITERA102_BASE_URL:-https://api.itera102.space/v1}"
        
        if [ "$PROVIDER" = "elevenlabs" ]; then VOICE_ID="4HGP1feHKTQ1DJst6Tk8"; MODEL_ID="eleven_turbo_v2_5"; P_PARAM="elevenlabs"; S_PARAM="1.0"
        elif [ "$PROVIDER" = "elevenlabs-female" ]; then VOICE_ID="KqbkuMVLVelcCTkFXEbE"; MODEL_ID="eleven_turbo_v2_5"; P_PARAM="elevenlabs"; S_PARAM="1.0"
        else VOICE_ID="362703657091273"; MODEL_ID="speech-2.8-turbo"; P_PARAM="minimax"; S_PARAM="1.1"; fi

        echo "🎤 Generating $NAME with $P_PARAM (Remote)..."
        local payload=$(python3 -c "import json; text=open('$text_file').read().strip(); print(json.dumps({'text': text, 'model_id': '$MODEL_ID', 'provider': '$P_PARAM', 'voice_settings': {'speed': $S_PARAM}}))")
        local response=$(curl -s -X POST "$BASE_URL/text-to-speech/$VOICE_ID" -H "xi-api-key: $API_KEY" -H "Content-Type: application/json" -d "$payload")
        local task_id=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id') or d.get('task_id') or d.get('history_id',''))" 2>/dev/null)
        if [ -z "$task_id" ]; then echo "  ❌ Error: $response"; return 1; fi
        for i in $(seq 1 60); do
            sleep 3
            local poll=$(curl -s "$BASE_URL/history/$task_id" -H "xi-api-key: $API_KEY")
            local status=$(echo "$poll" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status') or d.get('state',''))" 2>/dev/null)
            if [ "$status" = "completed" ] || [ "$status" = "done" ]; then
                local url=$(echo "$poll" | python3 -c "import json,sys; d=json.load(sys.stdin); r=d.get('result',{}); print(r.get('audio_url','') if isinstance(r,dict) else d.get('audio_url',''))" 2>/dev/null)
                if [ -n "$url" ]; then curl -sL -o "$out_file" "$url"; break; fi
            fi
            echo "  Polling... ($i)"
        done
    fi

    local dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$out_file" 2>/dev/null || echo "?")
    echo "  ✅ Done! Duration: ${dur}s"
}

generate

#!/bin/bash
# Generate TTS voiceovers via VieNeu Python SDK (Default) or iterA102 API
# Usage: ./tts.sh <video_number_name> [vieneu|minimax|elevenlabs|elevenlabs-female]
#   Example: ./tts.sh 1 vieneu
#
# Requires: 
#   - Python 3.12 + vieneu SDK (for local TTS)
#   - ITERA102_API_KEY (optional, only for minimax/elevenlabs)

set -e
cd "$(dirname "$0")"

PROVIDER="${2:-vieneu}"
OUTDIR="$(pwd)/../voices"
mkdir -p "$OUTDIR"

# Video registry - update this as needed
# Format: NUMBER:videoN_name
VIDEOS="1:video1_example 2:video2_example"

generate() {
    local num=$1
    local name=$2
    local prov=$3
    local text_file="$OUTDIR/${name}.txt"
    local out_file="$OUTDIR/${name}_podcast.mp3"

    if [ ! -f "$text_file" ]; then
        echo "  ❌ Text file not found: $text_file"
        return 1
    fi

    if [ "$prov" = "vieneu" ]; then
        echo "🎤 Generating $name with VieNeu (local)..."
        ../.venv/bin/python3 tts_vieneu.py --file "$text_file" --output "$out_file" --mode standard --emotion natural
    else
        # Legacy ITERA102 logic
        API_KEY="${ITERA102_API_KEY:-}"
        if [ -z "$API_KEY" ]; then
            echo "❌ Error: ITERA102_API_KEY not set for $prov"
            exit 1
        fi
        BASE_URL="${ITERA102_BASE_URL:-https://api.itera102.space/v1}"
        
        # Mapping for legacy voices
        if [ "$prov" = "elevenlabs" ]; then VOICE_ID="4HGP1feHKTQ1DJst6Tk8"; MODEL_ID="eleven_turbo_v2_5"; P_PARAM="elevenlabs"; S_PARAM="1.0"
        elif [ "$prov" = "elevenlabs-female" ]; then VOICE_ID="KqbkuMVLVelcCTkFXEbE"; MODEL_ID="eleven_turbo_v2_5"; P_PARAM="elevenlabs"; S_PARAM="1.0"
        else VOICE_ID="362703657091273"; MODEL_ID="speech-2.8-turbo"; P_PARAM="minimax"; S_PARAM="1.1"; fi

        echo "🎤 Generating $name with $P_PARAM (Remote)..."
        
        # Build JSON
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

if [ "$1" = "all" ]; then
    for entry in $VIDEOS; do num=${entry%%:*}; name=${entry##*:}; generate "$num" "$name" "$PROVIDER"; done
elif [ -n "$1" ]; then
    found=0
    for entry in $VIDEOS; do
        num=${entry%%:*}; name=${entry##*:};
        if [ "$num" = "$1" ]; then generate "$num" "$name" "$PROVIDER"; found=1; break; fi
    done
    if [ $found -eq 0 ]; then echo "❌ Video $1 not found in registry"; exit 1; fi
else
    echo "Usage: ./tts.sh <number> [vieneu|minimax|elevenlabs]"
    exit 1
fi

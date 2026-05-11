#!/bin/bash
# Generate TTS voiceovers via iterA102 API (MiniMax + ElevenLabs)
# Usage: ./tts.sh <video_number_name> [minimax|elevenlabs|elevenlabs-female]
#   Example: ./tts.sh 1 minimax
#           ./tts.sh all elevenlabs
#
# Requires: ITERA102_API_KEY environment variable
#   Example: ITERA102_API_KEY=YOUR_KEY ./tts.sh 1
#
# Providers:
#   minimax (default)    - speech-2.8-turbo, voice Podcast Host (Vietnamese)
#   elevenlabs           - eleven_turbo_v2_5, voice Ton (male, northern, warm)
#   elevenlabs-female    - eleven_turbo_v2_5, voice Man Nghi (female, southern, calm)

set -e
cd "$(dirname "$0")"

API_KEY="${ITERA102_API_KEY:-}"
if [ -z "$API_KEY" ]; then
    echo "❌ Error: ITERA102_API_KEY not set"
    echo "Usage: ITERA102_API_KEY=YOUR_KEY ./tts.sh <number> [minimax|elevenlabs|elevenlabs-female]"
    exit 1
fi

# Default provider: minimax
PROVIDER="${2:-minimax}"

BASE_URL="${ITERA102_BASE_URL:-https://api.itera102.space/v1}"
OUTDIR="$(pwd)/voices"
mkdir -p "$OUTDIR"

# Voice config per provider
if [ "$PROVIDER" = "elevenlabs" ]; then
    VOICE_ID="4HGP1feHKTQ1DJst6Tk8"  # Ton - male, northern, warm
    MODEL_ID="eleven_turbo_v2_5"
    PROVIDER_PARAM="elevenlabs"
    LANGUAGE_PARAM=""
    SPEED_PARAM="1.0"
    echo "🎤 Using ElevenLabs (Ton - male, northern, warm)"
elif [ "$PROVIDER" = "elevenlabs-female" ]; then
    VOICE_ID="KqbkuMVLVelcCTkFXEbE"  # Man Nghi - female, southern, calm
    MODEL_ID="eleven_turbo_v2_5"
    PROVIDER_PARAM="elevenlabs"
    LANGUAGE_PARAM=""
    SPEED_PARAM="1.0"
    echo "🎤 Using ElevenLabs (Man Nghi - female, southern, calm)"
else
    VOICE_ID="362703657091273"  # Podcast Host - Vietnamese, Resonant
    MODEL_ID="speech-2.8-turbo"
    PROVIDER_PARAM="minimax"
    LANGUAGE_PARAM="Vietnamese"
    SPEED_PARAM="1.1"
    echo "🎤 Using MiniMax (Podcast Host - Vietnamese)"
fi

generate() {
    local num=$1
    local name=$2
    local text_file="$OUTDIR/${name}.txt"
    local out_file="$OUTDIR/${name}_podcast.mp3"
    
    if [ ! -f "$text_file" ]; then
        echo "  ❌ Text file not found: $text_file"
        return 1
    fi
    
    if [ -f "$out_file" ]; then
        echo "  ⏩ $name already exists, skipping"
        return 0
    fi
    
    echo "🎤 Generating $name with $PROVIDER_PARAM..."
    
    # Build JSON payload based on provider
    if [ "$PROVIDER_PARAM" = "minimax" ]; then
        local payload=$(python3 -c "
import json, sys
text = open('$text_file').read().strip()
print(json.dumps({
    'text': text,
    'model_id': '$MODEL_ID',
    'provider': 'minimax',
    'language_code': '$LANGUAGE_PARAM',
    'voice_settings': {'speed': $SPEED_PARAM, 'pitch': -2, 'vol': 1.0}
}))
")
    else
        local payload=$(python3 -c "
import json, sys
text = open('$text_file').read().strip()
print(json.dumps({
    'text': text,
    'model_id': '$MODEL_ID',
    'provider': 'elevenlabs',
    'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0, 'use_speaker_boost': True, 'speed': $SPEED_PARAM}
}))
")
    fi
    
    local response=$(curl -s -X POST "$BASE_URL/text-to-speech/$VOICE_ID"       -H "xi-api-key: $API_KEY"       -H "Content-Type: application/json"       -d "$payload")
    
    local task_id=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id') or d.get('task_id') or d.get('history_id',''))" 2>/dev/null)
    
    if [ -z "$task_id" ]; then
        echo "  ❌ Error: $response" | head -c 500
        return 1
    fi
    
    echo "  Task ID: $task_id"
    
    for i in $(seq 1 60); do
        sleep 3
        local poll=$(curl -s "$BASE_URL/history/$task_id" -H "xi-api-key: $API_KEY")
        local status=$(echo "$poll" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status') or d.get('state',''))" 2>/dev/null)
        
        if [ "$status" = "completed" ] || [ "$status" = "done" ]; then
            local audio_url=$(echo "$poll" | python3 -c "
import json, sys
d = json.load(sys.stdin)
r = d.get('result', {})
print(r.get('audio_url', '') if isinstance(r, dict) else d.get('audio_url', ''))
" 2>/dev/null)
            
            if [ -n "$audio_url" ]; then
                curl -sL -o "$out_file" "$audio_url"
                local dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$out_file" 2>/dev/null || echo "?")
                echo "  ✅ Done! Duration: ${dur}s"
                return 0
            fi
        elif [ "$status" = "processing" ] || [ "$status" = "pending" ] || [ "$status" = "queued" ]; then
            if [ $((i % 5)) -eq 0 ]; then echo "  Polling... ($i)"; fi
        else
            echo "  ⚠️ Status: $status"
            return 1
        fi
    done
    echo "  ❌ Timeout"
    return 1
}

# Video registry — users should customize this for their project
# Format: NUMBER:videoN_name (name matches HTML file and TTS text file)
VIDEOS="1:video1_example 2:video2_example"

if [ "$1" = "all" ]; then
    for entry in $VIDEOS; do
        num=${entry%%:*}
        name=${entry##*:}
        generate "$num" "$name"
    done
elif [ -n "$1" ]; then
    for entry in $VIDEOS; do
        num=${entry%%:*}
        name=${entry##*:}
        if [ "$num" = "$1" ]; then
            generate "$num" "$name"
            break
        fi
    done
else
    echo "Usage: ITERA102_API_KEY=YOUR_KEY ./tts.sh <number> [minimax|elevenlabs|elevenlabs-female]"
    echo ""
    echo "Providers:"
    echo "  minimax            (default) MiniMax Podcast Host, fast, Vietnamese"
    echo "  elevenlabs         Ton - male, northern, warm voice"
    echo "  elevenlabs-female  Man Nghi - female, southern, calm voice"
    exit 1
fi

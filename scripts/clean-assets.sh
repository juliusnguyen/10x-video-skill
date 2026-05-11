#!/bin/bash
# Video Production Cleanup — clears old assets to free disk
# Usage: ./clean-assets.sh [video_number] [--full] [--all]
#   Default: clears frame PNGs + temp files (safe, keeps final MP4/HTML/TTS)
#   video_number: clear specific video's frames only (e.g., ./clean-assets.sh 10)
#   --full : also removes final MP4 outputs (use after backup/upload)
#   --all  : nuclear — remove ALL generated assets (frames, tmp, thumbnails html)

set -e
cd "$(dirname "$0")"

FULL=false
ALL=false
VIDEO_NUM=""

for arg in "$@"; do
    case "$arg" in
        --full) FULL=true ;;
        --all) ALL=true ;;
        [0-9]*) VIDEO_NUM="$arg" ;;
    esac
done

echo "🧹 Cleaning video production assets..."
echo ""

FREED=0

# If specific video number, clear that video's frames only
if [ -n "$VIDEO_NUM" ]; then
    FRAMES_DIR="frames_${VIDEO_NUM}"
    if [ -d "$FRAMES_DIR" ]; then
        SIZE=$(du -sh "$FRAMES_DIR" 2>/dev/null | awk '{print $1}')
        rm -rf "$FRAMES_DIR"
        echo "  ✅ Cleared $FRAMES_DIR ($SIZE freed)"
        FREED=1
    else
        echo "  ⏩ No $FRAMES_DIR to clean"
    fi
    # Also clear temp mp4 for this video
    for f in output/*.temp.mp4; do
        [ -f "$f" ] && rm -f "$f" && echo "  ✅ Cleared temp MP4: $f"
    done
else
    # Default: clear ALL frame directories
    if ls -d frames_*/ 2>/dev/null; then
        SIZE=$(du -sh frames_*/ 2>/dev/null | tail -1 | awk '{print $1}')
        rm -rf frames_*/
        echo "  ✅ Cleared ALL frame directories ($SIZE total freed)"
        FREED=1
    else
        echo "  ⏩ No frame directories to clean"
    fi
fi

# Temp MP4 files
TEMP_COUNT=$(ls output/*.temp.mp4 2>/dev/null | wc -l)
if [ "$TEMP_COUNT" -gt 0 ]; then
    rm -f output/*.temp.mp4
    echo "  ✅ Cleared $TEMP_COUNT temp MP4 files"
fi

# Thumbnail HTML sources
THUMB_HTML=$(ls thumbnails/*.html 2>/dev/null | wc -l)
if [ "$THUMB_HTML" -gt 0 ]; then
    rm -f thumbnails/*.html
    echo "  ✅ Cleared $THUMB_HTML thumbnail HTML sources"
fi

# tmp directory
if [ -d "tmp" ]; then
    rm -rf tmp
    echo "  ✅ Cleared tmp/ directory"
fi

if [ "$ALL" = true ]; then
    echo ""
    echo "☢️  Nuclear clean — removing ALL generated assets!"
    rm -rf frames_*/ tmp/
    rm -f output/*.temp.mp4 thumbnails/*.html
    echo "  ✅ Nuclear clean done"
fi

if [ "$FULL" = true ]; then
    echo ""
    echo "⚠️  Full clean — removing final MP4 outputs too!"
    MP4_COUNT=$(ls output/*.mp4 2>/dev/null | wc -l)
    if [ "$MP4_COUNT" -gt 0 ]; then
        MP4_SIZE=$(du -sh output/*.mp4 2>/dev/null | tail -1 | awk '{print $1}')
        rm -f output/*.mp4
        echo "  ✅ Cleared $MP4_COUNT MP4 outputs ($MP4_SIZE freed)"
    fi
fi

echo ""
echo "📊 Disk usage:"
df -h . | tail -1 | awk '{print "   Used: "$3"  Free: "$4"  Use%: "$5}'
echo ""
echo "🧹 Done!"

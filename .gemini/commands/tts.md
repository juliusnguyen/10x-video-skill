Generate TTS voiceover using the iterA102 API.

Usage: `ITERA102_API_KEY="your_key" bash scripts/tts.sh <N> [provider]`

Providers: `minimax` (default), `elevenlabs`, `elevenlabs-female`.

Steps:
1. Ensure `ITERA102_API_KEY` is set.
2. Run the script with the video number/name.
3. Check `voices/` for the generated `.mp3` and `.txt` files.

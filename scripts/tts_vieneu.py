import argparse
import os
import sys
from vieneu import Vieneu

def main():
    parser = argparse.ArgumentParser(description="VieNeu TTS CLI Wrapper")
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--file", help="Path to text file")
    parser.add_argument("--output", required=True, help="Output audio file path")
    parser.add_argument("--emotion", default="natural", choices=["natural", "storytelling"], help="Inference emotion")
    parser.add_argument("--mode", default="standard", choices=["standard", "turbo", "remote"], help="Inference mode")
    parser.add_argument("--voice", help="Preset voice ID")

    args = parser.parse_args()

    # Get text
    if args.text:
        text = args.text
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    else:
        print("Error: Either --text or --file must be provided.")
        sys.exit(1)

    if not text:
        print("Error: Input text is empty.")
        sys.exit(1)

    print(f"Initializing VieNeu (mode={args.mode}, emotion={args.emotion})...")
    tts = Vieneu(mode=args.mode, emotion=args.emotion)

    voice_data = None
    if args.voice:
        print(f"Using preset voice: {args.voice}")
        voice_data = tts.get_preset_voice(args.voice)

    print(f"Synthesizing text: {text[:50]}...")
    audio = tts.infer(text=text, voice=voice_data)

    print(f"Saving to {args.output}...")
    # Vieneu save usually handles the audio data correctly
    tts.save(audio, args.output)
    print("Done.")

if __name__ == "__main__":
    main()

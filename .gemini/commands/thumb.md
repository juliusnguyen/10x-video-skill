Generate a thumbnail for the video.

Usage: `/thumb <N>`

Steps:
1. Write SVG with design tokens.
2. Convert SVG to PNG using `python3 -c "import cairosvg; ..."`
3. Convert PNG to JPEG using `ffmpeg`.
4. Save to `thumbnails/videoN_name.jpg`.

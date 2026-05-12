Perform Pixel Quality Control on the rendered video.

Run: `python3 -c "from PIL import Image; import numpy as np; arr=np.array(Image.open('/tmp/qc5s.png')); print(f'mean={arr.mean():.1f} max={arr.max()} unique={len(np.unique(arr.reshape(-1,3),axis=0))}')"`

Note: You must first extract a frame using ffmpeg:
`ffmpeg -y -ss 5 -i output/video{N}_{name}.mp4 -frames:v 1 -update 1 /tmp/qc5s.png`

Pass criteria: `mean > 18, max = 255, unique > 5000`.

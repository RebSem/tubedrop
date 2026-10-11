# tubedrop — promo video

LinkedIn promo (1080×1350, 4:5, 30 fps). `BPM = 87` gives the 41 s cut (v2); `BPM = 120` gives the original 30 s cut (v1). Built with [Remotion](https://remotion.dev).

```
npm install
npm run studio   # live preview / scrub
npm run build    # synth audio → render → loudness-master → out/tubedrop-promo-final.mp4
```

## How it's put together

- **Everything sits on a beat grid.** `src/config.ts` holds `BPM`, the scene ranges (in beats) and
  `MUSIC_OFFSET`. Every animation and every sound cue is written in beats, so changing the tempo moves
  every cut with it.
- **Scenes** (`src/scenes/`): `Hook` (departure board → 3-hour interview → zero wi-fi), `Scam`,
  `Cli`, `Vibe`, `Product` (logo drop + flight over the real app UI), `Features`, `Outro`.
- **The app UI** (`src/components/AppUI.tsx`) is rebuilt from `ytconverter/web/ui.py`. It isn't a
  screenshot, so the camera can fly over it.
- **All audio is synthesised** by `scripts/make_audio.py` (numpy only): every SFX plus a temporary
  guide track at the edit's BPM. Nothing to license.

## Swapping in the real track

1. Drop the file into `public/music/` and point `MUSIC_FILE` at it.
2. Set `BPM` to the track's tempo. Set `MUSIC_OFFSET` (in seconds) so that beat 28, the logo drop
   (14 s in at 120 BPM, 19 s at 87), lands on the track's drop: `MUSIC_OFFSET = dropTime - 28 * 60 / BPM`.
3. Run `npm run sfx` (the riser, ticks and progress sounds follow `BPM`), then `npm run build`.

// Single source of truth for timing. Everything is laid out on a beat grid,
// so swapping the music track = change BPM / MUSIC_OFFSET and every cut moves.
export const FPS = 30;
export const W = 1080;
export const H = 1350;

// 120 = v1 (fast cut). 87 = v2, the same edit at 72.5% speed.
export const BPM = 87;
// Seconds into the music file where beat 0 of the edit sits (its first downbeat).
export const MUSIC_OFFSET = 0;
export const MUSIC_FILE = 'music/temp-beat.wav';

export const FPB = (60 / BPM) * FPS; // frames per beat
export const TOTAL_BEATS = 60;
export const f = (beats: number) => Math.round(beats * FPB);

// [startBeat, endBeat]
export const SCENES = {
  hook: [0, 8],
  scam: [8, 16],
  cli: [16, 22],
  vibe: [22, 28],
  product: [28, 44], // logo drop + app demo (one continuous scene)
  features: [44, 52],
  outro: [52, 60],
} as const;

export const C = {
  ink: '#0B0B10',
  ink2: '#16161D',
  ink3: '#1F1F28',
  paper: '#F1F0EC',
  paper2: '#FAFAF7',
  white: '#FFFFFF',
  text: '#0A0A0F',
  muted: '#5E5E66',
  subtle: '#8A8A92',
  border: 'rgba(15,15,20,0.07)',
  borderStrong: 'rgba(15,15,20,0.12)',
  blue: '#0066FF',
  blueHi: '#3D88FF',
  blueDeep: '#0052D4',
  blueSoft: 'rgba(0,102,255,0.10)',
  green: '#16A34A',
  mint: '#2DD692',
  orange: '#FF9500',
  red: '#FF2D3D',
  ytRed: '#FF0033',
  yellow: '#FFE14D',
  amber: '#FFB800',
};

import {Easing, interpolate, spring, useCurrentFrame} from 'remotion';
import {FPB, FPS} from './config';

export const EXPO_OUT = Easing.bezier(0.16, 1, 0.3, 1);
export const STRONG_OUT = Easing.bezier(0.23, 1, 0.32, 1); // rebsem.ru --ease-out-strong
export const STRONG_IN_OUT = Easing.bezier(0.77, 0, 0.175, 1); // rebsem.ru --ease-in-out-strong
export const BACK_OUT = Easing.bezier(0.34, 1.56, 0.64, 1);
export const EXPO_IN = Easing.bezier(0.7, 0, 0.84, 0);

/** Current local time in beats (inside the nearest Sequence). */
export const useBeat = () => useCurrentFrame() / FPB;

/** Clamped interpolation on the beat clock. */
export const tw = (
  t: number,
  t0: number,
  t1: number,
  from: number,
  to: number,
  easing: (x: number) => number = EXPO_OUT,
) =>
  interpolate(t, [t0, t1], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing,
  });

/** Spring that starts at beat t0. */
export const sp = (
  t: number,
  t0: number,
  config: {damping?: number; stiffness?: number; mass?: number} = {},
) =>
  spring({
    frame: Math.max(0, (t - t0) * FPB),
    fps: FPS,
    config: {damping: 14, stiffness: 170, mass: 0.9, ...config},
  });

/** 1 on every beat, decaying to 0 before the next one. */
export const pulse = (t: number, every = 1, sharp = 7) => {
  if (t < 0) return 0;
  const ph = (t % every) / every;
  return Math.exp(-ph * sharp);
};

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));

/** Deterministic pseudo-random in [0,1). */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

export const between = (t: number, a: number, b: number) => t >= a && t < b;

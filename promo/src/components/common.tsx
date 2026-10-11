import React from 'react';
import {AbsoluteFill, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {Audio} from '@remotion/media';
import {C, f} from '../config';
import {mono} from '../fonts';

/* ───────────── sound ───────────── */

export const Sfx: React.FC<{name: string; at: number; volume?: number}> = ({
  name,
  at,
  volume = 1,
}) => (
  <Sequence from={f(at)} layout="none" name={`sfx:${name}`}>
    <Audio src={staticFile(`sfx/${name}.wav`)} volume={volume} />
  </Sequence>
);

/* ───────────── film grain ───────────── */

export const Grain: React.FC<{opacity?: number}> = ({opacity = 0.07}) => {
  const frame = useCurrentFrame();
  const seed = frame % 12;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'overlay', opacity}}>
      <svg width="100%" height="100%">
        <filter id={`grain-${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={seed} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#grain-${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

/* ───────────── directional blur (fake motion blur) ───────────── */

export const DirBlur: React.FC<{
  id: string;
  x?: number;
  y?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({id, x = 0, y = 0, children, style}) => {
  const on = x > 0.4 || y > 0.4;
  return (
    <AbsoluteFill style={style}>
      {on ? (
        <svg width="0" height="0" style={{position: 'absolute'}}>
          <filter id={id} x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation={`${x.toFixed(2)} ${y.toFixed(2)}`} />
          </filter>
        </svg>
      ) : null}
      <AbsoluteFill style={{filter: on ? `url(#${id})` : undefined}}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ───────────── tubedrop logo (matches .logo in ui.py) ───────────── */

export const Logo: React.FC<{
  size: number;
  shine?: number; // 0..1 sweep position of a glossy highlight
  glow?: number; // 0..1 extra outer glow
  style?: React.CSSProperties;
}> = ({size, shine = -1, glow = 0, style}) => {
  const r = size * (16 / 52);
  return (
    <div
      style={{
        position: 'relative',
        width: size,
        height: size,
        borderRadius: r,
        background: `linear-gradient(160deg, #3A85FF 0%, ${C.blue} 50%, ${C.blueDeep} 100%)`,
        boxShadow: [
          `inset 0 ${size * 0.02}px 0 rgba(255,255,255,0.35)`,
          `inset 0 ${-size * 0.15}px ${size * 0.27}px rgba(0,0,0,0.18)`,
          `0 ${size * 0.115}px ${size * 0.27}px ${-size * 0.04}px rgba(0,102,255,${0.45 + glow * 0.3})`,
          `0 ${size * 0.23}px ${size * 0.54}px ${-size * 0.115}px rgba(0,102,255,${0.25 + glow * 0.3})`,
        ].join(','),
        display: 'grid',
        placeItems: 'center',
        overflow: 'hidden',
        flexShrink: 0,
        ...style,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse at 30% 20%, rgba(255,255,255,0.4) 0%, transparent 55%)',
        }}
      />
      {shine >= 0 && shine <= 1 ? (
        <div
          style={{
            position: 'absolute',
            top: -size * 0.5,
            left: -size + shine * size * 3,
            width: size * 0.35,
            height: size * 2,
            transform: 'rotate(25deg)',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.55), transparent)',
          }}
        />
      ) : null}
      <span
        style={{
          position: 'relative',
          fontFamily: mono,
          fontWeight: 700,
          fontSize: size * (19 / 52),
          letterSpacing: '-0.05em',
          color: 'white',
          textShadow: `0 ${size * 0.02}px 0 rgba(0,0,0,0.15)`,
          lineHeight: 1,
        }}
      >
        td
      </span>
    </div>
  );
};

/* ───────────── mac cursor ───────────── */

export const Cursor: React.FC<{
  x: number;
  y: number;
  size?: number;
  press?: number; // 0..1
  ripple?: number; // 0..1 progress of click ripple, <0 = none
  rippleColor?: string;
  opacity?: number;
}> = ({x, y, size = 46, press = 0, ripple = -1, rippleColor = C.blue, opacity = 1}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, opacity, zIndex: 50}}>
    {ripple >= 0 && ripple <= 1 ? (
      <div
        style={{
          position: 'absolute',
          left: -size * (0.3 + ripple * 0.9),
          top: -size * (0.3 + ripple * 0.9),
          width: size * (0.6 + ripple * 1.8),
          height: size * (0.6 + ripple * 1.8),
          borderRadius: '50%',
          border: `${Math.max(1, 5 * (1 - ripple))}px solid ${rippleColor}`,
          opacity: 1 - ripple,
        }}
      />
    ) : null}
    <svg
      width={size}
      height={size * 1.4}
      viewBox="0 0 20 28"
      style={{
        position: 'absolute',
        left: -size * 0.12,
        top: -size * 0.06,
        transform: `scale(${1 - press * 0.16})`,
        transformOrigin: '10% 5%',
        filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.35))',
      }}
    >
      <path
        d="M2 1.5 L2 22.5 L7.2 17.6 L10.6 25.6 L14.1 24.1 L10.8 16.3 L17.8 16.3 Z"
        fill="#000"
        stroke="#fff"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  </div>
);

/* ───────────── icons (lucide-style, same set as the app) ───────────── */

type IconProps = {size?: number; color?: string; stroke?: number; style?: React.CSSProperties};

const mk =
  (children: React.ReactNode, fill = false) =>
  ({size = 24, color = 'currentColor', stroke = 2, style}: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={fill ? color : 'none'}
      stroke={fill ? 'none' : color}
      strokeWidth={stroke}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{display: 'block', flexShrink: 0, ...style}}
    >
      {children}
    </svg>
  );

export const I = {
  link: mk(
    <>
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </>,
  ),
  download: mk(<path d="M12 3v13m0 0-4.5-4.5M12 16l4.5-4.5M5 21h14" />),
  video: mk(
    <>
      <rect x="2" y="6" width="14" height="12" rx="2" />
      <path d="m22 8-6 4 6 4V8Z" />
    </>,
  ),
  music: mk(
    <>
      <path d="M9 18V5l12-2v13" />
      <circle cx="6" cy="18" r="3" />
      <circle cx="18" cy="16" r="3" />
    </>,
  ),
  folder: mk(<path d="M4 5a2 2 0 0 1 2-2h3.5L12 5h6a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5Z" />),
  check: mk(<path d="m5 12 5 5L20 7" />),
  x: mk(<path d="M18 6 6 18M6 6l12 12" />),
  sparkle: mk(
    <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1" />,
  ),
  lock: mk(
    <>
      <rect x="4" y="11" width="16" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </>,
  ),
  alert: mk(
    <>
      <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
      <path d="M12 9v4M12 17h.01" />
    </>,
  ),
  plane: mk(
    <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z" />,
    true,
  ),
  star: mk(
    <path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z" />,
    true,
  ),
  bell: mk(
    <>
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
    </>,
  ),
  puzzle: mk(
    <path d="M19.4 14.6c.6 0 1.1-.3 1.5-.7a2.1 2.1 0 0 0 0-3c-.4-.4-.9-.7-1.5-.7H18V7a1 1 0 0 0-1-1h-3.2V4.6c0-.6-.3-1.1-.7-1.5a2.1 2.1 0 0 0-3 0c-.4.4-.7.9-.7 1.5V6H6a1 1 0 0 0-1 1v3.2h1.4c.6 0 1.1.3 1.5.7a2.1 2.1 0 0 1 0 3c-.4.4-.9.7-1.5.7H5V18a1 1 0 0 0 1 1h3.4v-1.4c0-.6.3-1.1.7-1.5a2.1 2.1 0 0 1 3 0c.4.4.7.9.7 1.5V19H17a1 1 0 0 0 1-1v-3.4z" />,
  ),
  gift: mk(
    <>
      <rect x="3" y="8" width="18" height="4" rx="1" />
      <path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7" />
      <path d="M7.5 8a2.5 2.5 0 0 1 0-5C10 3 12 8 12 8s2-5 4.5-5a2.5 2.5 0 0 1 0 5" />
    </>,
  ),
  github: ({size = 24, color = 'currentColor', style}: IconProps) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={color} style={{display: 'block', flexShrink: 0, ...style}}>
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.55v-2.16c-3.2.69-3.87-1.36-3.87-1.36-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.71.08-.71 1.17.08 1.78 1.2 1.78 1.2 1.04 1.77 2.72 1.26 3.38.96.11-.75.41-1.26.74-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.46.11-3.04 0 0 .97-.31 3.18 1.18.92-.26 1.91-.39 2.89-.39.98 0 1.97.13 2.89.39 2.21-1.49 3.18-1.18 3.18-1.18.63 1.58.23 2.75.11 3.04.74.81 1.18 1.84 1.18 3.1 0 4.42-2.69 5.39-5.26 5.68.42.36.79 1.07.79 2.16v3.2c0 .31.21.66.8.55C20.21 21.38 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z" />
    </svg>
  ),
};

/* ───────────── text helpers ───────────── */

/** Line that slides up out of an overflow mask. p: 0 hidden → 1 shown; q: 0 → 1 leaving upwards. */
export const MaskLine: React.FC<{
  p: number;
  q?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
  pad?: number;
}> = ({p, q = 0, children, style, pad = 0.12}) => (
  <div style={{overflow: 'hidden', paddingBottom: `${pad}em`, marginBottom: `-${pad}em`, ...style}}>
    <div style={{transform: `translateY(${(1 - p) * 115 - q * 115}%)`}}>{children}</div>
  </div>
);

export const Kbd: React.FC<{children: React.ReactNode; size?: number; press?: number}> = ({
  children,
  size = 120,
  press = 0,
}) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size * 0.22,
      background: 'linear-gradient(180deg,#FFFFFF,#F1F0EC)',
      border: `2px solid ${C.borderStrong}`,
      boxShadow: `0 ${size * 0.07 * (1 - press)}px 0 #C9C8C2, 0 ${size * 0.2}px ${size * 0.35}px -${size * 0.1}px rgba(0,0,0,0.25)`,
      transform: `translateY(${size * 0.06 * press}px)`,
      display: 'grid',
      placeItems: 'center',
      fontFamily: mono,
      fontWeight: 600,
      fontSize: size * 0.5,
      color: C.text,
    }}
  >
    {children}
  </div>
);

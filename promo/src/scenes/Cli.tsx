import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C} from '../config';
import {display, mono, serif} from '../fonts';
import {EXPO_IN, EXPO_OUT, STRONG_OUT, tw, useBeat} from '../anim';
import {MaskLine, Sfx} from '../components/common';

type Line = {at: number; text: string; color?: string; typed?: number; input?: string};

const G = '#7CFFB2';
const Y = '#FFD866';
const D = '#6B6B75';

// "typed" = beats it takes to type the user input at the end of the line
const LINES: Line[] = [
  {at: 0.05, text: '~ % ', color: G, input: 'python3 -m ytconverter', typed: 0.45},
  {at: 0.55, text: '+------------------------------+', color: Y},
  {at: 0.6, text: '|   Y T C O N V E R T E R      |', color: Y},
  {at: 0.65, text: '+------------------------------+', color: Y},
  {at: 0.75, text: ' [1] Single video   (MP4)'},
  {at: 0.8, text: ' [2] Single audio   (MP3)'},
  {at: 0.85, text: ' [3] Playlist       (MP4)'},
  {at: 0.9, text: ' [4] Playlist       (MP3)'},
  {at: 0.95, text: ' [5] Multiple links'},
  {at: 1.0, text: ' [6] Exit'},
  {at: 1.15, text: '? Enter your choice [1-6]: ', color: G, input: '1', typed: 0.1},
  {at: 1.45, text: '? Paste URL: ', color: G, input: 'https://youtu.be/xY3h…', typed: 0.3},
  {at: 1.9, text: '  fetching formats…', color: D},
  {at: 2.1, text: ' [1] 144p  [2] 240p  [3] 360p'},
  {at: 2.15, text: ' [4] 480p  [5] 720p  [6] 1080p'},
  {at: 2.35, text: '? Select resolution [1-6]: ', color: G, input: '6', typed: 0.1},
  {at: 2.65, text: '? Output dir [./downloads]: ', color: G, input: '', typed: 0},
  {at: 2.95, text: '? Embed thumbnail? [y/N]: ', color: G, input: 'y', typed: 0.1},
  {at: 3.25, text: '? Continue? [Y/n]: ', color: G, input: 'Y', typed: 0.1},
  {at: 3.55, text: '  ERROR: Sign in to confirm you’re not a bot', color: '#FF6B6B'},
  {at: 3.75, text: '? Retry? [Y/n]: ', color: G, input: '█', typed: 0},
];

export const Cli: React.FC = () => {
  const t = useBeat();
  const frame = useCurrentFrame();

  const visible = LINES.filter((l) => t >= l.at);
  const maxLines = 17;
  const shown = visible.slice(-maxLines);

  // captions
  const c1 = tw(t, 0, 0.5, 0, 1, STRONG_OUT);
  const c2in = tw(t, 1.75, 2.2, 0, 1, STRONG_OUT);
  const c2out = tw(t, 3.15, 3.4, 0, 1, EXPO_IN);
  const c3in = tw(t, 3.3, 3.75, 0, 1, STRONG_OUT);

  // CRT power-off
  const sy = tw(t, 5.0, 5.22, 1, 0.006, EXPO_IN);
  const sx = tw(t, 5.25, 5.5, 1, 0.0, EXPO_IN);
  const bright = tw(t, 4.95, 5.2, 1, 3.5, EXPO_IN);
  const dotFade = tw(t, 5.45, 5.8, 1, 0, EXPO_OUT);

  const flicker = 0.96 + Math.sin(frame * 1.7) * 0.02 + (frame % 7 === 0 ? -0.03 : 0);

  return (
    <AbsoluteFill style={{background: '#050506', overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          transform: `scale(${sx}, ${sy})`,
          filter: `brightness(${bright})`,
          opacity: dotFade,
        }}
      >
        {/* captions */}
        <div style={{position: 'absolute', left: 60, right: 60, top: 92}}>
          <MaskLine p={c1}>
            <div style={{fontFamily: display, fontWeight: 600, fontSize: 52, letterSpacing: '-0.03em', color: '#9C9CA6'}}>
              Then I remembered a CLI tool I had.
            </div>
          </MaskLine>
          <div style={{position: 'relative', height: 170, marginTop: 14}}>
            <div style={{position: 'absolute', inset: 0}}>
              <MaskLine p={c2in} q={c2out}>
                <div style={{fontFamily: display, fontWeight: 900, fontSize: 150, letterSpacing: '-0.06em', lineHeight: 1, color: '#fff'}}>
                  It worked<span style={{color: G}}>.</span>
                </div>
              </MaskLine>
            </div>
            <div style={{position: 'absolute', inset: 0}}>
              <MaskLine p={c3in}>
                <div style={{fontFamily: display, fontWeight: 900, fontSize: 150, letterSpacing: '-0.06em', lineHeight: 1, color: '#fff'}}>
                  I{' '}
                  <span style={{fontFamily: serif, fontWeight: 500, fontStyle: 'italic', letterSpacing: '-0.03em', color: C.orange}}>hated</span>{' '}
                  it.
                </div>
              </MaskLine>
            </div>
          </div>
        </div>

        {/* terminal window */}
        <div
          style={{
            position: 'absolute',
            left: 50,
            top: 432,
            width: 980,
            height: 860,
            borderRadius: 22,
            background: '#0C0C0F',
            border: '1.5px solid #2A2A32',
            boxShadow: '0 50px 120px -30px rgba(0,0,0,0.9), 0 0 80px -20px rgba(124,255,178,0.12)',
            overflow: 'hidden',
            transform: `translateY(${tw(t, 0, 0.6, 120, 0, EXPO_OUT)}px)`,
            opacity: flicker,
          }}
        >
          <div style={{height: 52, background: '#17171C', display: 'flex', alignItems: 'center', padding: '0 20px', gap: 10, borderBottom: '1px solid #24242B'}}>
            {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
              <div key={c} style={{width: 16, height: 16, borderRadius: 8, background: c, opacity: 0.85}} />
            ))}
            <div style={{flex: 1, textAlign: 'center', fontFamily: mono, fontSize: 20, color: '#77777F', marginRight: 60}}>
              ~/tools/ytconverter — zsh — 80×24
            </div>
          </div>
          <div style={{padding: '22px 30px', fontFamily: mono, fontSize: 27, lineHeight: 1.6, color: '#D8D8DE', whiteSpace: 'pre'}}>
            {shown.map((l, i) => {
              const isLast = i === shown.length - 1;
              const typedChars = l.input
                ? Math.floor(tw(t, l.at + 0.08, l.at + 0.08 + (l.typed || 0.01), 0, l.input.length, (x) => x))
                : 0;
              const cursorOn = isLast && Math.floor(frame / 8) % 2 === 0;
              return (
                <div key={l.at}>
                  <span style={{color: l.color || '#D8D8DE'}}>{l.text}</span>
                  {l.input ? <span style={{color: '#fff', fontWeight: 700}}>{l.input.slice(0, typedChars)}</span> : null}
                  {isLast && !l.input?.includes('█') ? <span style={{opacity: cursorOn ? 1 : 0, color: G}}>█</span> : null}
                </div>
              );
            })}
          </div>
          {/* scanlines */}
          <AbsoluteFill
            style={{
              backgroundImage: 'repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0 2px, transparent 2px 5px)',
              pointerEvents: 'none',
            }}
          />
        </div>
      </AbsoluteFill>

      {/* CRT dot */}
      {t > 5.2 && t < 5.9 ? (
        <div
          style={{
            position: 'absolute',
            left: 540 - 40,
            top: 675 - 40,
            width: 80,
            height: 80,
            borderRadius: 40,
            background: 'radial-gradient(circle, #fff 0%, rgba(124,255,178,0.6) 30%, transparent 70%)',
            opacity: tw(t, 5.2, 5.35, 0, 1) * tw(t, 5.5, 5.85, 1, 0),
            transform: `scale(${tw(t, 5.3, 5.85, 1.4, 0.1, EXPO_IN)})`,
          }}
        />
      ) : null}

      <Sfx name="type_long" at={0.05} volume={0.35} />
      <Sfx name="type_short" at={1.45} volume={0.35} />
      <Sfx name="type_short" at={2.35} volume={0.3} />
      <Sfx name="type_short" at={2.95} volume={0.3} />
      <Sfx name="error1" at={3.55} volume={0.35} />
      <Sfx name="hit" at={1.75} volume={0.55} />
      <Sfx name="hit" at={3.3} volume={0.65} />
      <Sfx name="zap" at={4.95} volume={0.7} />
    </AbsoluteFill>
  );
};

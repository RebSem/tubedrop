import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FPB, SCENES, f} from '../config';
import {display, mono} from '../fonts';
import {EXPO_IN, EXPO_OUT, STRONG_IN_OUT, STRONG_OUT, pulse, rand, sp, tw} from '../anim';
import {Cursor, DirBlur, I, Kbd, Logo, MaskLine, Sfx} from '../components/common';
import {AppUI, CHIP_GAP, CHIP_W, PICK_INDEX, T} from '../components/AppUI';

export const PRODUCT_PRE = 0.35; // beats of pre-roll before the drop (logo falling)
// integer-frame pre-roll so the impact lands exactly on the downbeat frame
const PRE_FRAMES = f(SCENES.product[0]) - f(SCENES.product[0] - PRODUCT_PRE);
const PRE_B = PRE_FRAMES / FPB;

/* camera keyframes over the 620px-wide app "world" */
type Cam = {t: number; fx: number; fy: number; s: number; rx: number; ry: number; rz: number; cy?: number};
const CX = 540;
const CY = 770;
const K: Cam[] = [
  {t: 4.0, fx: 310, fy: 135, s: 1.62, rx: 0, ry: 0, rz: 0},
  {t: 5.85, fx: 310, fy: 135, s: 1.62, rx: 0, ry: 0, rz: 0},
  {t: 6.3, fx: 310, fy: 330, s: 1.58, rx: 4, ry: -3, rz: 0},
  {t: 7.55, fx: 310, fy: 345, s: 1.58, rx: 4, ry: -3, rz: 0},
  {t: 7.95, fx: 310, fy: 540, s: 1.66, rx: -3, ry: 4, rz: 0},
  {t: 9.4, fx: 310, fy: 548, s: 1.66, rx: -3, ry: 4, rz: 0},
  {t: 9.85, fx: 310, fy: 790, s: 1.6, rx: 3, ry: -2, rz: 0},
  {t: 11.9, fx: 310, fy: 805, s: 1.6, rx: 3, ry: -2, rz: 0},
  {t: 12.9, fx: 310, fy: 500, s: 0.8, rx: 16, ry: -18, rz: 4, cy: 850},
  {t: 16, fx: 310, fy: 500, s: 0.85, rx: 12, ry: -10, rz: 2, cy: 850},
];

const camAt = (t: number): Cam => {
  if (t <= K[0].t) return K[0];
  for (let i = 0; i < K.length - 1; i++) {
    const a = K[i];
    const b = K[i + 1];
    if (t <= b.t) {
      const lin = (b.t - a.t) > 2 ? (x: number) => x : STRONG_IN_OUT;
      const k = tw(t, a.t, b.t, 0, 1, lin);
      const m = (x: number, y: number) => x + (y - x) * k;
      return {t, fx: m(a.fx, b.fx), fy: m(a.fy, b.fy), s: m(a.s, b.s), rx: m(a.rx, b.rx), ry: m(a.ry, b.ry), rz: m(a.rz, b.rz), cy: m(a.cy ?? CY, b.cy ?? CY)};
    }
  }
  return K[K.length - 1];
};

/* where things live in the world (px inside the 620px shell) */
const W_LOGO = {cx: 30, cy: 26, size: 52};
const W_WORD = {x: 70, y: 3, fs: 22};
const W_INPUT = {x: 250, y: 152};
const W_FETCH = {x: 544, y: 152};
const W_AUDIO = {x: 452, y: 408};
const W_VIDEO = {x: 168, y: 408};
const chipCenter = (i: number) => {
  const row = i < 5 ? 0 : 1;
  const col = row === 0 ? i : i - 5;
  return {x: 23 + col * (CHIP_W + CHIP_GAP) + CHIP_W / 2, y: 523.5 + row * 45};
};
const W_CTA = {x: 330, y: 813};

const CURSOR: [number, number, number][] = [
  // t, x, y (world)
  [4.15, 600, 330],
  [4.6, W_INPUT.x, W_INPUT.y],
  [5.25, W_INPUT.x, W_INPUT.y],
  [5.55, W_FETCH.x, W_FETCH.y],
  [6.35, W_FETCH.x, W_FETCH.y + 40],
  [6.7, W_AUDIO.x, W_AUDIO.y],
  [7.0, W_AUDIO.x, W_AUDIO.y],
  [7.25, W_VIDEO.x, W_VIDEO.y],
  [8.3, W_VIDEO.x + 60, W_VIDEO.y + 90],
  [8.9, chipCenter(PICK_INDEX).x, chipCenter(PICK_INDEX).y],
  [9.5, chipCenter(PICK_INDEX).x, chipCenter(PICK_INDEX).y],
  [9.9, W_CTA.x, W_CTA.y],
  [10.4, W_CTA.x, W_CTA.y],
  [11.0, 560, 1000],
];
const CLICKS = [T.click1, T.fetch, T.toAudio, T.toVideo, T.pick, T.download];

const cursorAt = (t: number) => {
  let x = CURSOR[0][1];
  let y = CURSOR[0][2];
  for (let i = 0; i < CURSOR.length - 1; i++) {
    const [ta, xa, ya] = CURSOR[i];
    const [tb, xb, yb] = CURSOR[i + 1];
    if (t >= ta) {
      const k = tw(t, ta, tb, 0, 1, STRONG_IN_OUT);
      x = xa + (xb - xa) * k;
      y = ya + (yb - ya) * k;
    }
  }
  return {x, y};
};

const CAPTIONS: {at: number; out: number; num: string; text: React.ReactNode}[] = [
  {at: 4.0, out: 6.1, num: '01', text: 'Paste a link.'},
  {at: 6.25, out: 7.75, num: '02', text: 'Video or MP3.'},
  {at: 7.9, out: 9.55, num: '03', text: 'Pick the quality.'},
  {at: 9.7, out: 11.85, num: '04', text: 'Hit download.'},
  {
    at: 12.0,
    out: 99,
    num: '✓',
    text: (
      <>
        Done.
        <br />
        <span style={{color: C.blue}}>Before boarding.</span>
      </>
    ),
  },
];

export const Product: React.FC = () => {
  const frame = useCurrentFrame();
  const t = (frame - PRE_FRAMES) / FPB; // 0 = the drop

  /* ═════ phase 1: the drop ═════ */
  const fallK = tw(t, -PRE_B, 0, 0, 1, (x) => x * x);
  const landed = t >= 0;
  const squashS = sp(t, 0, {damping: 7, stiffness: 320, mass: 0.7});
  const squash = landed ? (1 - squashS) * 0.42 : 0;
  const logoBigCx = 540;
  const logoBigCy = 520;
  const logoBigSize = 280;
  const fallY = landed ? logoBigCy : -320 + (logoBigCy + 320) * fallK;
  const stretch = landed ? 0 : 0.16 * fallK;

  const flood = tw(t, 0, 0.55, 0, 1, EXPO_OUT);
  const ring = tw(t, 0, 0.7, 0, 1, EXPO_OUT);
  const flash = tw(t, 0, 0.18, 0.9, 0);

  /* ═════ phase 2: magic move into the app header (3.0 → 4.0) ═════ */
  const mm = tw(t, 3.0, 4.0, 0, 1, STRONG_IN_OUT);
  const cam = camAt(t);
  const hLogoCx = CX + cam.s * (W_LOGO.cx - cam.fx);
  const camCy = cam.cy ?? CY;
  const hLogoCy = camCy + cam.s * (W_LOGO.cy - cam.fy);
  const hLogoSize = W_LOGO.size * cam.s;
  const hWordX = CX + cam.s * (W_WORD.x - cam.fx);
  const hWordY = camCy + cam.s * (W_WORD.y - cam.fy);
  const hWordFs = W_WORD.fs * cam.s;

  const bigWordFs = 160;
  const bigWordX = 540 - (8 * 0.56 * bigWordFs) / 2;
  const bigWordY = 780;

  const lerp = (a: number, b: number) => a + (b - a) * mm;
  const logoCx = lerp(logoBigCx, hLogoCx);
  const logoCy = lerp(fallY, hLogoCy);
  const logoSize = lerp(logoBigSize, hLogoSize);
  const wordX = lerp(bigWordX, hWordX);
  const wordY = lerp(bigWordY, hWordY);
  const wordFs = lerp(bigWordFs, hWordFs);
  const brandInWorld = t >= 4.0;

  const tagline = '// drop a link. get the file.';
  const tagTyped = Math.floor(tw(t, 1.8, 2.6, 0, tagline.length, (x) => x));
  const tagOut = tw(t, 2.9, 3.2, 0, 1, EXPO_IN);

  /* ═════ demo ═════ */
  const cur = cursorAt(t);
  const lastClick = CLICKS.filter((c) => t >= c).pop();
  const press = lastClick !== undefined ? tw(t, lastClick, lastClick + 0.15, 1, 0) : 0;
  const ripple = lastClick !== undefined && t < lastClick + 0.45 ? tw(t, lastClick, lastClick + 0.45, 0, 1, (x) => x) : -1;
  const cursorOpacity = tw(t, 4.1, 4.3, 0, 1) * tw(t, 11.0, 11.3, 1, 0);

  const keysIn = sp(t, 4.7, {damping: 13, stiffness: 260});
  const keysOut = tw(t, 5.45, 5.7, 0, 1, EXPO_IN);
  const keyPress = t >= T.paste ? tw(t, T.paste, T.paste + 0.2, 1, 0) : 0;

  const toastIn = sp(t, 13.5, {damping: 13, stiffness: 220});
  const toggleOn = tw(t, 13.75, 13.95, 0, 1, EXPO_OUT);

  const whip = tw(t, 15.55, 16, 0, 1, EXPO_IN);
  const bump = 1 + pulse(t, 1, 8) * (t > 4 ? 0.006 : 0);

  // confetti around the success card
  const conf = t >= T.done ? t - T.done : -1;

  return (
    <AbsoluteFill style={{background: t < 0 ? 'transparent' : C.ink, overflow: 'hidden'}}>
      <DirBlur id="prodWhip" x={whip * 70}>
        <AbsoluteFill style={{transform: `translateX(${-whip * 1300}px)`}}>
          {/* paper flood */}
          <div
            style={{
              position: 'absolute',
              left: logoBigCx - 1900 * flood,
              top: logoBigCy + logoBigSize / 2 - 1900 * flood,
              width: 3800 * flood,
              height: 3800 * flood,
              borderRadius: '50%',
              background: `radial-gradient(circle at 30% 20%, #FFFFFF 0%, ${C.paper} 38%, #E8E6E0 100%)`,
            }}
          />
          {flood >= 1 ? (
            <AbsoluteFill style={{background: `radial-gradient(circle at 20% 0%, #FFFFFF 0%, ${C.paper} 38%, #E8E6E0 100%)`}} />
          ) : null}

          {/* shockwave */}
          {landed && ring < 1 ? (
            <div
              style={{
                position: 'absolute',
                left: logoBigCx - 1000 * ring,
                top: logoBigCy + logoBigSize / 2 - 1000 * ring * 0.35,
                width: 2000 * ring,
                height: 700 * ring,
                borderRadius: '50%',
                border: `${26 * (1 - ring) + 1}px solid ${C.blue}`,
                opacity: 1 - ring,
              }}
            />
          ) : null}

          {/* particles */}
          {landed && t < 1.2
            ? [...Array(18)].map((_, i) => {
                const a = (i / 18) * Math.PI * 2 + rand(i) * 0.3;
                const sp_ = 380 + rand(i + 3) * 420;
                const k = tw(t, 0, 1.2, 0, 1, EXPO_OUT);
                const x = logoBigCx + Math.cos(a) * sp_ * k;
                const y = logoBigCy + logoBigSize / 2 + Math.sin(a) * sp_ * k * 0.45 - Math.sin(k * Math.PI) * 120 * rand(i + 9);
                const s = 10 + rand(i + 5) * 22;
                return (
                  <div
                    key={i}
                    style={{
                      position: 'absolute',
                      left: x - s / 2,
                      top: y - s / 2,
                      width: s,
                      height: s,
                      borderRadius: i % 3 === 0 ? 4 : s / 2,
                      background: i % 2 ? C.blue : C.ink,
                      opacity: 1 - k,
                      transform: `rotate(${k * 300}deg)`,
                    }}
                  />
                );
              })
            : null}

          {/* ── the app world, flown by a camera ── */}
          {t >= T.uiIn - 0.1 ? (
            <AbsoluteFill style={{perspective: 2600, perspectiveOrigin: `${CX}px ${camCy}px`}}>
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  top: 0,
                  transformOrigin: '0 0',
                  transform: `translate(${CX}px, ${camCy}px) rotateX(${cam.rx}deg) rotateY(${cam.ry}deg) rotateZ(${cam.rz}deg) scale(${cam.s * bump}) translate(${-cam.fx}px, ${-cam.fy}px)`,
                  transformStyle: 'preserve-3d',
                }}
              >
                <AppUI t={t} hideBrand={!brandInWorld} />
                {/* cursor lives in the world so it rides the camera */}
                {cursorOpacity > 0 ? (
                  <Cursor x={cur.x} y={cur.y} size={26} press={press} ripple={ripple} opacity={cursorOpacity} />
                ) : null}
                {/* success confetti */}
                {conf >= 0 && conf < 1.4
                  ? [...Array(22)].map((_, i) => {
                      const a = -Math.PI / 2 + (rand(i) - 0.5) * 2.4;
                      const v = 120 + rand(i + 1) * 220;
                      const k = conf;
                      const x = 60 + Math.cos(a) * v * k;
                      const y = 824 + Math.sin(a) * v * k + 260 * k * k;
                      return (
                        <div
                          key={i}
                          style={{
                            position: 'absolute',
                            left: x,
                            top: y,
                            width: 7,
                            height: i % 2 ? 7 : 12,
                            borderRadius: i % 3 ? 2 : 4,
                            background: [C.blue, C.green, '#FFB800', C.blueHi][i % 4],
                            opacity: 1 - k / 1.4,
                            transform: `rotate(${k * 500 + i * 40}deg)`,
                          }}
                        />
                      );
                    })
                  : null}
              </div>
            </AbsoluteFill>
          ) : null}

          {/* top fade so captions sit on clean paper */}
          {t >= 3.8 ? (
            <AbsoluteFill
              style={{
                background: `linear-gradient(180deg, ${C.paper} 0%, ${C.paper} 24%, rgba(241,240,236,0) 36%)`,
                opacity: tw(t, 3.8, 4.1, 0, 1),
              }}
            />
          ) : null}

          {/* ── the big logo + wordmark (screen space until they land in the header) ── */}
          {!brandInWorld && t >= -PRE_B ? (
            <>
              <div
                style={{
                  position: 'absolute',
                  left: logoCx - logoSize / 2,
                  top: logoCy - logoSize / 2,
                  transformOrigin: '50% 100%',
                  transform: `scale(${1 + squash - stretch * 0.6}, ${1 - squash + stretch})`,
                }}
              >
                <Logo size={logoSize} shine={tw(t, 0.4, 1.4, 0, 1, (x) => x)} glow={pulse(t, 1, 5) * (1 - mm)} />
              </div>
              <div
                style={{
                  position: 'absolute',
                  left: wordX,
                  top: wordY,
                  fontFamily: mono,
                  fontWeight: 700,
                  fontSize: wordFs,
                  letterSpacing: '-0.04em',
                  lineHeight: 1.1,
                  color: C.text,
                  whiteSpace: 'nowrap',
                }}
              >
                {'tubedrop'.split('').map((ch, i) => {
                  const at = 0.75 + i * 0.07;
                  const k = sp(t, at, {damping: 9, stiffness: 240, mass: 0.6});
                  return (
                    <span
                      key={i}
                      style={{
                        display: 'inline-block',
                        opacity: t >= at ? 1 : 0,
                        transform: `translateY(${(1 - k) * -260 * (1 - mm)}px)`,
                      }}
                    >
                      {ch}
                    </span>
                  );
                })}
              </div>
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  right: 0,
                  top: 990,
                  textAlign: 'center',
                  fontFamily: mono,
                  fontSize: 40,
                  color: C.muted,
                  opacity: 1 - tagOut,
                  transform: `translateY(${tagOut * 30}px)`,
                }}
              >
                <span style={{color: C.blue}}>{tagline.slice(0, Math.min(3, tagTyped))}</span>
                {tagline.slice(3, Math.max(3, tagTyped))}
                {tagTyped > 0 && tagTyped < tagline.length ? <span style={{color: C.blue}}>▍</span> : null}
              </div>
            </>
          ) : null}

          {/* captions */}
          {CAPTIONS.map((c) => {
            if (t < c.at - 0.05 || t > c.out + 0.4) return null;
            const p = tw(t, c.at, c.at + 0.4, 0, 1, STRONG_OUT);
            const q = tw(t, c.out, c.out + 0.3, 0, 1, EXPO_IN);
            return (
              <div key={c.num} style={{position: 'absolute', left: 64, right: 64, top: 128}}>
                <MaskLine p={p} q={q}>
                  <div style={{display: 'flex', alignItems: 'center', gap: 16, fontFamily: mono, fontWeight: 600, fontSize: 26, letterSpacing: '0.12em', color: C.subtle, marginBottom: 14}}>
                    <span style={{fontSize: 22, padding: '4px 10px', borderRadius: 8, background: 'rgba(15,15,20,0.06)', color: c.num === '✓' ? C.green : C.muted, letterSpacing: 0}}>{c.num}</span>
                    TUBEDROP
                  </div>
                </MaskLine>
                <MaskLine p={p} q={q}>
                  <div style={{fontFamily: display, fontWeight: 800, fontSize: 104, letterSpacing: '-0.05em', lineHeight: 1, color: C.text}}>{c.text}</div>
                </MaskLine>
              </div>
            );
          })}

          {/* ⌘V keycaps */}
          {t >= 4.7 && t < 5.75 ? (
            <div
              style={{
                position: 'absolute',
                left: 0,
                right: 0,
                top: 1010,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 26,
                transform: `scale(${keysIn * (1 - keysOut)})`,
                opacity: 1 - keysOut,
              }}
            >
              <Kbd size={150} press={keyPress}>
                ⌘
              </Kbd>
              <div style={{fontFamily: display, fontWeight: 800, fontSize: 70, color: C.subtle}}>+</div>
              <Kbd size={150} press={keyPress}>
                V
              </Kbd>
            </div>
          ) : null}

          {/* airplane-mode toast: the callback to the hook */}
          {t >= 13.5 ? (
            <div
              style={{
                position: 'absolute',
                left: 200,
                right: 48,
                top: 420,
                height: 120,
                borderRadius: 32,
                background: C.ink,
                display: 'flex',
                alignItems: 'center',
                padding: '0 30px',
                gap: 22,
                color: '#fff',
                transform: `translateX(${(1 - toastIn) * 900}px)`,
                boxShadow: '0 30px 60px -20px rgba(0,0,0,0.5)',
              }}
            >
              <div style={{width: 64, height: 64, borderRadius: 18, background: toggleOn > 0.5 ? C.orange : '#3A3A44', display: 'grid', placeItems: 'center'}}>
                <I.plane size={36} color="#fff" />
              </div>
              <div style={{flex: 1}}>
                <div style={{fontFamily: display, fontWeight: 700, fontSize: 34, letterSpacing: '-0.02em'}}>Airplane mode</div>
                <div style={{fontFamily: mono, fontSize: 22, color: '#9C9CA6'}}>3:12:47 ready offline</div>
              </div>
              <div style={{width: 110, height: 64, borderRadius: 32, background: toggleOn > 0.5 ? C.orange : '#3A3A44', position: 'relative'}}>
                <div style={{position: 'absolute', top: 5, left: 5 + toggleOn * 46, width: 54, height: 54, borderRadius: 27, background: '#fff'}} />
              </div>
            </div>
          ) : null}

          {/* impact flash */}
          {landed && flash > 0 ? <AbsoluteFill style={{background: '#fff', opacity: flash}} /> : null}
        </AbsoluteFill>
      </DirBlur>

      {/* sound */}
      <Sfx name="boom" at={PRE_B} volume={1} />
      <Sfx name="sparkle" at={PRE_B + 0.3} volume={0.4} />
      {'tubedrop'.split('').map((_, i) => (
        <Sfx key={i} name="pop" at={PRE_B + 0.75 + i * 0.07} volume={0.18} />
      ))}
      <Sfx name="type_short" at={PRE_B + 1.8} volume={0.25} />
      <Sfx name="whoosh" at={PRE_B + 3.0} volume={0.45} />
      {CLICKS.map((c) => (
        <Sfx key={c} name="click" at={PRE_B + c} volume={0.7} />
      ))}
      <Sfx name="keypress" at={PRE_B + T.paste} volume={0.7} />
      <Sfx name="pop" at={PRE_B + T.paste} volume={0.4} />
      <Sfx name="pop" at={PRE_B + T.preview} volume={0.35} />
      {[...Array(9)].map((_, i) => (
        <Sfx key={`c${i}`} name="tick" at={PRE_B + T.chips + i * 0.1} volume={0.3} />
      ))}
      <Sfx name="whoosh" at={PRE_B + 5.95} volume={0.25} />
      <Sfx name="whoosh" at={PRE_B + 7.6} volume={0.25} />
      <Sfx name="whoosh" at={PRE_B + 9.5} volume={0.25} />
      <Sfx name="progress" at={PRE_B + T.progress} volume={0.35} />
      <Sfx name="ding" at={PRE_B + T.done} volume={0.6} />
      <Sfx name="whoosh_long" at={PRE_B + 12} volume={0.35} />
      <Sfx name="toggle" at={PRE_B + 13.75} volume={0.6} />
      <Sfx name="whoosh" at={PRE_B + 15.5} volume={0.55} />
    </AbsoluteFill>
  );
};


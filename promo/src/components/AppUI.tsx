import React from 'react';
import {C} from '../config';
import {mono, sans} from '../fonts';
import {BACK_OUT, EXPO_OUT, STRONG_IN_OUT, clamp, rand, sp, tw} from '../anim';
import {I, Logo} from './common';

/*
 * A faithful re-build of tubedrop's real UI (ytconverter/web/ui.py), laid out
 * in "world" pixels (620px wide shell) so the camera can fly over it.
 * Everything is driven by `t` — the product scene's local beat clock.
 */

export const T = {
  uiIn: 3.25,
  click1: 4.65, // focus url
  paste: 5.0,
  fetch: 5.6,
  preview: 5.95,
  toAudio: 6.75,
  toVideo: 7.3,
  chips: 7.75,
  pick: 9.0,
  download: 10.0,
  progress: 10.2,
  progressEnd: 11.6,
  done: 11.7,
};

export const URL_TEXT = 'https://youtube.com/watch?v=3h-interview';

export const QUALITIES: [string, string][] = [
  ['best', 'auto'],
  ['144p', '~180 MB'],
  ['240p', '~310 MB'],
  ['360p', '~520 MB'],
  ['480p', '~0.9 GB'],
  ['720p', '~1.6 GB'],
  ['1080p', '~2.4 GB'],
  ['1440p', '~5.1 GB'],
  ['4K', '~9.8 GB'],
];
export const PICK_INDEX = 6;
export const CHIP_W = 106;
export const CHIP_GAP = 9;

const sectionLabel = (n: string, label: string) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: 9,
      fontFamily: mono,
      fontSize: 10.5,
      fontWeight: 600,
      letterSpacing: '0.12em',
      textTransform: 'uppercase',
      color: C.subtle,
      height: 16,
      marginBottom: 14,
    }}
  >
    <span style={{fontSize: 9.5, padding: '2px 5px', borderRadius: 5, background: 'rgba(15,15,20,0.05)', color: C.muted, letterSpacing: 0}}>{n}</span>
    {label}
  </div>
);

const Section: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div style={{padding: '20px 22px', borderTop: `1px solid ${C.border}`, ...style}}>{children}</div>
);

const Thumb: React.FC = () => (
  <svg width="168" height="94.5" viewBox="0 0 968 545" style={{display: 'block'}}>
    <defs>
      <linearGradient id="thumbBg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#3B2416" />
        <stop offset="1" stopColor="#0E0A09" />
      </linearGradient>
    </defs>
    <rect width="968" height="545" fill="url(#thumbBg)" />
    <circle cx="200" cy="120" r="260" fill="#FF9A4A" opacity="0.18" />
    <circle cx="800" cy="100" r="240" fill="#4A7BFF" opacity="0.16" />
    <path d="M150 545 C150 420 210 360 300 360 C390 360 450 420 450 545 Z" fill="#0B0807" />
    <circle cx="300" cy="275" r="78" fill="#0B0807" />
    <path d="M520 545 C520 430 580 372 668 372 C756 372 816 430 816 545 Z" fill="#0B0807" />
    <circle cx="668" cy="288" r="74" fill="#0B0807" />
    <rect x="388" y="330" width="44" height="92" rx="22" fill="#2A2A30" />
    <rect x="540" y="340" width="44" height="92" rx="22" fill="#2A2A30" />
  </svg>
);

export const AppUI: React.FC<{t: number; hideBrand?: boolean}> = ({t, hideBrand}) => {
  // assembly (staggered rise-in)
  const rise = (k: number) => {
    const p = tw(t, T.uiIn + k * 0.12, T.uiIn + 0.6 + k * 0.12, 0, 1, EXPO_OUT);
    return {opacity: p, transform: `translateY(${(1 - p) * 40}px)`};
  };

  // url field
  const focused = t >= T.click1;
  const pasted = t >= T.paste;
  const flash = tw(t, T.paste, T.paste + 0.5, 1, 0);
  const fetching = t >= T.fetch && t < T.preview;
  const fetchPress = t >= T.fetch ? tw(t, T.fetch, T.fetch + 0.15, 1, 0) : 0;

  // preview
  const pv = tw(t, T.preview, T.preview + 0.4, 0, 1, EXPO_OUT);

  // format segmented control: 0 = video, 1 = audio
  const seg =
    tw(t, T.toAudio, T.toAudio + 0.2, 0, 1, STRONG_IN_OUT) - tw(t, T.toVideo, T.toVideo + 0.2, 0, 1, STRONG_IN_OUT);
  const isAudio = seg > 0.5;

  // chips
  const chipIn = (i: number) => sp(t, T.chips + i * 0.1, {damping: 11, stiffness: 300, mass: 0.6});
  const picked = t >= T.pick;
  const pickPop = picked ? sp(t, T.pick, {damping: 9, stiffness: 320}) : 0;

  // download
  const ctaPress = t >= T.download ? tw(t, T.download, T.download + 0.18, 1, 0) : 0;
  const inProgress = t >= T.progress && t < T.done;
  const isDone = t >= T.done;
  const pct = tw(t, T.progress, T.progressEnd, 0, 100, STRONG_IN_OUT);
  const speed = 41 + Math.round(rand(Math.floor(t * 8)) * 110) / 10;
  const eta = Math.max(0, Math.round(52 * (1 - pct / 100)));
  const doneIn = tw(t, T.done, T.done + 0.35, 0, 1, EXPO_OUT);
  const checkPop = sp(t, T.done + 0.1, {damping: 9, stiffness: 260});

  return (
    <div style={{position: 'relative', width: 620, fontFamily: mono, color: C.text, fontSize: 13, lineHeight: 1.55}}>
      {/* ── header ── */}
      <div style={{position: 'relative', height: 52}}>
        <div style={{position: 'absolute', left: 4, top: 0, opacity: hideBrand ? 0 : 1}}>
          <Logo size={52} />
        </div>
        <div style={{position: 'absolute', left: 70, top: 3, opacity: hideBrand ? 0 : 1}}>
          <div style={{fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '-0.04em', lineHeight: 1.1}}>tubedrop</div>
        </div>
        <div style={{position: 'absolute', left: 70, top: 31, fontSize: 11.5, color: C.muted, letterSpacing: '0.01em', ...rise(0)}}>
          // drop a youtube link · keep it on your mac
        </div>
        <div style={{position: 'absolute', right: 4, top: 10, display: 'flex', gap: 8, ...rise(0)}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 7, padding: '6px 13px 6px 11px', background: '#fff', border: `1px solid ${C.borderStrong}`, borderRadius: 999, fontSize: 11.5, color: C.muted}}>
            <div style={{width: 7, height: 7, borderRadius: 4, background: C.green, boxShadow: '0 0 0 3px rgba(22,163,74,0.25)'}} />
            ready
          </div>
        </div>
      </div>

      {/* ── card ── */}
      <div
        style={{
          position: 'relative',
          marginTop: 18,
          background: '#fff',
          border: `1px solid ${C.border}`,
          borderRadius: 22,
          boxShadow: '0 1px 0 rgba(255,255,255,0.6) inset, 0 1px 2px rgba(15,15,20,0.04), 0 30px 60px -30px rgba(15,15,20,0.25)',
          overflow: 'hidden',
          ...rise(1),
        }}
      >
        {/* hero / drop zone */}
        <div style={{padding: 6}}>
          <div
            style={{
              borderRadius: 18,
              background: 'linear-gradient(180deg, #F2F5FB 0%, #FAFAF7 100%)',
              border: '1.5px dashed rgba(0,102,255,0.32)',
              padding: '22px 22px 18px',
            }}
          >
            <div style={{display: 'flex', alignItems: 'center', gap: 8, fontSize: 10.5, fontWeight: 600, letterSpacing: '0.12em', color: C.subtle, height: 16, marginBottom: 12}}>
              <I.link size={12} />
              YOUTUBE URL
              <div style={{flex: 1}} />
              <span style={{fontSize: 10, padding: '1px 6px', background: '#fff', border: `1px solid ${C.borderStrong}`, borderRadius: 6, color: C.muted, letterSpacing: 0, fontWeight: 500}}>⌘V</span>
              <span style={{letterSpacing: 0, fontWeight: 500, textTransform: 'none'}}>to paste</span>
            </div>
            <div style={{display: 'flex', gap: 10, height: 50}}>
              <div
                style={{
                  position: 'relative',
                  flex: 1,
                  borderRadius: 14,
                  background: pasted ? `rgba(0,102,255,${0.1 * flash})` : '#fff',
                  backgroundColor: '#fff',
                  border: `1px solid ${focused ? C.blue : C.borderStrong}`,
                  boxShadow: focused ? '0 0 0 4px rgba(0,102,255,0.10)' : '0 1px 2px rgba(15,15,20,0.04)',
                  display: 'flex',
                  alignItems: 'center',
                  paddingLeft: 44,
                  fontSize: 14,
                  overflow: 'hidden',
                  whiteSpace: 'nowrap',
                }}
              >
                <div style={{position: 'absolute', left: 16, top: 16, color: C.subtle}}>
                  <I.link size={18} />
                </div>
                {pasted ? (
                  <span style={{background: `rgba(0,102,255,${0.22 * flash})`, borderRadius: 4, color: C.text}}>{URL_TEXT}</span>
                ) : (
                  <span style={{color: C.subtle}}>
                    paste a link…
                    {focused && Math.floor(t * 4) % 2 === 0 ? <span style={{color: C.blue}}>|</span> : null}
                  </span>
                )}
              </div>
              <div
                style={{
                  width: 92,
                  borderRadius: 14,
                  background: '#fff',
                  border: `1px solid ${C.borderStrong}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 7,
                  fontSize: 13,
                  fontWeight: 600,
                  transform: `scale(${1 - fetchPress * 0.06})`,
                  boxShadow: '0 1px 2px rgba(15,15,20,0.04)',
                }}
              >
                <div style={{transform: `rotate(${fetching ? t * 720 : 0}deg)`}}>
                  <I.sparkle size={13} />
                </div>
                fetch
              </div>
            </div>
            <div style={{marginTop: 10, fontSize: 11, color: C.subtle, display: 'flex', alignItems: 'center', gap: 6, height: 17}}>
              <I.download size={12} /> or drop a link anywhere on this window
            </div>
          </div>
        </div>

        {/* preview */}
        <div style={{height: pv * 100.5, overflow: 'hidden'}}>
          <div
            style={{
              margin: '0 6px 6px',
              borderRadius: 16,
              background: C.paper2,
              border: `1px solid ${C.border}`,
              overflow: 'hidden',
              display: 'grid',
              gridTemplateColumns: '168px 1fr',
              opacity: pv,
              transform: `translateY(${(1 - pv) * 8}px)`,
            }}
          >
            <div style={{position: 'relative'}}>
              <Thumb />
              <div style={{position: 'absolute', right: 6, bottom: 6, background: 'rgba(0,0,0,0.78)', color: '#fff', fontSize: 10.5, fontWeight: 600, padding: '1px 6px', borderRadius: 5}}>3:12:47</div>
            </div>
            <div style={{padding: '16px 18px'}}>
              <div style={{fontFamily: sans, fontWeight: 600, fontSize: 15, letterSpacing: '-0.01em'}}>The 3-hour interview</div>
              <div style={{marginTop: 6, fontSize: 12, color: C.muted}}>
                <span style={{color: C.text}}>Long Talks</span> · 1.2M views
              </div>
              <div style={{marginTop: 8, display: 'inline-block', fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 5, background: 'rgba(255,0,51,0.10)', color: '#E0002B'}}>YOUTUBE</div>
            </div>
          </div>
        </div>

        {/* 01 format */}
        <Section style={rise(2)}>
          {sectionLabel('01', 'format')}
          <div style={{position: 'relative', height: 52, borderRadius: 14, background: 'rgba(15,15,20,0.04)', padding: 5, display: 'flex'}}>
            <div
              style={{
                position: 'absolute',
                top: 5,
                bottom: 5,
                left: 5 + seg * 283,
                width: 283,
                borderRadius: 10,
                background: '#fff',
                boxShadow: '0 1px 3px rgba(15,15,20,0.1), 0 4px 10px -4px rgba(15,15,20,0.1)',
              }}
            />
            {[
              {icon: <I.video size={16} />, label: 'video', tag: 'MP4', on: !isAudio},
              {icon: <I.music size={16} />, label: 'audio', tag: 'MP3', on: isAudio},
            ].map((o) => (
              <div key={o.label} style={{position: 'relative', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, fontSize: 15, fontWeight: 600, color: o.on ? C.text : C.muted}}>
                {o.icon}
                {o.label}
                <span style={{fontSize: 10.5, fontWeight: 600, padding: '2px 6px', borderRadius: 5, background: o.on ? C.blueSoft : 'rgba(15,15,20,0.05)', color: o.on ? C.blue : C.subtle}}>{o.tag}</span>
              </div>
            ))}
          </div>
        </Section>

        {/* 02 quality */}
        <Section style={rise(3)}>
          {sectionLabel('02', isAudio ? 'audio quality' : 'video quality')}
          <div style={{display: 'flex', flexWrap: 'wrap', gap: CHIP_GAP, height: 80}}>
            {QUALITIES.map(([q, size], i) => {
              const k = chipIn(i);
              const sel = picked && i === PICK_INDEX;
              return (
                <div
                  key={q}
                  style={{
                    width: CHIP_W,
                    height: 36,
                    borderRadius: 10,
                    border: `1px solid ${sel ? 'rgba(0,102,255,0.45)' : C.borderStrong}`,
                    background: sel ? 'rgba(0,102,255,0.10)' : '#fff',
                    boxShadow: sel ? '0 0 0 3px rgba(0,102,255,0.10)' : '0 1px 2px rgba(15,15,20,0.04)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                    fontSize: 13.5,
                    fontWeight: 600,
                    color: sel ? C.blue : C.text,
                    transform: `scale(${k * (sel ? 1 + (1 - pickPop) * 0.25 : 1)})`,
                    opacity: clamp(k * 1.5),
                  }}
                >
                  {q}
                  <span style={{fontSize: 10, fontWeight: 500, color: sel ? C.blue : C.subtle}}>{size}</span>
                </div>
              );
            })}
          </div>
        </Section>

        {/* 03 folder */}
        <Section style={rise(4)}>
          {sectionLabel('03', 'save to folder')}
          <div style={{display: 'flex', gap: 10, height: 46}}>
            <div style={{flex: 1, borderRadius: 13, border: `1px solid ${C.borderStrong}`, display: 'flex', alignItems: 'center', gap: 10, paddingLeft: 16, fontSize: 13.5}}>
              <I.folder size={16} color={C.subtle} /> ~/Downloads/tubedrop
            </div>
            <div style={{width: 104, borderRadius: 13, border: `1px solid ${C.borderStrong}`, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, fontWeight: 600, fontSize: 13.5}}>
              <I.folder size={15} /> browse
            </div>
          </div>
        </Section>

        {/* subtitles + CTA / progress / success */}
        <div style={{padding: '0 22px 22px', ...rise(5)}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '6px 0 18px'}}>
            <div style={{width: 40, height: 40, borderRadius: 11, background: 'rgba(15,15,20,0.04)', display: 'grid', placeItems: 'center'}}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={C.muted} strokeWidth="2" strokeLinecap="round">
                <rect x="3" y="5" width="18" height="14" rx="2.5" />
                <path d="M7 14h3M14 14h3M7 11h4M13 11h4" />
              </svg>
            </div>
            <div style={{flex: 1}}>
              <div style={{fontFamily: sans, fontWeight: 600, fontSize: 14.5}}>Download subtitles</div>
              <div style={{fontSize: 11.5, color: C.muted}}>russian · english · original language · .srt</div>
            </div>
            <div style={{width: 46, height: 28, borderRadius: 14, background: 'rgba(15,15,20,0.08)', position: 'relative'}}>
              <div style={{position: 'absolute', left: 3, top: 3, width: 22, height: 22, borderRadius: 11, background: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.2)'}} />
            </div>
          </div>

          {!inProgress && !isDone ? (
            <div
              style={{
                height: 54,
                borderRadius: 14,
                background: `linear-gradient(180deg, #2E7BFF 0%, ${C.blue} 45%, ${C.blueDeep} 100%)`,
                boxShadow: `inset 0 1px 0 rgba(255,255,255,0.3), 0 8px 24px -4px rgba(0,102,255,${0.45 + ctaPress * 0.3})`,
                display: 'flex',
                alignItems: 'center',
                padding: '0 20px',
                gap: 12,
                color: '#fff',
                fontSize: 15.5,
                fontWeight: 700,
                letterSpacing: '0.01em',
                transform: `scale(${1 - ctaPress * 0.035})`,
              }}
            >
              <I.download size={17} stroke={2.4} />
              download {isAudio ? 'audio' : 'video'}
              <span style={{marginLeft: 'auto', fontSize: 10.5, fontWeight: 600, padding: '3px 7px', background: 'rgba(255,255,255,0.18)', borderRadius: 6, letterSpacing: '0.06em'}}>{isAudio ? 'MP3' : 'MP4'}</span>
            </div>
          ) : null}

          {inProgress ? (
            <div style={{padding: 20, background: C.paper2, borderRadius: 16, border: `1px solid ${C.border}`}}>
              <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14}}>
                <div style={{display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: C.muted, fontWeight: 500}}>
                  <div style={{width: 12, height: 12, borderRadius: 6, border: '2px solid rgba(15,15,20,0.09)', borderTopColor: C.blue, transform: `rotate(${t * 900}deg)`}} />
                  downloading video · 1080p
                  <span style={{marginLeft: 6, fontSize: 9.5, fontWeight: 700, padding: '1px 5px', borderRadius: 4, background: 'rgba(15,15,20,0.06)', color: C.subtle}}>▶▶ ×40</span>
                </div>
                <div style={{fontSize: 22, fontWeight: 700, letterSpacing: '-0.02em', fontVariantNumeric: 'tabular-nums'}}>
                  {pct.toFixed(1)}
                  <span style={{fontSize: 13, color: C.muted, fontWeight: 500}}>%</span>
                </div>
              </div>
              <div style={{height: 8, borderRadius: 999, background: 'rgba(15,15,20,0.04)', overflow: 'hidden'}}>
                <div
                  style={{
                    width: `${pct}%`,
                    height: '100%',
                    borderRadius: 999,
                    background: `linear-gradient(90deg, ${C.blue}, #2E9F8A)`,
                    boxShadow: '0 0 12px rgba(0,102,255,0.5)',
                  }}
                />
              </div>
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginTop: 16}}>
                {[
                  ['size', '2.41 GB'],
                  ['speed', `${speed.toFixed(1)} MB/s`],
                  ['eta', `0:${String(eta).padStart(2, '0')}`],
                ].map(([k, v]) => (
                  <div key={k}>
                    <div style={{fontSize: 9.5, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', color: C.subtle}}>{k}</div>
                    <div style={{fontSize: 13.5, fontWeight: 600, marginTop: 3, fontVariantNumeric: 'tabular-nums'}}>{v}</div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {isDone ? (
            <div style={{padding: 20, background: C.paper2, borderRadius: 16, border: `1px solid ${C.border}`, opacity: doneIn, transform: `translateY(${(1 - doneIn) * 8}px)`}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14}}>
                <div style={{width: 36, height: 36, borderRadius: 12, background: '#DCFCE7', color: C.green, display: 'grid', placeItems: 'center', transform: `scale(${checkPop})`}}>
                  <I.check size={18} stroke={2.8} />
                </div>
                <div>
                  <div style={{fontFamily: sans, fontWeight: 700, fontSize: 15}}>Download complete</div>
                  <div style={{fontSize: 11.5, color: C.muted}}>1 file saved to your mac</div>
                </div>
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', background: '#fff', border: `1px solid ${C.border}`, borderRadius: 12}}>
                <div style={{width: 32, height: 32, borderRadius: 8, background: C.blueSoft, color: C.blue, display: 'grid', placeItems: 'center'}}>
                  <I.video size={15} />
                </div>
                <div style={{flex: 1}}>
                  <div style={{fontSize: 12, fontWeight: 500}}>The 3-hour interview.mp4</div>
                  <div style={{fontSize: 10.5, color: C.subtle}}>2.41 GB · 1080p · H.264</div>
                </div>
                <div style={{padding: '6px 12px', borderRadius: 8, border: `1px solid ${C.borderStrong}`, fontSize: 11, fontWeight: 600}}>show</div>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* footer */}
      <div style={{marginTop: 18, textAlign: 'center', fontSize: 11.5, color: C.subtle, ...rise(6)}}>
        <span style={{display: 'inline-flex', alignItems: 'center', gap: 6}}>
          <I.lock size={11} /> local server · files never leave your mac
        </span>
      </div>
    </div>
  );
};


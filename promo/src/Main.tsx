import React from 'react';
import {AbsoluteFill, Sequence, staticFile} from 'remotion';
import {Audio} from '@remotion/media';
import {C, FPS, MUSIC_FILE, MUSIC_OFFSET, SCENES, TOTAL_BEATS, f} from './config';
import {Grain} from './components/common';
import {Hook} from './scenes/Hook';
import {Scam} from './scenes/Scam';
import {Cli} from './scenes/Cli';
import {Vibe} from './scenes/Vibe';
import {Product, PRODUCT_PRE} from './scenes/Product';
import {Features} from './scenes/Features';
import {Outro} from './scenes/Outro';
import './fonts';

const Scene: React.FC<{range: readonly [number, number]; pre?: number; name: string; children: React.ReactNode}> = ({
  range,
  pre = 0,
  name,
  children,
}) => (
  <Sequence from={f(range[0] - pre)} durationInFrames={f(range[1]) - f(range[0] - pre)} name={name}>
    {children}
  </Sequence>
);

export const Main: React.FC = () => (
  <AbsoluteFill style={{background: C.ink}}>
    <Scene range={SCENES.hook} name="01 hook">
      <Hook />
    </Scene>
    <Scene range={SCENES.scam} name="02 scam">
      <Scam />
    </Scene>
    <Scene range={SCENES.cli} name="03 cli">
      <Cli />
    </Scene>
    <Scene range={SCENES.vibe} name="04 vibe">
      <Vibe />
    </Scene>
    <Scene range={SCENES.product} pre={PRODUCT_PRE} name="05 product">
      <Product />
    </Scene>
    <Scene range={SCENES.features} name="06 features">
      <Features />
    </Scene>
    <Scene range={SCENES.outro} name="07 outro">
      <Outro />
    </Scene>

    <Grain opacity={0.06} />

    <Audio
      src={staticFile(MUSIC_FILE)}
      trimBefore={Math.round(MUSIC_OFFSET * FPS)}
      volume={(fr) => {
        // short fade-out on the last beat so the loop point is clean
        const end = f(TOTAL_BEATS);
        return fr > end - 12 ? Math.max(0, (end - fr) / 12) * 0.7 : 0.7;
      }}
    />
  </AbsoluteFill>
);

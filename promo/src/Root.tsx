import React from 'react';
import {Composition} from 'remotion';
import {FPS, H, TOTAL_BEATS, W, f} from './config';
import {Main} from './Main';

export const RemotionRoot: React.FC = () => (
  <Composition id="TubedropPromo" component={Main} durationInFrames={f(TOTAL_BEATS)} fps={FPS} width={W} height={H} />
);

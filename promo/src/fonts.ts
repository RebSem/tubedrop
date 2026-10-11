import {loadFont as loadGeist} from '@remotion/google-fonts/Geist';
import {loadFont as loadGeistMono} from '@remotion/google-fonts/GeistMono';
import {loadFont as loadJetBrains} from '@remotion/google-fonts/JetBrainsMono';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadNewsreader} from '@remotion/google-fonts/Newsreader';

export const display = loadGeist('normal', {
  weights: ['500', '600', '700', '800', '900'],
  subsets: ['latin'],
}).fontFamily;

export const displayMono = loadGeistMono('normal', {
  weights: ['500', '700', '800'],
  subsets: ['latin'],
}).fontFamily;

export const mono = loadJetBrains('normal', {
  weights: ['400', '500', '600', '700', '800'],
  subsets: ['latin'],
}).fontFamily;

export const sans = loadInter('normal', {
  weights: ['500', '600', '700'],
  subsets: ['latin'],
}).fontFamily;

export const serif = loadNewsreader('italic', {
  weights: ['400', '500', '600'],
  subsets: ['latin'],
}).fontFamily;

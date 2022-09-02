#!/bin/bash

exec urxvt +sb -geometry 199x63+0+0 -title IRC -xrm 'URxvt.perl-ext-common:-confirm-paste' -xrm 'URxvt.keysym.Mod1-0: string:\0330' -xrm 'URxvt.keysym.Mod1-1: string:\0331' -xrm 'URxvt.keysym.Mod1-2: string:\0332' -xrm 'URxvt.keysym.Mod1-3: string:\0333' -xrm 'URxvt.keysym.Mod1-4: string:\0334' -xrm 'URxvt.keysym.Mod1-5: string:\0335' -xrm 'URxvt.keysym.Mod1-6: string:\0336' -xrm 'URxvt.keysym.Mod1-7: string:\0337' -xrm 'URxvt.keysym.Mod1-8: string:\0338' -xrm 'URxvt.keysym.Mod1-9: string:\0339' -xrm 'URxvt.keysym.Mod1-a: string:\033a' -xrm 'URxvt.keysym.Mod1-b: string:\033b' -xrm 'URxvt.keysym.Mod1-c: string:\033c' -xrm 'URxvt.keysym.Mod1-d: string:\033d' -xrm 'URxvt.keysym.Mod1-e: string:\033e' -xrm 'URxvt.keysym.Mod1-f: string:\033f' -xrm 'URxvt.keysym.Mod1-g: string:\033g' -xrm 'URxvt.keysym.Mod1-h: string:\033h' -xrm 'URxvt.keysym.Mod1-i: string:\033i' -xrm 'URxvt.keysym.Mod1-j: string:\033j' -xrm 'URxvt.keysym.Mod1-k: string:\033k' -xrm 'URxvt.keysym.Mod1-l: string:\033l' -xrm 'URxvt.keysym.Mod1-m: string:\033m' -xrm 'URxvt.keysym.Mod1-n: string:\033n' -xrm 'URxvt.keysym.Mod1-o: string:\033o' -xrm 'URxvt.keysym.Mod1-p: string:\033p' -xrm 'URxvt.keysym.Mod1-q: string:\033q' -xrm 'URxvt.keysym.Mod1-r: string:\033r' -xrm 'URxvt.keysym.Mod1-s: string:\033s' -xrm 'URxvt.keysym.Mod1-t: string:\033t' -xrm 'URxvt.keysym.Mod1-u: string:\033u' -xrm 'URxvt.keysym.Mod1-v: string:\033v' -xrm 'URxvt.keysym.Mod1-w: string:\033w' -xrm 'URxvt.keysym.Mod1-x: string:\033x' -xrm 'URxvt.keysym.Mod1-y: string:\033y' -xrm 'URxvt.keysym.Mod1-z: string:\033z'  -xrm 'URxvt.keysym.Mod1-Right: string:\033\033[C' -xrm 'URxvt.keysym.Mod1-Left: string:\033\033[D' -e ssh -t irc 'TERM=rxvt-256color tmux attach -d -t irc'

exit $?

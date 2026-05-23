import sys
sys.stdout.reconfigure(encoding='utf-8')

from tools.sff2_reader import read_style

path = r'données etude\YAMAHA (TYROS5)\Ballad\8BeatBallad1.T160.prs'
y = read_style(path)
total = sum(len(s.events) for s in y.sections)
print('sections:', len(y.sections), 'total events:', total)
for s in y.sections:
    print(f'  {s.name}: {len(s.events)} events')
print('cseg:', len(y.casm), 'groups')
for cseg in y.casm:
    print(f'  sections={cseg.sections}, channels={len(cseg.channels)}')

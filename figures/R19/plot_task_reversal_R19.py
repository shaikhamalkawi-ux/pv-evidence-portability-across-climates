#!/usr/bin/env python3
"""Redraw a two-panel task-portability figure from the frozen R16 derived ledger.

This is a deterministic display-only transformation. It neither recomputes
any PV measurements nor alters stopping decisions. It tests the locked
input hashes and the 184/12 correctness-gated counts before plotting.
"""
import csv
import hashlib
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SHA = '45060d415faa8ed84f5b1212a36893e2401913616031deddf73e244d43bb3c9d'

def make_plot(input_path: Path, output_path: Path) -> None:
    if hashlib.sha256(input_path.read_bytes()).hexdigest() != SHA:
        raise ValueError('Input is not the frozen R16 task ledger.')
    rows = list(csv.DictReader(input_path.open(newline='', encoding='utf-8')))
    if len(rows) != 190:
        raise ValueError(f'Expected 190 historical order runs, found {len(rows)}')
    eligible = []
    for row in rows:
        complete = (row['source_mean_pair_cells'] and row['local_mean_pair_cells']
                    and int(row['n_unresolved']) == 0)
        if not complete or row['source_winner_correct'] != 'True':
            continue
        x, y = float(row['pct_mean_pair_cells']), float(row['pct_winner_depth'])
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError('Nonfinite accepted values')
        eligible.append((x, y, (x > 0 > y or x < 0 < y), row['target_id'],row['source_order']))
    if len(eligible) != 184 or sum(a[2] for a in eligible) != 12:
        raise ValueError('Correctness gate or strict reversal count failed.')
    a = [p for p in eligible if not p[2]]
    b = [p for p in eligible if p[2]]
    if any(abs(x)>5 for x,y,*_ in b):
        raise ValueError('Reversal x-coordinate exceeded verified magnitude.')

    # Print friendly dual-panel figure with the SAME x/y records in both panels.
    plt.rcParams.update({'font.size': 10.4,'pdf.fonttype':42})
    fig,(ax,zoom)=plt.subplots(2,1,figsize=(7.25,8.0),layout='constrained')
    for a0 in [ax,zoom]:
        a0.axhline(0,color='0.45',lw=.9,zorder=1)
        a0.axvline(0,color='0.45',lw=.9,zorder=1)
        a0.scatter([p[0] for p in a],[p[1] for p in a],s=21,facecolor='#548bb8',edgecolor='white',linewidth=.35,alpha=.85,zorder=2)
        a0.scatter([p[0] for p in b],[p[1] for p in b],s=48,facecolor='white',edgecolor='#1b1b1b',linewidth=1.15,zorder=5)
        a0.grid(True,alpha=.13)
        a0.set_xlabel('Change in pairwise mean depth (%)')
    ax.set_xlim(-19,91); ax.set_ylim(-58,108)
    ax.set_ylabel('Change in winner-identification depth (%)')
    ax.set_title('(a) All 184 correct, complete runs',loc='left',fontweight='semibold')
    zoom.set_xlim(-6,6);zoom.set_ylim(-55,42)
    zoom.set_title('(b) Magnified region near zero mean change',loc='left',fontweight='semibold')
    handles=[Line2D([],[],marker='o',linestyle='',markersize=5,markerfacecolor='#548bb8',markeredgecolor='white',label='No strict reversal'),
             Line2D([],[],marker='o',linestyle='',markersize=7,markerfacecolor='white',markeredgecolor='#1b1b1b',label='Strict task reversal (12 runs)')]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,-.012),ncol=2,frameon=False)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output_path,bbox_inches='tight',pad_inches=.16)
    plt.close(fig)
    print('PASS: 184 correct/complete historical runs; 12 strict task reversals; figure produced.')

if __name__ == '__main__':
    if len(sys.argv)!=3:
        raise SystemExit('usage: python plot_task_reversal_R19.py INPUT_R16.csv OUTPUT.pdf')
    make_plot(Path(sys.argv[1]),Path(sys.argv[2]))

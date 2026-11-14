#!/usr/bin/env python3
"""Deterministic figures for Project 66 fuzzy preference sensitivity. Not raw PV data."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
with (P/'StageA_Fuzzy_AlphaCut_Summary.csv').open() as f:r=[x for x in csv.DictReader(f) if x['mode']=='1']
r.sort(key=lambda x:float(x['alpha']))
a=[float(x['alpha']) for x in r]
fig,ax=plt.subplots(figsize=(8.2,4.4))
for col,name,marker in [
 ('necessarily_better','Better throughout α-cut','o'),
 ('necessarily_worse','Worse throughout α-cut','s'),
 ('both_signs_possible','Both outcomes possible','^'),
 ('exact_tie','Exact modal tie','x')]:
 y=[int(x[col]) for x in r]
 ax.plot(a,y,label=name,marker=marker,linewidth=1.6)
ax.set(xlabel='α level (narrower preference core at higher α)',ylabel='Number of replay cases',
 title='Stage A: preference robustness of 79 mean-improving replays')
ax.set_xticks(a)
ax.set_ylim(0,51)
ax.legend(fontsize=9,loc='center left',bbox_to_anchor=(1.02,.5))
ax.grid(True,alpha=.2)
fig.text(.11,.015,'Illustrative triangular weight (0.05, 1, 10); weights not elicited from a laboratory.',fontsize=8)
fig.tight_layout(rect=(0,.045,1,1))
fig.savefig(P/'Figure_A_AlphaCut_CampaignRobustness.pdf',bbox_inches='tight')
fig.savefig(P/'Figure_A_AlphaCut_CampaignRobustness.png',dpi=180,bbox_inches='tight')
plt.close(fig)
with (P/'StageB_q_Exact_Count_Segments.csv').open() as f:s=list(csv.DictReader(f))
xs=[float(s[0]['q_from_pct'])]+[float(x['q_to_pct']) for x in s]
ys=[int(x['false_exclusion_count']) for x in s]+[int(s[-1]['false_exclusion_count'])]
fig,ax=plt.subplots(figsize=(8.3,4.2))
ax.step(xs,ys,where='post',linewidth=2.2,label='Nominal source-to-target false exclusions')
ax.axvline(5,linestyle='--',linewidth=1,label='Reference q = 5%')
for x in xs[1:-1]:ax.axvline(x,linestyle=':',linewidth=.8,alpha=.5)
ax.set(xlim=(4.5,5.5),ylim=(1.6,4.4),xlabel='Decision-resolution threshold q (percentage points)',
       ylabel='Number of nominal false exclusions',title='Stage B: exact shortlist threshold transitions')
ax.set_yticks([2,3,4]);ax.grid(True,alpha=.15)
ax.legend(loc='upper left',fontsize=9)
fig.text(.11,.01,'Fixed published yields for 11 modules; changing q is a preference sensitivity, not yield uncertainty.',fontsize=8)
fig.tight_layout(rect=(0,.04,1,1))
fig.savefig(P/'Figure_B_FuzzyShortlistThresholds.pdf',bbox_inches='tight')
fig.savefig(P/'Figure_B_FuzzyShortlistThresholds.png',dpi=180,bbox_inches='tight')
plt.close(fig)
print('PASS: independent single-plot figures written')

#!/usr/bin/env python3
"""Display-only plot of graph-based exact decomposition from archived pair decisions."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
d=pd.read_csv(P/'Graph_12ValidReversals.csv')
assert len(d)==12 and len(set(d.target_id))==11
fig,ax=plt.subplots(figsize=(9.2,6.3))
a=d[(d.delta_mean>0)&(d.delta_Kwin<0)];b=d[(d.delta_mean<0)&(d.delta_Kwin>0)]
assert (len(a),len(b))==(9,3)
ax.scatter(a.delta_star_edge_sum,a.delta_other_edge_sum,marker='o',s=95,facecolors='none',edgecolors='#235fa2',lw=1.6,label='Mean worse / winner earlier (9)')
ax.scatter(b.delta_star_edge_sum,b.delta_other_edge_sum,marker='s',s=76,facecolors='#a64740',edgecolors='#a64740',label='Mean better / winner later (3)')
ax.axhline(0,color='0.5',lw=.9);ax.axvline(0,color='0.5',lw=.9)
# total stopped-pair depth sum = x+y, so mean changes sign across this diagonal
left,right=-12,8
ax.plot([left,right],[-left,-right],'--',color='0.55',lw=.8,label='No change in overall pair mean')
# annotations selected, avoid data/value changes
ann={("D24_Trieste_inv1_tpan","Cocoa"):('Italy / Cocoa',(-20,7)),
     ("D09_PS_034","Albuquerque"):('Brazil PS034 / Albuquerque',(8,2)),
     ("D09_PS_006","Albuquerque"):('PS006 / Albuquerque',(6,-8)),
     ("2019_System_2B","Eugene"):('Germany 2019 / Eugene',(8,-8)),
     ("D09_PS_043","Golden"):('PS043 / Golden',(-110,-6))}
for r in d.itertuples():
 k=(r.target_id,r.source_order)
 if k in ann:
  tx,(ox,oy)=ann[k]
  ax.annotate(tx,(r.delta_star_edge_sum,r.delta_other_edge_sum),xytext=(ox,oy),textcoords='offset points',fontsize=8,arrowprops=dict(arrowstyle='-',lw=.45,color='.55') if abs(ox)>20 else None)
ax.set(xlabel='Change in sum of 8 winner-star pair depths (cells)',ylabel='Change in sum of 28 non-winner pair depths (cells)',title='Graph decomposition of the 12 retrospectively valid task reversals')
ax.set_xlim(-12,8.5);ax.set_ylim(-19,27)
ax.legend(loc='upper right',fontsize=8.4)
ax.grid(alpha=.13)
fig.text(.12,.01,'Source minus target-local. Derived pair-depth records; no new PV measurements or independent site replications.',fontsize=8)
fig.tight_layout(rect=[0,.035,1,1])
fig.savefig(P/'Figure_Graph12_StarVsOther.pdf',bbox_inches='tight',pad_inches=.15)
fig.savefig(P/'Figure_Graph12_StarVsOther.png',dpi=180,bbox_inches='tight',pad_inches=.15)
plt.close(fig)
print('PASS chart from exact 12-case original decisions')

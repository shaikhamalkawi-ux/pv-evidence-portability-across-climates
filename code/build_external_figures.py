"""Deterministic journal figures from individually archived output CSVs."""
from pathlib import Path
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype']=42  # TrueType embedding; avoids Type 3 PDF fonts
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent.parent;R=OUT/'results';ART=OUT/'r4_candidate';ART.mkdir(exist_ok=True)
D=pd.read_csv(R/'external_source_order_replay.csv')
orders=['Cocoa','Eugene','Golden','Switzerland','Albuquerque']
labels=['Cocoa','Eugene','Golden','Switzerland','Albuquerque']
# Each Brazilian plant receives one descriptive data point per source. Missing = unresolved.
b=D[(D.source_dataset=='D09_Brazil') & (D.source_order.isin(orders)) & (~D.is_repeated_sensitivity)]
vals=[b.loc[b.source_order==o,'directional_excess_pct_all_resolved_only'].dropna().to_numpy(float) for o in orders]
fig,ax=plt.subplots(figsize=(7.75,3.65))
ax.axhline(0,linestyle='--',linewidth=.9,color='0.45',zorder=0)
box=ax.boxplot(vals,tick_labels=labels,whis=[5,95],showfliers=True,vert=True,patch_artist=True,widths=.60)
for p in box['boxes']:p.set_facecolor('0.89');p.set_edgecolor('0.25')
for k in ['medians','whiskers','caps']:
 for p in box[k]:p.set_color('0.18');p.set_linewidth(1)
for i,v in enumerate(vals):
 ax.text(i+1,89,'n='+str(len(v)),fontsize=8,ha='center',color='0.3')
ax.set_ylim(-18,96);ax.set_ylabel('Excess characterization depth (%)',fontsize=10)
ax.set_title('Brazil: five fixed R3 source orders applied to distinct plant G–T series',fontsize=10,pad=9)
ax.grid(axis='y',alpha=.2)
fig.text(.5,.018,'Each plant: one value; Eugene excludes two plant cases with unresolved comparisons.',ha='center',fontsize=7.2,color='0.35')
fig.subplots_adjust(left=.11,right=.99,top=.88,bottom=.245)
fig.savefig(ART/'fig_brazil_external_source_excess.pdf',dpi=220)
fig.savefig(ART/'fig_brazil_external_source_excess.png',dpi=220)
plt.close(fig)
# Repeated-quarter categorical picture with all top-source ties as normalized letters.
q=pd.read_csv(R/'Brazil_quarter_best_source_sets.csv')
plants=pd.read_csv(R/'Brazil_within_plant_quarter_source_choice_stability.csv')
q=q[q.parent_site.isin(plants.site)]
quarters=sorted(q.quarter.unique());names=sorted(plants.site)
short={'Cocoa':'C','Eugene':'E','Golden':'G','Switzerland':'S','Albuquerque':'A'}
fig,ax=plt.subplots(figsize=(7.5,7.3))
ax.set_xlim(-.5,len(quarters)-.5);ax.set_ylim(len(names)-.5,-.5)
for i,n in enumerate(names):
 for j,qt in enumerate(quarters):
  selected=q[(q.parent_site==n)&(q.quarter==qt)]
  if selected.empty: continue
  val=selected.best_order_set.iloc[0]
  typ=len(val.split('|'))
  ax.add_patch(plt.Rectangle((j-.48,i-.45),.96,.9,fill=True,facecolor='0.91' if i%2 else '0.96',edgecolor='0.8',lw=.25))
  ax.text(j,i,'/'.join(short[x] for x in val.split('|')),ha='center',va='center',fontsize=6.8,weight='normal')
ax.set_xticks(range(len(quarters)),quarters,fontsize=8)
ax.set_yticks(range(len(names)),names,fontsize=7)
ax.tick_params(axis='both',length=0)
ax.xaxis.tick_top();ax.set_title('Best historical source order by Brazilian plant and eligible calendar quarter',pad=36,fontsize=10)
fig.text(.53,.016,'A=Albuquerque  C=Cocoa  E=Eugene  G=Golden  S=Switzerland; slash denotes tied minima',ha='center',fontsize=7.2)
for spine in ax.spines.values():spine.set_visible(False)
fig.subplots_adjust(left=.175,right=.98,bottom=.068,top=.865)
fig.savefig(ART/'fig_brazil_quarter_source_choice.pdf',dpi=200)
fig.savefig(ART/'fig_brazil_quarter_source_choice.png',dpi=200)
plt.close(fig)
print('Figures saved')

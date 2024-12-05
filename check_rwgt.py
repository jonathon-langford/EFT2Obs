#from coffea import nanoevents
from scripts.standalone_reweight import *
import pandas as pd
import numpy as np

rw = StandaloneReweight('rw_ttH_SMEFTsim_topU3l_test')

# Number of events to process
#N = 50000

# Constants
alphas = 0.137
use_helicity = False

# Load events
df = pd.read_csv("/eos/user/j/jlangfor/icrf/msci/Dec24/tth_data_replace_gg.csv")
df['h_pt'] = (df['h_px']**2 + df['h_py']**2)**0.5

# Mask: drop gq-initiated events
#mask = df['is_qg_initial']==0
#df = df[mask] #[:N] 

W_T = []
h_pt = []
genw = []
run, event, lumi = [], [], []
N_events = len(df)


for ir,r in df.iterrows():
#for ir,r in df[:10000].iterrows():

    if ir % 10000 == 0:
        print(f" --> Processed ({ir}/{N_events}) events")

    parts = [
        [r['i1_E'], r['i1_px'], r['i1_py'], r['i1_pz']],
        [r['i2_E'], r['i2_px'], r['i2_py'], r['i2_pz']],
        [r['h_E'], r['h_px'], r['h_py'], r['h_pz']],
        [r['t1_E'], r['t1_px'], r['t1_py'], r['t1_pz']],
        [r['t2_E'], r['t2_px'], r['t2_py'], r['t2_pz']]
    ]

    pdgs = [r['i1_id'], r['i2_id'], r['h_id'], r['t1_id'], r['t2_id']]
    hel = [r['i1_spin'], r['i2_spin'], r['h_spin'], r['t1_spin'], r['t2_spin']]
    status = [-1, -1, 1, 1, 1]

    w = rw.ComputeWeights(parts, pdgs, hel, status, alphas, use_helicity)
    w_t = rw.TransformWeights(w)
    W_T.append(w_t)

    h_pt.append(r['h_pt'])
    genw.append(r['gen_weight'])
    event.append(r['event_id'])
    run.append(r['run_id'])
    lumi.append(r['lumi_block_id'])

    #if sum(w) != 10:
    #    W.append(w)
    #
    #    # Transform weights
    #    w_t = rw.TransformWeights(w)
    #    W_T.append(w_t)
    #    h_pt.append(r['h_pt'])
    #    genw.append(r['gen_weight'])
    #else:
    #    print(" --> Dropping event")

    # Match event IDs to selected events

    # Append to processed dataframe

W_T = np.array(W_T)
h_pt = np.array(h_pt)
genw = np.array(genw)
event = np.array(event)
run = np.array(run)
lumi = np.array(lumi)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Load events
tth = pd.read_parquet("/eos/cms/store/group/phys_higgs/cmshgg/Run3HggSTXS_working/Run3HggSTXS_truth/processed/ttH_processed_selected.parquet")

c = {}
c['nan'] = 0
c['notfound'] = 0
c['found'] = 0

W = []

for ir, r in tth.iterrows():
    event_id = r['event_sel']
    if event_id != event_id:
        w = [-999]*9
        c['nan'] += 1
    else:
        if len(np.where(event==event_id)[0]) == 0:
            # Could not find ID
            w = [-999]*9
            c['notfound'] += 1
        else:
            w = W_T[np.where(event==event_id)[0][0]][1:]
            c['found'] += 1
    W.append(w)

columns = ['a_cg', 'b_cg_cg', 'a_chg', 'b_chg_chg', 'a_ctgre', 'b_ctgre_ctgre', 'b_cg_chg', 'b_cg_ctgre', 'b_chg_ctgre']

tth_weights = pd.DataFrame(W, columns=columns)

tth_with_weights = pd.concat([tth,tth_weights], axis=1)

tth_with_weights.to_parquet("/eos/user/j/jlangfor/icrf/msci/Dec24/ttH_processed_selected_with_smeft.parquet")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Apply masks for different pT regions and print A,B terms
def extract_AB(genw, reweights, name="ADD-NAME-HERE"):
    res = {}
    res['a_cg'], res['b_cg_cg'] = (reweights[:,1]*genw).sum()/genw.sum(), (reweights[:,2]*genw).sum()/genw.sum()
    res['a_chg'], res['b_chg_chg'] = (reweights[:,3]*genw).sum()/genw.sum(), (reweights[:,4]*genw).sum()/genw.sum()
    res['a_ctgre'], res['b_ctgre_ctgre'] = (reweights[:,5]*genw).sum()/genw.sum(), (reweights[:,6]*genw).sum()/genw.sum()
    res['b_cg_chg'] = (reweights[:,7]*genw).sum()/genw.sum()
    res['b_cg_ctgre'] = (reweights[:,8]*genw).sum()/genw.sum()
    res['b_chg_ctgre'] = (reweights[:,9]*genw).sum()/genw.sum()
    return res

# Inclusive
res = {}
res['TTH'] = extract_AB(genw, W_T, name="ttH, inclusive")

# pT 0-60
mask = h_pt < 60
res['TTH_PTH_0_60'] = extract_AB(genw[mask], W_T[mask], name="ttH, 0-60")

# pT 60-120
mask = (h_pt >= 60)&(h_pt < 120)
res['TTH_PTH_60_120'] = extract_AB(genw[mask], W_T[mask], name="ttH, 60-120")

# pT 120-200
mask = (h_pt >= 120)&(h_pt < 200)
res['TTH_PTH_120_200'] = extract_AB(genw[mask], W_T[mask], name="ttH, 120-200")

# pT 200-300
mask = (h_pt >= 200)&(h_pt < 300)
res['TTH_PTH_200_300'] = extract_AB(genw[mask], W_T[mask], name="ttH, 200-300")

# pT >300
mask = (h_pt >= 300)
res['TTH_PTH_GT300'] = extract_AB(genw[mask], W_T[mask], name="ttH, >300")

# Make dummy json
stxs_data = {}
stxs_data["metadata"] = {}
stxs_data["metadata"]['observable_names'] = ['TTH', 'TTH_PTH_0_60', 'TTH_PTH_60_120', 'TTH_PTH_120_200', 'TTH_PTH_200_300', 'TTH_PTH_GT300']

stxs_data["data"] = {}
stxs_data["data"]["central"] = {}
for k in res['TTH'].keys():
    stxs_data["data"]["central"][k] = []
    for obs in res.keys():
        stxs_data["data"]["central"][k].append(res[obs][k])

import json
with open("/eos/user/j/jlangfor/icrf/msci/Dec24/TTH_standalone.json", "w") as jf:
    json.dump(stxs_data, jf, indent=4)

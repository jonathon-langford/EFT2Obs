from coffea import nanoevents
import pandas as pd
import numpy as np
import awkward as ak

# Extract LHE information for ttH events
f_name = "root://xrootd-cms.infn.it//store/mc/Run3Summer22NanoAODv13/ttHtoGG_M-125_TuneCP5_13p6TeV_amcatnloFXFX-madspin-pythia8/NANOAODSIM/133X_mcRun3_2022_realistic_ForNanov13_v1-v1/80000/2705c80b-a8fc-440f-9777-2c9a9c805126.root"
events = nanoevents.NanoEventsFactory.from_root(f_name).events()

LHEPart = events.LHEPart
# Event info
event_id = events.event
run_id = events.run
lumi_block_id = events.luminosityBlock
gen_weight = events.genWeight

# Define incoming particles and higgs
i1 = LHEPart[:,0]
i2 = LHEPart[:,1]
h = LHEPart[:,2]

# Build top from b-W pairs
t1 = LHEPart[:,3]+LHEPart[:,4]
t2 = LHEPart[:,7]+LHEPart[:,8]


N_events = len(LHEPart)
#N_events = 50000

columns = ["event_id", "run_id", "lumi_block_id", "gen_weight",
    "i1_E", "i1_px", "i1_py", "i1_pz",
    "i2_E", "i2_px", "i2_py", "i2_pz",
    "h_E", "h_px", "h_py", "h_pz",
    "t1_E", "t1_px", "t1_py", "t1_pz",
    "t2_E", "t2_px", "t2_py", "t2_pz",
    "i1_id", "i2_id", "h_id", "t1_id", "t2_id",
    "i1_spin", "i2_spin", "h_spin", "t1_spin", "t2_spin",
    "is_qg_initial"
]

df = pd.DataFrame(columns=columns)

debug_ids = []

for ev in range(N_events):

    if ev % 10000 == 0:
        print(f" --> Processed ({ev}/{N_events}) events")
    
    # Check if we have incoming partons of gluon + quark
    if abs(i1[ev].pdgId) != abs(i2[ev].pdgId):
        i1_pdgId, i2_pdgId = 21, 21

    # Or if two incoming partons are qq or qbarqbar
    elif (i1[ev].pdgId) == (i2[ev].pdgId):
        i1_pdgId, i2_pdgId = 21, 21

    else:
        i1_pdgId, i2_pdgId = i1[ev].pdgId, i2[ev].pdgId

    ev_info = [event_id[ev], run_id[ev], lumi_block_id[ev], gen_weight[ev],
        abs(i1[ev].incomingpz), 0, 0, i1[ev].incomingpz,
        abs(i2[ev].incomingpz), 0, 0, i2[ev].incomingpz,
        h[ev].energy, h[ev].px, h[ev].py, h[ev].pz,
        t1[ev].energy, t1[ev].px, t1[ev].py, t1[ev].pz,
        t2[ev].energy, t2[ev].px, t2[ev].py, t2[ev].pz,
        i1_pdgId, i2_pdgId, h[ev].pdgId, 6, -6,
        i1[ev].spin, i2[ev].spin, h[ev].spin, -1, 1,
        0
    ]

    # Add event to dataframe
    df.loc[ev] = ev_info

df.to_csv("/eos/user/j/jlangfor/icrf/msci/Dec24/tth_data_replace_gg.csv")

#for ev in range(N_events):
#
#    if ev % 10000 == 0:
#        print(f" --> Processed ({ev}/{N_events}) events")
#    
#    # Check if we have incoming partons of gluon + quark
#    if abs(i1[ev].pdgId) != abs(i2[ev].pdgId):
#        # Take ISR quark line from particle 11
#        isr_q = LHEPart[ev][11]
#        # Find gluon four momentum by subtracting radiated quark line from incoming quark
#        if isr_q.pdgId == i1[ev].pdgId:
#            i1_glu = i1[ev]-isr_q
#            debug_ids.append(i2[ev].pdgId)
#            ev_info = [event_id[ev], run_id[ev], lumi_block_id[ev], gen_weight[ev],
#                abs(i1_glu.energy), i1_glu.px, i1_glu.py, i1_glu.pz,
#                abs(i2[ev].incomingpz), 0, 0, i2[ev].incomingpz,
#                h[ev].energy, h[ev].px, h[ev].py, h[ev].pz,
#                t1[ev].energy, t1[ev].px, t1[ev].py, t1[ev].pz,
#                t2[ev].energy, t2[ev].px, t2[ev].py, t2[ev].pz,
#                21, i2[ev].pdgId, h[ev].pdgId, 6, -6,
#                i1[ev].spin, i2[ev].spin, h[ev].spin, -1, 1,
#                1
#            ]
#
#        else:
#            i2_glu = i2[ev]-isr_q
#            debug_ids.append(i1[ev].pdgId)
#            ev_info = [event_id[ev], run_id[ev], lumi_block_id[ev], gen_weight[ev],
#                abs(i1[ev].incomingpz), 0, 0, i1[ev].incomingpz,
#                abs(i2_glu.energy), i2_glu.px, i2_glu.py, i2_glu.pz,
#                h[ev].energy, h[ev].px, h[ev].py, h[ev].pz,
#                t1[ev].energy, t1[ev].px, t1[ev].py, t1[ev].pz,
#                t2[ev].energy, t2[ev].px, t2[ev].py, t2[ev].pz,
#                i1[ev].pdgId, 21, h[ev].pdgId, 6, -6,
#                i1[ev].spin, i2[ev].spin, h[ev].spin, -1, 1,
#                1
#            ]
#
#    # For qq, gg channels
#    else:
#        ev_info = [event_id[ev], run_id[ev], lumi_block_id[ev], gen_weight[ev],
#            abs(i1[ev].incomingpz), 0, 0, i1[ev].incomingpz,
#            abs(i2[ev].incomingpz), 0, 0, i2[ev].incomingpz,
#            h[ev].energy, h[ev].px, h[ev].py, h[ev].pz,
#            t1[ev].energy, t1[ev].px, t1[ev].py, t1[ev].pz,
#            t2[ev].energy, t2[ev].px, t2[ev].py, t2[ev].pz,
#            i1[ev].pdgId, i2[ev].pdgId, h[ev].pdgId, 6, -6,
#            i1[ev].spin, i2[ev].spin, h[ev].spin, -1, 1,
#            0
#        ]
#
#    # Add event to dataframe
#    df.loc[ev] = ev_info
#
#df.to_csv("/eos/user/j/jlangfor/icrf/msci/Dec24/tth_data_v2.csv")

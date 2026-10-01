"""Leakage-aware LSTM/Transformer forecasting interfaces."""
from __future__ import annotations
import numpy as np
import pandas as pd

def walk_forward_splits(frame, time_column="date", train_size=0.7, test_size=0.1):
    d=frame.sort_values(time_column).reset_index(drop=True)
    n=len(d); train_end=max(1,int(n*train_size)); test=max(1,int(n*test_size))
    while train_end+test<=n:
        yield d.iloc[:train_end], d.iloc[train_end:train_end+test]
        train_end+=test

def sequence_windows(values, lookback=20, horizon=1):
    a=np.asarray(values,dtype=float); X=[]; y=[]
    for i in range(lookback,len(a)-horizon+1):
        X.append(a[i-lookback:i]); y.append(a[i:i+horizon])
    return np.asarray(X),np.asarray(y)

def forecasting_contract(model_family="LSTM"):
    return {"model_family":model_family,"feature_source":"350-metric feature store","validation":"walk-forward","leakage_controls":["chronological split","point-in-time features","training-window transforms"]}

def build_pytorch_model(input_size, hidden_size=64, layers=2, model_family="LSTM"):
    import torch.nn as nn
    if model_family.upper()=="LSTM": return nn.LSTM(input_size,hidden_size,layers,batch_first=True)
    if model_family.upper()=="GRU": return nn.GRU(input_size,hidden_size,layers,batch_first=True)
    if model_family.upper()=="TRANSFORMER":
        enc=nn.TransformerEncoderLayer(d_model=hidden_size,nhead=4,batch_first=True)
        return nn.TransformerEncoder(enc,num_layers=layers)
    raise ValueError("Unsupported sequence model")

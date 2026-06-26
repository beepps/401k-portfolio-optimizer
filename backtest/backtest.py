import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

base = '/home/user/workspace/finance_data/'

# SHV expired - use BIL for both money market and short-term bond proxies
proxy_files = {
    'EFA': 'EFA.csv', 'IWB': 'IWB.csv', 'IWM': 'IWM.csv',
    'ACWX': 'ACWX.csv', 'SPY': 'SPY.csv', 'VNQ': 'VNQ.csv',
    'SPMD': 'SPMD.csv', 'AGG': 'AGG.csv', 'BIL': 'BIL.csv'
}

dfs = {}
for sym, fname in proxy_files.items():
    df = pd.read_csv(base + fname)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    dfs[sym] = df['close']

prices = pd.DataFrame(dfs).dropna()
print(f"Date range: {prices.index[0].date()} to {prices.index[-1].date()}, Months: {len(prices)}")

monthly_returns = prices.pct_change().dropna()
fund_list = list(prices.columns)  # 9 funds
print(f"Funds: {fund_list}, Months: {len(monthly_returns)}")

# ─── Individual fund stats ─────────────────────────────────────────────────────
stats = {}
for sym in fund_list:
    ret = monthly_returns[sym]
    n = len(ret)
    ann_ret = (1 + ret).prod() ** (12/n) - 1
    ann_vol = ret.std() * np.sqrt(12)
    sharpe  = (ann_ret - 0.02) / ann_vol if ann_vol > 0 else 0
    cum_ret = (1 + ret).prod() - 1
    cc = (1+ret).cumprod()
    max_dd = (cc / cc.cummax() - 1).min()
    stats[sym] = {
        'ann_return': round(ann_ret*100,2), 'ann_vol': round(ann_vol*100,2),
        'sharpe': round(sharpe,3), 'cum_return': round(cum_ret*100,2),
        'max_drawdown': round(max_dd*100,2)
    }
    print(f"  {sym}: Ann={stats[sym]['ann_return']}% Vol={stats[sym]['ann_vol']}% Sharpe={stats[sym]['sharpe']} CumRet={stats[sym]['cum_return']}% MaxDD={stats[sym]['max_drawdown']}%")

# ─── Generate 250 Blends ──────────────────────────────────────────────────────
# fund_list: EFA=0, IWB=1, IWM=2, ACWX=3, SPY=4, VNQ=5, SPMD=6, AGG=7, BIL=8
np.random.seed(42)
blends = []

# Aggressive growth
for intl in [0.05, 0.10, 0.15, 0.20, 0.25]:
    for bond in [0.00, 0.05, 0.10]:
        for real in [0.00, 0.05]:
            eq = max(0, 1 - intl - bond - real)
            if eq < 0.50: continue
            for spy_s in [0.40, 0.50, 0.55]:
                for iwb_s in [0.25, 0.30]:
                    spmd_s = max(0, 1 - spy_s - iwb_s - 0.20)
                    w = np.zeros(9)
                    w[0] = intl * 0.60; w[3] = intl * 0.40
                    w[4] = eq * spy_s; w[1] = eq * iwb_s
                    w[2] = eq * 0.20; w[6] = eq * spmd_s
                    w[5] = real; w[7] = bond * 0.80; w[8] = bond * 0.20
                    w = np.maximum(w, 0)
                    if abs(w.sum() - 1) > 0.05: w = w / w.sum()
                    blends.append(w)

# Balanced growth 60/40
for intl in [0.08, 0.12, 0.16, 0.20, 0.24]:
    for bond in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]:
        for real in [0.00, 0.05, 0.08]:
            eq = max(0, 1 - intl - bond - real)
            if eq < 0.18: continue
            for spy_s in [0.50, 0.55, 0.60]:
                spmd_s = max(0, 1 - spy_s - 0.25 - 0.15)
                w = np.zeros(9)
                w[0] = intl * 0.55; w[3] = intl * 0.45
                w[4] = eq * spy_s; w[1] = eq * 0.25
                w[2] = eq * 0.15; w[6] = eq * spmd_s
                w[5] = real; w[7] = bond * 0.80; w[8] = bond * 0.20
                w = np.maximum(w, 0)
                w = w / w.sum()
                blends.append(w)

# Conservative
for bond in [0.40, 0.50, 0.60, 0.70]:
    for eq in [0.20, 0.30, 0.40, 0.50]:
        if bond + eq > 1.0: continue
        cash = 1 - bond - eq
        intl = min(0.10, eq * 0.15)
        w = np.zeros(9)
        w[0] = intl * 0.6; w[3] = intl * 0.4
        w[4] = (eq - intl) * 0.60; w[1] = (eq - intl) * 0.30; w[2] = (eq - intl) * 0.10
        w[5] = 0.0; w[6] = 0.0
        w[7] = bond * 0.75; w[8] = bond * 0.25 + cash
        w = np.maximum(w, 0)
        w = w / w.sum()
        blends.append(w)

print(f"Structured blends: {len(blends)}")

# Monte Carlo fill
while len(blends) < 250:
    alpha = np.array([2, 4, 2, 1.5, 5, 1, 2, 2, 0.5])
    w = np.random.dirichlet(alpha)
    w[8] = min(w[8], 0.08)
    w = np.maximum(w, 0); w = w / w.sum()
    blends.append(w)

blends = blends[:250]
print(f"Total blends: {len(blends)}")

# ─── Backtest ─────────────────────────────────────────────────────────────────
results = []
for i, w in enumerate(blends):
    port_ret = monthly_returns.values @ w
    n = len(port_ret)
    ann_ret = (1+port_ret).prod() ** (12/n) - 1
    ann_vol = port_ret.std() * np.sqrt(12)
    sharpe  = (ann_ret - 0.02) / ann_vol if ann_vol > 0 else 0
    cum_ret = (1+port_ret).prod() - 1
    cc = np.cumprod(1+port_ret)
    max_dd = (cc / np.maximum.accumulate(cc) - 1).min()
    neg = port_ret[port_ret < 0.02/12]
    dstd = neg.std() * np.sqrt(12) if len(neg) > 0 else ann_vol
    sortino = (ann_ret - 0.02) / dstd if dstd > 0 else 0
    calmar  = ann_ret / abs(max_dd) if max_dd != 0 else 0
    
    yr_list = []
    for yr in range(monthly_returns.index[0].year, monthly_returns.index[-1].year+1):
        mask = monthly_returns.index.year == yr
        if mask.sum() < 10: continue
        yr_ret = port_ret[mask]
        yr_list.append({'year': yr, 'return': round(((1+yr_ret).prod()-1)*100,2)})
    
    results.append({
        'blend_id': i+1,
        'weights': dict(zip(fund_list, w.round(4).tolist())),
        'ann_return': round(ann_ret*100,2),
        'ann_vol': round(ann_vol*100,2),
        'sharpe': round(sharpe,3),
        'sortino': round(sortino,3),
        'calmar': round(calmar,3),
        'cum_return': round(cum_ret*100,2),
        'max_drawdown': round(max_dd*100,2),
        'annual_returns': yr_list,
        'best_year': max(yr_list,key=lambda x:x['return']) if yr_list else {'year':0,'return':0},
        'worst_year': min(yr_list,key=lambda x:x['return']) if yr_list else {'year':0,'return':0},
    })

top3 = sorted(results, key=lambda x: x['sharpe'], reverse=True)[:3]

print("\n=== TOP 3 BY SHARPE ===")
lbl = {'EFA':'ZDEVLT','IWB':'ZBGRIT','IWM':'ZBGRNT','ACWX':'WMTX2','SPY':'WMTX8','VNQ':'WMTX7','SPMD':'WMTX9','AGG':'ZDEVNT/WMTX1','BIL':'BGMMT/ZDBCFT'}
for rank, r in enumerate(top3, 1):
    print(f"\n#{rank}: Return={r['ann_return']}% Vol={r['ann_vol']}% Sharpe={r['sharpe']} Sortino={r['sortino']} MaxDD={r['max_drawdown']}% Cum={r['cum_return']}%")
    for sym, w in sorted(r['weights'].items(), key=lambda x:-x[1]):
        if w > 0.005:
            print(f"   {lbl.get(sym,sym)}: {w*100:.1f}%")

# Build output JSON
dates = [str(d.date()) for d in monthly_returns.index]
curves = {}
for rank, r in enumerate(top3, 1):
    w = np.array([r['weights'][f] for f in fund_list])
    pret = monthly_returns.values @ w
    curves[f'P{rank}'] = {'dates': dates, 'values': list(np.round(np.cumprod(1+pret)*100, 2))}
for sym in ['SPY','IWB','EFA','AGG','VNQ','IWM']:
    curves[sym] = {'dates': dates, 'values': list(np.round((1+monthly_returns[sym]).cumprod()*100, 2))}

scatter = [{'x': r['ann_vol'], 'y': r['ann_return'], 'sharpe': r['sharpe'], 'id': r['blend_id']} for r in results]
corr = monthly_returns.corr().round(3).to_dict()

yearly = {}
for yr in range(monthly_returns.index[0].year, monthly_returns.index[-1].year+1):
    mask = monthly_returns.index.year == yr
    if mask.sum() < 10: continue
    yd = {}
    for sym in fund_list:
        yd[sym] = round(((1+monthly_returns[sym][mask]).prod()-1)*100, 2)
    for rank, r in enumerate(top3, 1):
        w = np.array([r['weights'][f] for f in fund_list])
        yr_ret = monthly_returns.values[mask] @ w
        yd[f'P{rank}'] = round(((1+yr_ret).prod()-1)*100, 2)
    yearly[str(yr)] = yd

output = {
    'individual_stats': stats,
    'top3': top3,
    'all_blends_count': len(results),
    'date_range': {'start': str(prices.index[0].date()), 'end': str(prices.index[-1].date()), 'months': len(prices)},
    'growth_curves': curves,
    'scatter': scatter,
    'correlation': corr,
    'yearly_returns': yearly,
    'fund_labels': lbl
}

with open('/home/user/workspace/finance_data/backtest_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print("\nDone! Saved backtest_results.json")

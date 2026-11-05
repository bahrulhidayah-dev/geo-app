

# ---------------- mineral modes ----------------
MODE_COLOURS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00",
                "#F0E442", "#999999", "#000000"]   # Okabe and Ito (2008)


def plot_modes(table, style="dark", width=6.4):
    """Mineral modes (wt%) as one horizontal stacked bar per sample.
    table: rows = samples (index = names), columns = minerals. Negative
    fractions are drawn as zero and marked with an asterisk."""
    s = STYLES[style]
    table = table.astype(float)
    n = len(table)
    fig = _figure((width, 1.4 + 0.30 * max(n, 1)))
    fig.patch.set_facecolor(s["bg"])
    fig._geo_style = s
    ax = fig.subplots()
    y = np.arange(n)[::-1]
    left = np.zeros(n)
    for k, m in enumerate(table.columns):
        v = table[m].clip(lower=0).fillna(0).to_numpy()
        ax.barh(y, v, left=left, height=0.72, color=MODE_COLOURS[k % len(MODE_COLOURS)],
                edgecolor=s["bg"], linewidth=0.4, label=str(m), zorder=3)
        left += v
    neg = (table < -0.5).any(axis=1).to_numpy()
    labels = [f"{nm} *" if bad else str(nm) for nm, bad in zip(table.index, neg)]
    ax.set_yticks(y, labels)
    ax.set_xlim(0, max(100.0, float(left.max()) if n else 100.0))
    ax.set_ylim(-0.6, n - 0.4)
    _style_axes(ax, s, "Mode (wt%)", None)
    _legend(ax, s, title=None, where="below")
    return _finish(fig)

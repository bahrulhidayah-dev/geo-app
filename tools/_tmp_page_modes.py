def md_sources(df, rocks):
    """Rock compositions that can be chosen: the mean of every group and every sample."""
    names = df.iloc[:, 0].astype(str)
    src = {}
    g = st.session_state.get("group_col", NONE)
    if g != NONE and g in df:
        for grp, part in df.groupby(df[g].astype(str)):
            src[t("Mean of group: {g} (n = {n})").format(g=grp, n=len(part))] = \
                rocks.loc[part.index].mean()
    for i, n in names.items():
        src[t("Sample: {s}").format(s=n)] = rocks.loc[i]
    return src


def page_modes():
    header(t("Mineral modes"),
           t("Mineral proportions (wt%) from the whole-rock analysis by least squares, "
             "with the condition that the minerals add up to 100 % (Albarède 1995, "
             "section 5.3). For serpentinised peridotites H2O (from LOI) is used as a "
             "component, so serpentine can be told apart from olivine."))
    if ctx is None:
        empty_state()
        return
    df = view()
    rocks = modes.rock_components(df)
    if rocks[["SiO2", "MgO"]].dropna().empty:
        missing_note(["SiO2", "MgO", "FeOt / Fe2O3", "LOI / H2O+"])
        return
    left, right = st.columns([2, 3], gap="large")
    with left:
        names = st.multiselect(
            t("Minerals"), list(modes.MINERALS), default=modes.DEFAULT_MINERALS,
            key="md_min",
            help=t("Choose only minerals that are present in the rock. At most one mineral "
                   "per component can be resolved: with six components (SiO2, Al2O3, "
                   "FeOt, MgO, CaO, H2O) choose at most six minerals."))
        comps = st.multiselect(
            t("Components"), modes.COMPONENTS,
            default=[c for c in modes.COMPONENTS if rocks[c].notna().any()], key="md_comp",
            help=t("H2O is taken from H2O+ when the file has it, otherwise from LOI. All "
                   "iron is used as FeOt, so magnetite is entered as 93.1 % FeOt."))
        if not names or not comps:
            st.info(t("Choose at least one mineral and one component."))
            return
        with st.expander(t("Mineral compositions (wt%)")):
            st.caption(t("Ideal compositions. Replace them with your own analyses (for "
                         "example EPMA) for better modes; add a row for another mineral."))
            base = modes.mineral_table(names).T.round(2).rename_axis("Mineral").reset_index()
            ed = st.data_editor(base, num_rows="dynamic", hide_index=True, width="stretch",
                                key="md_ed_" + "|".join(names))
        ed = ed.dropna(subset=["Mineral"])
        ed = ed[ed["Mineral"].astype(str).str.strip() != ""]
        A = ed.set_index("Mineral")[modes.COMPONENTS].astype(float).fillna(0).T
        A = A.loc[comps]
        if A.shape[1] == 0:
            st.info(t("Choose at least one mineral and one component."))
            return
    src = md_sources(df, rocks[comps])
    with right:
        tab1, tab2 = st.tabs([t("One sample"), t("All samples")])
        with tab1:
            pick = st.selectbox(t("Rock composition"), list(src), key="md_rock")
            y = src[pick].astype(float)
            out = modes.solve(y, A)
            for w in out["warnings"]:
                st.warning(t(w), icon=":material/warning:")
            sd = modes.uncertainty(y, A)
            m1, m2, m3 = st.columns(3)
            m1.metric(t("Sum of squared residuals"), f"{out['ssr']:.3f}",
                      help=t("Sum of (measured − calculated)² over the components, in "
                             "(wt%)². Large values mean the minerals do not explain the "
                             "rock: a mineral is missing or its composition is wrong."))
            m2.metric(t("Condition number"), f"{out['condition']:.0f}",
                      help=t("How strongly the modes react to small analytical errors. "
                             "Below about 100 the minerals are well separated; above 300 "
                             "the modes are unstable."))
            m3.metric(t("Components used"), len(out["components"]))
            res = pd.DataFrame({t("Mode (wt%)"): 100 * out["x"], "±1σ": sd,
                                t("Without the sum condition (wt%)"): 100 * out["x0"]})
            res.index.name = t("Mineral")
            show(plotting.plot_modes((100 * out["x"]).to_frame(pick).T, style=SCREEN))
            st.dataframe(res.round(2))
            fit = pd.DataFrame({t("Measured"): y[out["components"]], t("Calculated"): out["fit"],
                                t("Residual"): out["residual"]})
            fit.index.name = t("Component")
            st.dataframe(fit.round(2))
            st.caption(t("±1σ: spread of the modes when the analysis is varied by its "
                         "analytical error (1 % relative, at least 0.05 wt%; 300 runs). "
                         "Modes are mass fractions, not volume fractions."))
        with tab2:
            table, info = modes.solve_all(rocks[comps], A)
            if table.empty:
                st.info(t("No sample has SiO2 and MgO."))
            else:
                names_s = df.iloc[:, 0].astype(str).reindex(table.index)
                out_t = table.copy()
                out_t.insert(0, t("Sample"), names_s)
                out_t[t("Sum of squared residuals")] = info["Sum of squared residuals"]
                st.dataframe(out_t.round(2), hide_index=True, height=320)
                csv_download(t("Download mineral modes (CSV)"), lambda: out_t,
                             "mineral_modes.csv")
                shown = table.set_axis(names_s).head(40)
                show(plotting.plot_modes(shown, style=SCREEN))
                downloads(lambda s_: plotting.plot_modes(shown, style=s_), "mineral_modes")
                if (table < -0.5).any(axis=None):
                    st.caption(t("* Some modes are negative (drawn as zero): that mineral is "
                                 "probably absent in the sample, or its composition does "
                                 "not fit. Remove it and compare the residuals."))
                if len(table) > 40:
                    st.caption(t("The chart shows the first 40 samples; the table has all."))

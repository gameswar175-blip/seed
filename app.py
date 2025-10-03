import os
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Altair: remove limite padrão de linhas (evita warning/corte)
alt.data_transformers.disable_max_rows()

st.set_page_config(page_title="Fluxo SEED — Dashboard", layout="wide")

# --- Toggle de tema Claro/Escuro + CSS + Altair + AgGrid ---
tema = st.sidebar.radio("Tema do app", ["Claro", "Escuro"], index=1,
                        help="Troca cores do app, dos gráficos e da grid.")

def aplicar_css_tema(modo: str):
    if modo == "Escuro":
        st.markdown("""
<style>
:root {
  --bg1: #071225;
  --bg2: #0a102a;
  --bg3: #0b1533;
  --fg:  #e5e7eb;
  --neon:#22d3ee;  /* ciano */
}

/* Fundo com gradiente animado (sutil) */
@keyframes aurora {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}



.stApp {
  background: linear-gradient(270deg, #0f172a, #1e3a8a, #9333ea, #0f172a);
  background-size: 600% 600%;
  animation: aurora 120s ease infinite;
}


/* Sidebar com gradiente (sem exagero) */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--bg3) 0%, var(--bg2) 100%);
  color: var(--fg);
  background-size: 160% 160%;
  animation: aurora 20s ease-in-out infinite;
}

/* Container principal sem cartão sólido */
.block-container { background: transparent; }

/* ===== Botões (st.button) com acento ciano e leve glow ===== */
.stButton > button {
  border: 1px solid var(--neon);
  background: linear-gradient(180deg, rgba(34,211,238,0.10) 0%, rgba(34,211,238,0.03) 100%);
  color: var(--fg);
  box-shadow: 0 0 0px rgba(34,211,238,0.0);
  transition: box-shadow .2s ease, transform .05s ease, background .2s ease;
}
.stButton > button:hover {
  box-shadow: 0 0 16px rgba(34,211,238,0.35), 0 0 2px rgba(34,211,238,0.6) inset;
}
.stButton > button:active {
  transform: translateY(1px);
}

/* ===== Métricas (st.metric) com moldura/acento ===== */
div[data-testid="stMetric"] {
  border: 1px solid rgba(34,211,238,0.45);
  border-radius: 10px;
  padding: 10px 12px;
  background: linear-gradient(180deg, rgba(13,34,53,0.35) 0%, rgba(10,16,42,0.25) 100%);
  box-shadow: 0 0 10px rgba(34,211,238,0.12);
}
div[data-testid="stMetricValue"] {
  color: #eaf7fb;
  text-shadow: 0 0 6px rgba(34,211,238,0.35);
}
div[data-testid="stMetricDelta"] {
  color: #a7f3d0 !important; /* delta verde clarinho */
}

/* ===== Harmonizar AgGrid ao fundo ===== */
[class*="ag-theme-"] .ag-root-wrapper,
[class*="ag-theme-"] .ag-header,
[class*="ag-theme-"] .ag-header-cell,
[class*="ag-theme-"] .ag-row {
  background-color: transparent !important;
  color: var(--fg) !important;
}

/* Inputs básicos ficam legíveis no escuro */
input, select, textarea {
  background-color: #0f172a !important;
  color: var(--fg) !important;
  border: 1px solid rgba(148,163,184,.22) !important;
}

/* Links em ciano */
a { color: var(--neon); }
</style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
<style>
.stApp { background: #ffffff; color: #0f172a; }
[data-testid="stSidebar"] { background-color: #f1f5f9; color: #0f172a; }
.block-container { background: transparent; }
/* Acento suave nos botões no claro */
.stButton > button {
  border: 1px solid #0ea5e9;
  background: linear-gradient(180deg, rgba(14,165,233,0.10) 0%, rgba(14,165,233,0.03) 100%);
}
div[data-testid="stMetric"] {
  border: 1px solid rgba(14,165,233,0.35);
  border-radius: 10px;
  padding: 10px 12px;
  background: #ffffff;
}
</style>
        """, unsafe_allow_html=True)


aplicar_css_tema(tema)

PALETA_CLARA  = ["#0b6b3a", "#0ea5e9", "#f59e0b", "#ef4444", "#8b5cf6", "#14b8a6", "#22c55e", "#e11d48"]
# Paleta “neon” para modo escuro (ciano/azul/púrpura, com alternâncias vivas)
PALETA_ESCURO = [
    "#22d3ee",  # ciano
    "#60a5fa",  # azul
    "#a78bfa",  # roxo
    "#f472b6",  # pink
    "#34d399",  # esmeralda
    "#f59e0b",  # âmbar
    "#f87171",  # vermelho suave
    "#4ade80"   # verde claro
]

def altair_tema_escuro():
    return {
        "config": {
            "background": "#0a102a",            # canvas escuro-azulado
            "view": {"stroke": "transparent"},  # sem moldura no gráfico
            "title":  {"fontSize": 14, "font": "Inter", "color": "#e5e7eb"},
            "axis":   {
                "labelFont": "Inter", "titleFont": "Inter",
                "labelColor": "#e5e7eb", "titleColor": "#e5e7eb",
                "gridColor": "#1f2a44"          # grade discreta no azul
            },
            "legend": {"labelFont": "Inter", "titleFont": "Inter",
                       "labelColor": "#e5e7eb", "titleColor": "#e5e7eb"},
            "range":  {"category": PALETA_ESCURO}
        }
    }

def altair_tema_claro():
    return {
        "config": {
            "background": "#ffffff",
            "title":  {"fontSize": 14, "font": "Inter", "color": "#0f172a"},
            "axis":   {"labelFont": "Inter", "titleFont": "Inter",
                       "labelColor": "#0f172a", "titleColor": "#0f172a"},
            "legend": {"labelFont": "Inter", "titleFont": "Inter",
                       "labelColor": "#0f172a", "titleColor": "#0f172a"},
            "range":  {"category": PALETA_CLARA}
        }
    }


alt.themes.register("tema_claro_seed", altair_tema_claro)
alt.themes.register("tema_escuro_seed", altair_tema_escuro)
alt.themes.enable("tema_escuro_seed" if tema == "Escuro" else "tema_claro_seed")



# 5) Tema do AgGrid
grid_theme = "alpine-dark" if tema == "Escuro" else "alpine"






# (Daqui para baixo segue o seu app normalmente)
st.title("📊 Fluxo SEED — Dashboard Operacional")
st.caption("Filtro → KPIs → Gráficos → Grid → Alertas → Comparar Lojas (A vs B)")




# ---------- Sidebar ----------
st.sidebar.header("⚙️ Configurações")

uploaded = st.sidebar.file_uploader("Envie o Excel (opcional)", type=["xlsx", "xls"])
use_clean_csv = st.sidebar.checkbox("Usar CSV já limpo (fluxo_seed_limpo.csv)", value=True)

# Alertas
st.sidebar.markdown("### 🚨 Alertas (queda vs baseline)")
baseline_window = st.sidebar.slider("Janela da média móvel (dias)", 5, 30, 7, 1)
pct_alerta = st.sidebar.slider("Alerta (queda ≥ X%)", 5, 60, 20, 5)
pct_critico = st.sidebar.slider("Crítico (queda ≥ Y%)", 10, 90, 40, 5)

# Zero prolongado (opcional) — listagem detalhada ativaremos depois
min_consecutive_zero = st.sidebar.slider("Horas consecutivas com fluxo = 0 (sinalizar)", 2, 8, 4, 1)

st.sidebar.markdown("---")
st.sidebar.caption("Dica: na grid, use a **sidebar do AgGrid** para pinar colunas, filtrar e agrupar.")

# ---------- Helpers ----------
@st.cache_data(show_spinner=False)
def read_clean_or_raw(uploaded_file, use_clean=True):
    """
    1) Se existir fluxo_seed_limpo.csv no diretório, usa (rápido).
    2) Se o usuário enviar um Excel, detecta cabeçalho automaticamente.
    3) Como último recurso, tenta ler o Excel local 'Fluxo SEED 30d.xlsx'.
    """
    # 1) CSV limpo
    if use_clean and os.path.exists("fluxo_seed_limpo.csv"):
        df = pd.read_csv("fluxo_seed_limpo.csv")
        df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
        df["Hora"] = pd.to_numeric(df["Hora"], errors="coerce").astype("Int64")
        df["Fluxo"] = pd.to_numeric(df["Fluxo"], errors="coerce")
        for c in ["Company", "Loja", "ID_Loja"]:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip()
        return df

    # 2) Excel enviado
    if uploaded_file is not None:
        try:
            raw = pd.read_excel(uploaded_file, sheet_name="Fluxo seed 30d", header=None, engine="openpyxl")
        except Exception:
            raw = pd.read_excel(uploaded_file, header=None, engine="openpyxl")

        expected = {"Company", "Loja", "ID_Loja", "Data", "Hora", "Fluxo"}
        header_idx = None
        for i, row in raw.iterrows():
            vals = set(str(x).strip() for x in row.values if pd.notna(x))
            if expected.issubset(vals):
                header_idx = i
                break
        if header_idx is None:
            for i, row in raw.iterrows():
                vals = set(str(x).strip() for x in row.values if pd.notna(x))
                if {"Loja", "Data", "Fluxo"}.issubset(vals):
                    header_idx = i
                    break
        if header_idx is None:
            st.error("Não foi possível detectar o cabeçalho no Excel. Envie o CSV limpo ou verifique a planilha.")
            return pd.DataFrame()

        # Constrói o DataFrame usando a linha de cabeçalho detectada
        header = raw.iloc[header_idx].astype(str).tolist()
        # Dedup de nomes de coluna (Data, Data.1 etc)
        counts, header_dedup = {}, []
        for h in header:
            if h in counts:
                counts[h] += 1
                header_dedup.append(f"{h}.{counts[h]}")
            else:
                counts[h] = 0
                header_dedup.append(h)

        data = raw.iloc[header_idx + 1:].copy()
        data.columns = header_dedup

        # Seleciona e renomeia colunas padrão
        def pick(name):
            cols = [c for c in data.columns if c.split(".")[0] == name]
            return cols[0] if cols else None

        mapping = {n: pick(n) for n in ["Company", "Loja", "ID_Loja", "Data", "Hora", "Fluxo"]}
        keep = [c for c in mapping.values() if c]
        if not keep:
            st.error("Não encontrei colunas esperadas (Company/Loja/ID_Loja/Data/Hora/Fluxo).")
            return pd.DataFrame()

        df = data[keep].rename(columns={v: k for k, v in mapping.items() if v})

        # Coerções
        if "Data" in df.columns:
            df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
        if "Hora" in df.columns:
            df["Hora"] = pd.to_numeric(df["Hora"], errors="coerce").astype("Int64")
        if "Fluxo" in df.columns:
            df["Fluxo"] = pd.to_numeric(df["Fluxo"], errors="coerce")

        for c in ["Company", "Loja", "ID_Loja"]:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip()

        df = df.dropna(how="all", subset=[c for c in ["Data", "Hora", "Fluxo", "Loja"] if c in df.columns])

        return df

    # 3) Excel local original
    if os.path.exists("Fluxo SEED 30d.xlsx"):
        try:
            raw = pd.read_excel("Fluxo SEED 30d.xlsx", sheet_name="Fluxo seed 30d", header=None, engine="openpyxl")
        except Exception:
            raw = pd.read_excel("Fluxo SEED 30d.xlsx", header=None, engine="openpyxl")
        # Reaproveita a mesma lógica acima
        expected = {"Company", "Loja", "ID_Loja", "Data", "Hora", "Fluxo"}
        header_idx = None
        for i, row in raw.iterrows():
            vals = set(str(x).strip() for x in row.values if pd.notna(x))
            if expected.issubset(vals):
                header_idx = i
                break
        if header_idx is None:
            for i, row in raw.iterrows():
                vals = set(str(x).strip() for x in row.values if pd.notna(x))
                if {"Loja", "Data", "Fluxo"}.issubset(vals):
                    header_idx = i
                    break
        if header_idx is None:
            return pd.DataFrame()

        header = raw.iloc[header_idx].astype(str).tolist()
        counts, header_dedup = {}, []
        for h in header:
            if h in counts:
                counts[h] += 1
                header_dedup.append(f"{h}.{counts[h]}")
            else:
                counts[h] = 0
                header_dedup.append(h)

        data = raw.iloc[header_idx + 1:].copy()
        data.columns = header_dedup

        def pick(name):
            cols = [c for c in data.columns if c.split(".")[0] == name]
            return cols[0] if cols else None

        mapping = {n: pick(n) for n in ["Company", "Loja", "ID_Loja", "Data", "Hora", "Fluxo"]}
        keep = [c for c in mapping.values() if c]
        if not keep:
            return pd.DataFrame()

        df = data[keep].rename(columns={v: k for k, v in mapping.items() if v})

        if "Data" in df.columns:
            df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
        if "Hora" in df.columns:
            df["Hora"] = pd.to_numeric(df["Hora"], errors="coerce").astype("Int64")
        if "Fluxo" in df.columns:
            df["Fluxo"] = pd.to_numeric(df["Fluxo"], errors="coerce")

        for c in ["Company", "Loja", "ID_Loja"]:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip()

        df = df.dropna(how="all", subset=[c for c in ["Data", "Hora", "Fluxo", "Loja"] if c in df.columns])

        return df

    # Sem dados
    return pd.DataFrame()

def add_alertas(df, janela=7, x=20, y=40):
    """Calcula alertas por LOJA/DIA vs média móvel da própria loja."""
    if df.empty:
        return df, pd.DataFrame()

    di = df.groupby(["Loja", "ID_Loja", "Data"], as_index=False)["Fluxo"].sum()
    di = di.sort_values(["Loja", "Data"])

    # Média móvel por loja (mínimo de dados para começar = metade da janela, pelo menos 2)
    minp = max(2, janela // 2)
    di["mm_baseline"] = di.groupby("Loja")["Fluxo"].transform(lambda s: s.rolling(window=janela, min_periods=minp).mean())

    # Variação %
    di["var_pct"] = np.where(
        di["mm_baseline"].gt(0),
        (di["Fluxo"] - di["mm_baseline"]) / di["mm_baseline"] * 100.0,
        np.nan
    )

    def status(v):
        if pd.isna(v):
            return "—"
        if v <= -y:
            return "Crítico"
        if v <= -x:
            return "Alerta"
        return "No prazo"

    di["Status"] = di["var_pct"].apply(status)
    return df, di

# ---------- Carga ----------
df = read_clean_or_raw(uploaded, use_clean=use_clean_csv)

if df.empty:
    st.warning("Envie o arquivo ou deixe marcado **Usar CSV já limpo** (se estiver na pasta).")
    st.stop()

# ---------- Filtros ----------
min_d, max_d = df["Data"].min().date(), df["Data"].max().date()
lojas = sorted(df["Loja"].dropna().unique().tolist())

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    f_data = st.date_input("Período", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    f_inicio, f_fim = pd.to_datetime(f_data[0]), pd.to_datetime(f_data[1])
with c2:
    f_lojas = st.multiselect("Lojas", options=lojas, default=lojas)
with c3:
    hmin, hmax = int(df["Hora"].min()), int(df["Hora"].max())
    f_horas = st.slider("Horas", min_value=hmin, max_value=hmax, value=(hmin, hmax), step=1)

# Aplica filtros
mask = (
    (df["Data"].between(f_inicio, f_fim)) &
    (df["Loja"].isin(f_lojas)) &
    (df["Hora"].between(f_horas[0], f_horas[1]))
)
df_f = df.loc[mask].copy()

# ---------- KPIs ----------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Fluxo (soma)", f"{int(df_f['Fluxo'].sum()):,}".replace(",", "."))
with k2:
    media_dia = df_f.groupby("Data")["Fluxo"].sum().mean() if not df_f.empty else 0
    st.metric("Média por dia", f"{media_dia:.1f}")
with k3:
    st.metric("Dias no filtro", f"{df_f['Data'].nunique()}")

pico_dia = df_f.groupby("Data", as_index=False)["Fluxo"].sum().sort_values("Fluxo", ascending=False).head(1)
if not pico_dia.empty:
    d = pico_dia.iloc[0]["Data"].date().isoformat()
    v = int(pico_dia.iloc[0]["Fluxo"])
    with k4:
        st.metric("Pico do período (dia)", f"{v:,}".replace(",", ".") + f" em {d}")
else:
    with k4:
        st.metric("Pico do período (dia)", "—")

st.markdown("---")

# ---------- Gráfico: série temporal ----------
st.subheader("📈 Evolução diária (soma)")
daily = df_f.groupby("Data", as_index=False)["Fluxo"].sum()
if not daily.empty:
    chart = (
        alt.Chart(daily)
        .mark_line(point=True)
        .encode(
            x=alt.X("Data:T", title="Data"),
            y=alt.Y("Fluxo:Q", title="Fluxo (soma)"),
            tooltip=["Data", "Fluxo"]
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Sem dados no intervalo/lojas/horas selecionados.")

# ---------- Ranking de lojas ----------
st.subheader("🏆 Ranking de lojas (soma no filtro)")
rank = df_f.groupby(["Loja", "ID_Loja"], as_index=False)["Fluxo"].sum().sort_values("Fluxo", ascending=False)
st.dataframe(rank, use_container_width=True, height=280)

# ---------- Heatmap Data × Hora ----------
st.subheader("🔥 Heatmap — Data × Hora (soma)")
pivot = df_f.groupby(["Data", "Hora"], as_index=False)["Fluxo"].sum()
if not pivot.empty:
    heat = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("Hora:O", title="Hora"),
            y=alt.Y("Data:T", title="Data"),
            color=alt.Color("Fluxo:Q", title="Fluxo", scale=alt.Scale(scheme="blues")),
            tooltip=["Data", "Hora", "Fluxo"]
        )
        .properties(height=420)
    )
    st.altair_chart(heat, use_container_width=True)
else:
    st.info("Sem dados para exibir no heatmap.")

# ---------- Grid interativa ----------
st.subheader("🧱 Tabela (interativa)")
cols_grid = [c for c in ["Company", "Loja", "ID_Loja", "Data", "Hora", "Fluxo"] if c in df_f.columns]
gb = GridOptionsBuilder.from_dataframe(df_f[cols_grid])
gb.configure_default_column(sortable=True, filter=True, groupable=True, resizable=True)
gb.configure_side_bar()
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=True)
AgGrid(
    df_f[cols_grid],
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.MODEL_CHANGED,
    enable_enterprise_modules=True,
    theme=grid_theme,
    height=420
)

st.download_button(
    "📥 Baixar dados filtrados (CSV)",
    data=df_f.to_csv(index=False).encode("utf-8"),
    file_name="fluxo_filtrado.csv",
    mime="text/csv"
)

st.markdown("---")

# ---------- Alertas (queda vs média móvel) ----------
st.subheader("🚨 Alertas — Queda vs baseline por loja")

_, di = add_alertas(df, janela=baseline_window, x=pct_alerta, y=pct_critico)
di_f = di[(di["Data"].between(pd.to_datetime(f_inicio), pd.to_datetime(f_fim))) & (di["Loja"].isin(f_lojas))].copy()

if not di_f.empty:
    ult_dia = di_f["Data"].max()
    ult = di_f[di_f["Data"] == ult_dia].sort_values(["Status", "var_pct"], ascending=[True, True])
    st.caption(f"Status na última data do filtro: **{ult_dia.date().isoformat()}**")
    mostra = (
        ult[["Loja", "ID_Loja", "Fluxo", "mm_baseline", "var_pct", "Status"]]
        .rename(columns={"Fluxo": "Fluxo do dia", "mm_baseline": "Baseline (MM)", "var_pct": "Var %"})
    )
    st.dataframe(mostra, use_container_width=True, height=320)

    st.download_button(
        "📥 Baixar alertas (último dia no filtro, CSV)",
        data=ult.to_csv(index=False).encode("utf-8"),
        file_name="alertas_ultimo_dia.csv",
        mime="text/csv"
    )
else:
    st.info("Sem dados para calcular alertas no intervalo selecionado.")

# ---------- Comparar Lojas ----------
st.markdown("---")
st.header("🔍 Comparar Lojas")

if df_f.empty:
    st.info("Ajuste os filtros de período/lojas/horas para comparar.")
else:
    # =====================
    # Seleção de lojas A e B
    # =====================
    lojas_filtro = sorted(df_f["Loja"].dropna().unique().tolist())
    cA, cB, cMode = st.columns([2, 2, 2])
    with cA:
        loja_A = st.selectbox("Loja A", options=lojas_filtro, index=0 if lojas_filtro else None)
    with cB:
        idx_default_B = 1 if len(lojas_filtro) > 1 else 0
        loja_B = st.selectbox("Loja B", options=lojas_filtro, index=idx_default_B)
    with cMode:
        modo = st.radio(
            "Modo de comparação",
            options=[
                "Agregado por hora (período)",            # A vs B (loja única) - já existia
                "Evolução diária (A vs B)",               # A vs B (diário)      - já existia
                "Agregado por hora (sobreposto, N lojas)",# N lojas individuais  - já existe no seu app
                "Agregado por hora (A×B, múltiplas lojas por lado)",  # <-- NOVO
                "Evolução diária (A×B, múltiplas lojas por lado)"     # <-- NOVO
            ],
            index=0,
            horizontal=False
        )



    if loja_A == loja_B:
        st.warning("Selecione **duas** lojas diferentes para comparar.")
    else:
        # =====================
        # Funções auxiliares
        # =====================
        def agg_por_hora(df_sel):
            """Agrega soma por Loja x Hora no período filtrado."""
            t = (df_sel.groupby(["Loja", "Hora"], as_index=False)["Fluxo"].sum())
            t = t.dropna(subset=["Hora"])
            t["Hora"] = t["Hora"].astype(int)
            t["Fluxo"] = pd.to_numeric(t["Fluxo"], errors="coerce").fillna(0)
            return t

        def agg_por_dia(df_sel):
            """Agrega soma por Loja x Dia."""
            d = (df_sel.groupby(["Loja", "Data"], as_index=False)["Fluxo"].sum()
                        .sort_values(["Loja", "Data"]))
            d["Fluxo"] = pd.to_numeric(d["Fluxo"], errors="coerce").fillna(0)
            d["Data"] = pd.to_datetime(d["Data"], errors="coerce")
            return d

        # =====================
        # A vs B
        # =====================
        df_AB = df_f[df_f["Loja"].isin([loja_A, loja_B])].copy()

        # KPIs (período filtrado)
        tot_A = int(df_AB.loc[df_AB["Loja"] == loja_A, "Fluxo"].sum())
        tot_B = int(df_AB.loc[df_AB["Loja"] == loja_B, "Fluxo"].sum())
        diff_abs = tot_A - tot_B
        diff_pct = (diff_abs / tot_B * 100.0) if tot_B > 0 else np.nan

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric(f"Fluxo — {loja_A}", f"{tot_A:,}".replace(",", "."))
        with k2: st.metric(f"Fluxo — {loja_B}", f"{tot_B:,}".replace(",", "."))
        with k3: st.metric("Δ absoluto (A - B)", f"{diff_abs:,}".replace(",", "."))
        with k4: st.metric("Δ % vs B", f"{diff_pct:.1f}%" if pd.notna(diff_pct) else "—")

        # =====================
        # Modo 1: Agregado por hora (período)
        # =====================
        if modo == "Agregado por hora (período)":
            hora_sum = agg_por_hora(df_AB)

            # Pivota para A e B lado a lado
            base = hora_sum.pivot_table(index="Hora", columns="Loja", values="Fluxo", aggfunc="sum", fill_value=0)
            if (loja_A not in base.columns) or (loja_B not in base.columns):
                st.info("Sem dados suficientes para uma das lojas neste intervalo/horas.")
            else:
                base = base.reset_index().rename(columns={loja_A: "Fluxo_A", loja_B: "Fluxo_B"})
                base["Delta"] = base["Fluxo_A"] - base["Fluxo_B"]
                base["Vencedor"] = np.where(base["Delta"] > 0, "A", np.where(base["Delta"] < 0, "B", "Empate"))

                # Métricas de vitória por hora
                horas_A = int((base["Delta"] > 0).sum())
                horas_B = int((base["Delta"] < 0).sum())
                horas_empate = int((base["Delta"] == 0).sum())
                st.caption(f"🏁 Por hora no período: **{loja_A}** vence em **{horas_A}h**, **{loja_B}** vence em **{horas_B}h**, empates: **{horas_empate}h**.")

                # --- Linhas A vs B (usando melt em pandas, sem transform_fold) ---

                for col in ["Fluxo_A", "Fluxo_B"]:
                    base[col] = pd.to_numeric(base[col], errors="coerce").fillna(0)
                base["Hora"] = base["Hora"].astype(int)

                long = base.melt(
                    id_vars=["Hora"],
                    value_vars=["Fluxo_A", "Fluxo_B"],
                    var_name="Serie",
                    value_name="Fluxo"
                )
                long["Serie"] = long["Serie"].map({"Fluxo_A": loja_A, "Fluxo_B": loja_B})
                long["Fluxo"] = pd.to_numeric(long["Fluxo"], errors="coerce").fillna(0)

                # Camada de glow (grossa, translúcida) + camada nítida com pontos

                glow = (
                    alt.Chart()
                    .mark_line(strokeWidth=8, opacity=0.90)  # <-- reforça o neon
                    .encode(
                        x=alt.X("Hora:O", title="Hora"),
                        y=alt.Y("Fluxo:Q", title="Fluxo (soma no período)"),
                        color=alt.Color("Loja:N", title="Loja")
                    )
                )

                
                linhas = (
                    alt.Chart(long)
                    .mark_line(point=True, strokeWidth=2.2)
                    .encode(
                        x=alt.X("Hora:O", title="Hora"),
                        y=alt.Y("Fluxo:Q", title="Fluxo (soma no período)"),
                        color=alt.Color("Serie:N", title="Loja"),
                        tooltip=["Hora", "Serie", alt.Tooltip("Fluxo:Q", format=",.0f")]
                    )
                )
                chart_lines = (glow + linhas).properties(height=280)
                

                # --- Barras do Delta (A - B) ---
                chart_delta = (
                    alt.Chart(base)
                    .mark_bar()
                    .encode(
                        x=alt.X("Hora:O", title="Hora"),
                        y=alt.Y("Delta:Q", title=f"Δ ( {loja_A} - {loja_B} )"),
                        color=alt.Color("Delta:Q", scale=alt.Scale(scheme="redblue", domainMid=0), legend=None),
                        tooltip=["Hora", "Delta"]
                    )
                    .properties(height=200)
                )

                st.altair_chart(chart_lines, use_container_width=True)
                st.altair_chart(chart_delta, use_container_width=True)

                st.download_button(
                    "📥 Baixar comparação por hora (CSV)",
                    data=base.to_csv(index=False).encode("utf-8"),
                    file_name="comparacao_por_hora_AB.csv",
                    mime="text/csv"
                )

        # =====================
        # Modo 3: Agregado por hora (sobreposto, N lojas)
        # =====================
        elif modo == "Agregado por hora (sobreposto, N lojas)":

            # 1) Seleção de lojas (2+)
            lojas_default = lojas_filtro[:6]  # usa as 6 primeiras por padrão
            lojas_multi = st.multiselect(
                "Lojas para sobrepor (selecione 2 ou mais)",
                options=lojas_filtro,
                default=lojas_default,
                key="multi_sobreposto"  # evita conflito de widgets
            )

            if len(lojas_multi) < 2:
                st.info("Selecione pelo menos 2 lojas para comparar.")
            else:
                # 2) Base agregada por Loja × Hora no período filtrado
                df_multi = df_f[df_f["Loja"].isin(lojas_multi)].copy()
                hora_sum_multi = (
                    df_multi.groupby(["Loja", "Hora"], as_index=False)["Fluxo"]
                            .sum()
                            .dropna(subset=["Hora"])
                )
                hora_sum_multi["Hora"] = hora_sum_multi["Hora"].astype(int)
                hora_sum_multi["Fluxo"] = pd.to_numeric(hora_sum_multi["Fluxo"], errors="coerce").fillna(0)

                # 3) Linhas com "neon" (glow grosso + linha nítida)
                glow = (
                    alt.Chart(hora_sum_multi)
                    .mark_line(strokeWidth=8, opacity=0.35)
                    .encode(
                        x=alt.X("Hora:O", title="Hora"),
                        y=alt.Y("Fluxo:Q", title="Fluxo (soma no período)"),
                        color=alt.Color("Loja:N", title="Loja")  # paleta vem do tema
                    )
                )
                linhas = (
                    alt.Chart(hora_sum_multi)
                    .mark_line(point=True, strokeWidth=2.2)
                    .encode(
                        x=alt.X("Hora:O", title="Hora"),
                        y=alt.Y("Fluxo:Q", title="Fluxo (soma no período)"),
                        color=alt.Color("Loja:N", title="Loja"),
                        tooltip=["Loja", "Hora", alt.Tooltip("Fluxo:Q", format=",.0f")]
                    )
                )
                chart_multi = (glow + linhas).properties(height=380)
                st.altair_chart(chart_multi, use_container_width=True)

                # 4) Export
                st.download_button(
                    "📥 Baixar comparação por hora (N lojas, CSV)",
                    data=hora_sum_multi.to_csv(index=False).encode("utf-8"),
                    file_name="comparacao_por_hora_N_lojas.csv",
                    mime="text/csv"
                )
        
        
        
        # =====================
        # Modo 4: Agregado por hora (A×B, múltiplas lojas por lado)
        # =====================
        elif modo == "Agregado por hora (A×B, múltiplas lojas por lado)":

            st.caption("Selecione quantas lojas quiser em cada lado. O gráfico compara os **totais por grupo** (A vs B) por hora.")

            cga, cgb = st.columns(2)
            with cga:
                nome_A = st.text_input("Nome do Grupo A", value="Grupo A", key="nome_grupo_A_horas")
                lojas_A = st.multiselect(
                    "Lojas do Grupo A",
                    options=lojas_filtro,
                    default=lojas_filtro[:2],   # 2 primeiras como sugestão
                    key="grupoA_horas"
                )
            with cgb:
                nome_B = st.text_input("Nome do Grupo B", value="Grupo B", key="nome_grupo_B_horas")
                # sugere próximas lojas para B, sem repetir A
                sugestao_B = [l for l in lojas_filtro if l not in lojas_A][:2]
                lojas_B = st.multiselect(
                    "Lojas do Grupo B (diferentes do A)",
                    options=[l for l in lojas_filtro if l not in lojas_A],
                    default=sugestao_B,
                    key="grupoB_horas"
                )

            # validações
            if len(lojas_A) == 0 or len(lojas_B) == 0:
                st.warning("Selecione ao menos **1 loja** em cada grupo.")
            else:
                # base filtrada com as lojas A ∪ B
                df_grp = df_f[df_f["Loja"].isin(set(lojas_A) | set(lojas_B))].copy()

                # etiqueta de grupo por linha
                df_grp["Grupo"] = np.where(
                    df_grp["Loja"].isin(lojas_A), nome_A,
                    np.where(df_grp["Loja"].isin(lojas_B), nome_B, np.nan)
                )
                df_grp = df_grp.dropna(subset=["Grupo"])

                # agrega por Grupo × Hora
                hora_grp = (
                    df_grp.groupby(["Grupo", "Hora"], as_index=False)["Fluxo"].sum()
                        .dropna(subset=["Hora"])
                )
                hora_grp["Hora"] = hora_grp["Hora"].astype(int)
                hora_grp["Fluxo"] = pd.to_numeric(hora_grp["Fluxo"], errors="coerce").fillna(0)

                # KPIs de período por grupo
                tot_A = int(hora_grp.loc[hora_grp["Grupo"] == nome_A, "Fluxo"].sum())
                tot_B = int(hora_grp.loc[hora_grp["Grupo"] == nome_B, "Fluxo"].sum())
                diff_abs = tot_A - tot_B
                diff_pct = (diff_abs / tot_B * 100.0) if tot_B > 0 else np.nan

                k1, k2, k3, k4 = st.columns(4)
                with k1: st.metric(f"Fluxo — {nome_A}", f"{tot_A:,}".replace(",", "."))
                with k2: st.metric(f"Fluxo — {nome_B}", f"{tot_B:,}".replace(",", "."))
                with k3: st.metric("Δ absoluto (A - B)", f"{diff_abs:,}".replace(",", "."))
                with k4: st.metric("Δ % vs B", f"{diff_pct:.1f}%" if pd.notna(diff_pct) else "—")

                # Pivot para Delta por hora (A - B)
                base_grp = hora_grp.pivot_table(index="Hora", columns="Grupo", values="Fluxo", aggfunc="sum", fill_value=0)
                if nome_A not in base_grp.columns or nome_B not in base_grp.columns:
                    st.info("Sem dados suficientes para um dos grupos neste intervalo/horas.")
                else:
                    base_grp = base_grp.reset_index().rename(columns={nome_A: "Fluxo_A", nome_B: "Fluxo_B"})
                    base_grp["Delta"] = base_grp["Fluxo_A"] - base_grp["Fluxo_B"]
                    horas_A = int((base_grp["Delta"] > 0).sum())
                    horas_B = int((base_grp["Delta"] < 0).sum())
                    horas_emp = int((base_grp["Delta"] == 0).sum())
                    st.caption(f"🏁 Por hora no período: **{nome_A}** vence em **{horas_A}h**, **{nome_B}** vence em **{horas_B}h**, empates: **{horas_emp}h**.")

                    # Linhas com glow (neon)
                    glow = (
                        alt.Chart(hora_grp)
                        .mark_line(strokeWidth=8, opacity=0.35)
                        .encode(
                            x=alt.X("Hora:O", title="Hora"),
                            y=alt.Y("Fluxo:Q", title="Fluxo (soma no período)"),
                            color=alt.Color("Grupo:N", title="Grupo")
                        )
                    )
                    linhas = (
                        alt.Chart(hora_grp)
                        .mark_line(point=True, strokeWidth=2.2)
                        .encode(
                            x=alt.X("Hora:O", title="Hora"),
                            y=alt.Y("Fluxo:Q", title="Fluxo (soma no período)"),
                            color=alt.Color("Grupo:N", title="Grupo"),
                            tooltip=["Grupo", "Hora", alt.Tooltip("Fluxo:Q", format=",.0f")]
                        )
                    )
                    st.altair_chart((glow + linhas).properties(height=340), use_container_width=True)

                    # Barras do Delta (A - B)
                    chart_delta = (
                        alt.Chart(base_grp)
                        .mark_bar()
                        .encode(
                            x=alt.X("Hora:O", title="Hora"),
                            y=alt.Y("Delta:Q", title=f"Δ ( {nome_A} - {nome_B} )"),
                            color=alt.Color("Delta:Q", scale=alt.Scale(scheme="redblue", domainMid=0), legend=None),
                            tooltip=["Hora", "Delta"]
                        )
                        .properties(height=220)
                    )
                    st.altair_chart(chart_delta, use_container_width=True)

                    # Export
                    st.download_button(
                        "📥 Baixar A×B por hora (grupos, CSV)",
                        data=hora_grp.to_csv(index=False).encode("utf-8"),
                        file_name="comparacao_AxB_grupos_por_hora.csv",
                        mime="text/csv"
                    )

                    # Mostrar composição dos grupos (opcional)
                    st.caption("Composição dos grupos:")
                    compA = pd.DataFrame({"Grupo": nome_A, "Loja": lojas_A})
                    compB = pd.DataFrame({"Grupo": nome_B, "Loja": lojas_B})
                    st.dataframe(pd.concat([compA, compB], ignore_index=True), use_container_width=True, height=200)


        # =====================
        # Modo 5: Evolução diária (A×B, múltiplas lojas por lado)
        # =====================
        elif modo == "Evolução diária (A×B, múltiplas lojas por lado)":

            st.caption("Agrega as lojas de cada grupo por **dia** e compara as curvas A vs B.")

            cga, cgb = st.columns(2)
            with cga:
                nome_A = st.text_input("Nome do Grupo A", value="Grupo A", key="nome_grupo_A_dia")
                lojas_A = st.multiselect(
                    "Lojas do Grupo A",
                    options=lojas_filtro,
                    default=lojas_filtro[:2],
                    key="grupoA_dia"
                )
            with cgb:
                nome_B = st.text_input("Nome do Grupo B", value="Grupo B", key="nome_grupo_B_dia")
                sugestao_B = [l for l in lojas_filtro if l not in lojas_A][:2]
                lojas_B = st.multiselect(
                    "Lojas do Grupo B (diferentes do A)",
                    options=[l for l in lojas_filtro if l not in lojas_A],
                    default=sugestao_B,
                    key="grupoB_dia"
                )

            if len(lojas_A) == 0 or len(lojas_B) == 0:
                st.warning("Selecione ao menos **1 loja** em cada grupo.")
            else:
                df_grp = df_f[df_f["Loja"].isin(set(lojas_A) | set(lojas_B))].copy()
                df_grp["Grupo"] = np.where(
                    df_grp["Loja"].isin(lojas_A), nome_A,
                    np.where(df_grp["Loja"].isin(lojas_B), nome_B, np.nan)
                )
                df_grp = df_grp.dropna(subset=["Grupo"])

                dia_grp = (
                    df_grp.groupby(["Grupo", "Data"], as_index=False)["Fluxo"].sum()
                        .sort_values(["Grupo", "Data"])
                )
                dia_grp["Fluxo"] = pd.to_numeric(dia_grp["Fluxo"], errors="coerce").fillna(0)
                dia_grp["Data"] = pd.to_datetime(dia_grp["Data"], errors="coerce")

                # Linhas com glow (neon)
                glow_d = (
                    alt.Chart(dia_grp)
                    .mark_line(strokeWidth=8, opacity=0.35)
                    .encode(
                        x=alt.X("Data:T", title="Data"),
                        y=alt.Y("Fluxo:Q", title="Fluxo (soma diária)"),
                        color=alt.Color("Grupo:N", title="Grupo")
                    )
                )
                linhas_d = (
                    alt.Chart(dia_grp)
                    .mark_line(point=True, strokeWidth=2.2)
                    .encode(
                        x=alt.X("Data:T", title="Data"),
                        y=alt.Y("Fluxo:Q", title="Fluxo (soma diária)"),
                        color=alt.Color("Grupo:N", title="Grupo"),
                        tooltip=["Grupo", "Data", alt.Tooltip("Fluxo:Q", format=",.0f")]
                    )
                )
                st.altair_chart((glow_d + linhas_d).properties(height=360), use_container_width=True)

                # Export
                st.download_button(
                    "📥 Baixar A×B diário (grupos, CSV)",
                    data=dia_grp.to_csv(index=False).encode("utf-8"),
                    file_name="comparacao_AxB_grupos_diario.csv",
                    mime="text/csv"
                )
        
        
        

        
        # =====================
        # Modo 2: Evolução diária (A vs B)
        # =====================
        else:
            dia_sum = agg_por_dia(df_AB)
            base_dia = dia_sum.pivot_table(index="Data", columns="Loja", values="Fluxo", aggfunc="sum", fill_value=0)
            if (loja_A not in base_dia.columns) or (loja_B not in base_dia.columns):
                st.info("Sem dados diários suficientes para uma das lojas.")
            else:
                base_dia = base_dia.reset_index().rename(columns={loja_A: "Fluxo_A", loja_B: "Fluxo_B"})
                base_dia["Delta"] = base_dia["Fluxo_A"] - base_dia["Fluxo_B"]

                # Derrete no pandas (long)
                long_dia = base_dia.melt(
                    id_vars=["Data"],
                    value_vars=["Fluxo_A", "Fluxo_B"],
                    var_name="Serie",
                    value_name="Fluxo"
                )
                long_dia["Serie"] = long_dia["Serie"].map({"Fluxo_A": loja_A, "Fluxo_B": loja_B})
                long_dia["Fluxo"] = pd.to_numeric(long_dia["Fluxo"], errors="coerce").fillna(0)
                long_dia["Data"] = pd.to_datetime(long_dia["Data"], errors="coerce")

                chart_daily = (
                    alt.Chart(long_dia)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("Data:T", title="Data"),
                        y=alt.Y("Fluxo:Q", title="Fluxo (soma diária)"),
                        color=alt.Color("Serie:N", title="Loja", scale=alt.Scale(range=["#1f77b4", "#ff7f0e"])),
                        tooltip=["Data", "Serie", "Fluxo"]
                    )
                    .properties(height=320)
                )
                st.altair_chart(chart_daily, use_container_width=True)

                st.download_button(
                    "📥 Baixar comparação diária (CSV)",
                    data=base_dia.to_csv(index=False).encode("utf-8"),
                    file_name="comparacao_diaria_AB.csv",
                    mime="text/csv"
                )
                




# -------------------------------------------
# 📊 Small multiples por hora (N lojas)
# -------------------------------------------
st.markdown("---")
st.header("📊 Small multiples por hora (N lojas)")

if df_f.empty:
    st.info("Ajuste os filtros de período/lojas/horas para visualizar.")
else:
    # --- Controles de seleção ---
    csel1, csel2, csel3 = st.columns([2, 2, 2])
    with csel1:
        modo_sel = st.radio(
            "Seleção de lojas",
            options=["Top N por fluxo no período", "Seleção manual"],
            index=0,
            horizontal=False
        )
    with csel2:
        top_n = st.slider("Top N (por fluxo no período)", min_value=2, max_value=12, value=6, step=1)
    with csel3:
        usar_normalizacao = st.checkbox(
            "Normalizar por hora (% vs baseline da hora por loja)",
            value=False,
            help="Compara o volume observado com o 'esperado' (média da mesma hora na própria loja) no período."
        )

    # --- Base de agregação por dia/hora (para normalização robusta) ---
    # Fluxo diário por Loja x Data x Hora (no período filtrado)
    by_ldh = (
        df_f.groupby(["Loja", "ID_Loja", "Data", "Hora"], as_index=False)["Fluxo"]
            .sum()
            .dropna(subset=["Hora"])
    )
    by_ldh["Hora"] = by_ldh["Hora"].astype(int)
    by_ldh["Fluxo"] = pd.to_numeric(by_ldh["Fluxo"], errors="coerce").fillna(0)

    # --- Soma no período por Loja x Hora (para os gráficos small multiples) ---
    soma_lh = (
        by_ldh.groupby(["Loja", "ID_Loja", "Hora"], as_index=False)["Fluxo"]
              .sum()
    )  # S = soma dos dias (Loja, Hora)

    # --- Total por loja (para ranquear Top N) ---
    tot_loja = df_f.groupby(["Loja", "ID_Loja"], as_index=False)["Fluxo"].sum().rename(columns={"Fluxo": "Fluxo_total"})

    # Seleção de lojas
    lojas_disponiveis = (
        tot_loja.sort_values("Fluxo_total", ascending=False)["Loja"]
                .tolist()
    )
    if modo_sel == "Top N por fluxo no período":
        lojas_escolhidas = lojas_disponiveis[:top_n]
    else:
        lojas_escolhidas = st.multiselect(
            "Escolha as lojas para comparar",
            options=lojas_disponiveis,
            default=lojas_disponiveis[:min(top_n, len(lojas_disponiveis))]
        )
    if not lojas_escolhidas:
        st.warning("Selecione ao menos uma loja.")
        st.stop()

    soma_lh_sel = soma_lh[soma_lh["Loja"].isin(lojas_escolhidas)].copy()

    # --- Cálculo do baseline por hora (média diária da hora) e normalização ---
    # baseline_hora = média do Fluxo por (Loja, Hora) ao longo das datas
    base_mean = (
        by_ldh.groupby(["Loja", "Hora"], as_index=False)["Fluxo"].mean()
              .rename(columns={"Fluxo": "baseline_hora"})
    )
    # n_dias por (Loja, Hora) observado no filtro (contando dias com registro)
    n_dias = (
        by_ldh.groupby(["Loja", "Hora"], as_index=False)["Data"].nunique()
              .rename(columns={"Data": "n_dias"})
    )

    # Une baseline e nº de dias à soma no período
    soma_lh_sel = (
        soma_lh_sel
        .merge(base_mean, on=["Loja", "Hora"], how="left")
        .merge(n_dias, on=["Loja", "Hora"], how="left")
    )
    soma_lh_sel["baseline_hora"] = pd.to_numeric(soma_lh_sel["baseline_hora"], errors="coerce")
    soma_lh_sel["n_dias"] = pd.to_numeric(soma_lh_sel["n_dias"], errors="coerce")
    soma_lh_sel["esperado"] = soma_lh_sel["baseline_hora"] * soma_lh_sel["n_dias"]

    # % desvio vs esperado da própria hora na loja
    soma_lh_sel["norm_pct"] = np.where(
        soma_lh_sel["esperado"] > 0,
        (soma_lh_sel["Fluxo"] / soma_lh_sel["esperado"] - 1.0) * 100.0,
        np.nan
    )

    # --- Dataset para o gráfico ---
    plot_col_y = "norm_pct" if usar_normalizacao else "Fluxo"
    titulo_y = "Desvio vs baseline da hora (%)" if usar_normalizacao else "Fluxo (soma no período)"

    # Evita linhas quebradas por NaN e garante tipo
    soma_lh_sel["Hora"] = soma_lh_sel["Hora"].astype(int)
    soma_lh_sel["Fluxo"] = pd.to_numeric(soma_lh_sel["Fluxo"], errors="coerce").fillna(0)

    # Pequena ordenação para estética
    soma_lh_sel = soma_lh_sel.sort_values(["Loja", "Hora"])

    # --- Small multiples (facet por loja) ---
    chart_sm = (
        alt.Chart(soma_lh_sel)
        .mark_line(point=True)
        .encode(
            x=alt.X("Hora:O", title="Hora"),
            y=alt.Y(f"{plot_col_y}:Q", title=titulo_y),
            color=alt.value("#1f77b4"),
            tooltip=["Loja", "Hora", alt.Tooltip("Fluxo:Q", format=",.0f"),
                     alt.Tooltip("baseline_hora:Q", title="Baseline hora", format=",.1f"),
                     alt.Tooltip("n_dias:Q", title="Dias (hora)", format=",.0f"),
                     alt.Tooltip("norm_pct:Q", title="Desvio %", format=".1f")]
        )
        .properties(height=160)
        .facet(row=alt.Row("Loja:N", header=alt.Header(title="Lojas", labelAngle=0)))
    )
    st.altair_chart(chart_sm, use_container_width=True)

    # Exporta o dataset usado no gráfico
    st.download_button(
        "📥 Baixar (Loja × Hora) — com baseline e normalização",
        data=soma_lh_sel.to_csv(index=False).encode("utf-8"),
        file_name="small_multiples_por_hora.csv",
        mime="text/csv"
    )

    # -------------------------------------------
    # 🏁 Pódio por hora (Top 3 lojas em cada hora)
    # -------------------------------------------
    st.subheader("🏁 Pódio por horário (Top 3)")

    # Usamos a soma no período por (Loja, Hora) restrita às lojas escolhidas
    podio_base = soma_lh[soma_lh["Loja"].isin(lojas_escolhidas)].copy()

    # Rank por hora
    podio = (
        podio_base
        .assign(rank=lambda d: d.groupby("Hora")["Fluxo"].rank(method="first", ascending=False))
        .query("rank <= 3")
        .sort_values(["Hora", "rank"])
    )

    # Tabela do pódio
    st.dataframe(
        podio.rename(columns={"Fluxo": "Fluxo (soma no período)"}),
        use_container_width=True,
        height=360
    )

    # Gráfico: barras por hora (Top 3)
    chart_podio = (
        alt.Chart(podio)
        .mark_bar()
        .encode(
            x=alt.X("Hora:O", title="Hora"),
            y=alt.Y("Fluxo:Q", title="Fluxo (soma no período)"),
            color=alt.Color("Loja:N", title="Loja"),
            tooltip=["Hora", "Loja", alt.Tooltip("Fluxo:Q", title="Fluxo", format=",.0f"), "rank"]
        )
        .properties(height=320)
    )
    st.altair_chart(chart_podio, use_container_width=True)

    # Export CSV do pódio
    st.download_button(
        "📥 Baixar pódio por hora (Top 3, CSV)",
        data=podio.to_csv(index=False).encode("utf-8"),
        file_name="podio_por_hora_top3.csv",
        mime="text/csv"
    )
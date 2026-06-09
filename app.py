import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# =========================================================
# WARNA KONSISTEN PER AGENCY (dipakai di semua tab)
# =========================================================
COLOR_MAP = {
    'Subway':           '#1f77b4',  # biru tua
    'Bus':              '#ff7f0e',  # orange
    'BT':               '#2ca02c',  # hijau
    'LIRR':             '#d62728',  # merah
    'MNR':              '#9467bd',  # ungu
    'SIR':              '#8c564b',  # coklat
    'MTA Consolidated': '#7f7f7f',  # abu-abu
}

# =========================================================
# 1. LOAD DATA
# =========================================================

@st.cache_data
def load_projection_data():
    target_file = "Data Proyeksi Pemulihan Penumpang MTA (McKinsey).csv"
    if os.path.exists(target_file):
        df = pd.read_csv(target_file)
    else:
        st.error(f"❌ File '{target_file}' tidak ditemukan!")
        st.stop()

    df['Month'] = pd.to_datetime(df['Month']).dt.to_period('M').dt.to_timestamp()
    if df['Recovery'].max() <= 1.0:
        df['Recovery'] = df['Recovery'] * 100
    df['Revenue_Gap_Pct'] = 100 - df['Recovery']
    return df


@st.cache_data
def load_actual_data():
    actual_file = "Data Aktual Penumpang MTA.csv"
    if not os.path.exists(actual_file):
        return None

    df_act = pd.read_csv(actual_file)
    df_act['Count'] = df_act['Count'].astype(str).str.replace(',', '').astype(float)
    df_act['Month'] = pd.to_datetime(df_act['Date']).dt.to_period('M').dt.to_timestamp()
    df_act = df_act.rename(columns={'Mode': 'Agency'})

    valid_modes = ['Subway', 'Bus', 'LIRR', 'MNR', 'BT', 'SIR']
    df_act = df_act[df_act['Agency'].isin(valid_modes)]

    baselines = {
        'Subway': 5500000,
        'Bus':    2000000,
        'LIRR':    300000,
        'MNR':     170000,
        'BT':      800000,
        'SIR':     10000,
    }

    df_act['Recovery'] = df_act.apply(
        lambda r: (r['Count'] / baselines.get(r['Agency'], 1_000_000)) * 100,
        axis=1
    )

    df_monthly = (
        df_act.groupby(['Month', 'Agency'])['Recovery']
        .mean()
        .reset_index()
    )
    df_monthly['Source'] = 'MTA Actual'
    df_monthly['Projection'] = 'Actual'
    return df_monthly


# =========================================================
# 2. APP SETUP
# =========================================================
st.set_page_config(page_title="EL5069 - MTA Dashboard", layout="wide", page_icon="🚇")

st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

df_proj = load_projection_data()
df_act  = load_actual_data()

# =========================================================
# 3. SIDEBAR
# =========================================================
st.sidebar.title("🛠️ Project EL5069")
st.sidebar.markdown("**Ardiansah - Data Science & Web Tech**")

all_agencies = sorted(df_proj['Agency'].unique().tolist())
default_agencies = [a for a in ['Subway', 'Bus', 'BT'] if a in all_agencies]
if not default_agencies:
    default_agencies = all_agencies[:3]

selected_agencies = st.sidebar.multiselect(
    "Pilih Moda Transportasi", all_agencies, default=default_agencies
)

scenario = st.sidebar.selectbox(
    "Skenario Proyeksi Utama", df_proj['Projection'].unique()
)

show_actual = st.sidebar.checkbox(
    "Tampilkan Data Aktual MTA", value=True,
    disabled=(df_act is None)
)
if df_act is None:
    st.sidebar.warning("⚠️ File aktual tidak ditemukan.")

# =========================================================
# 4. FILTER DATA
# =========================================================
proj_filtered = df_proj[
    (df_proj['Agency'].isin(selected_agencies)) &
    (df_proj['Projection'] == scenario)
]

# =========================================================
# 5. MAIN LAYOUT
# =========================================================
st.title("🚇 MTA Passenger Recovery Analysis")
tab_viz, tab_stats, tab_finance = st.tabs([
    "📈 Visualisasi Tren",
    "🧪 Analitik Statistik",
    "💰 Simulasi Finansial"
])

# =========================================================
# TAB 1 — VISUALISASI PERBANDINGAN
# =========================================================
with tab_viz:
    if not proj_filtered.empty:
        col1, col2 = st.columns([3, 1])
        with col1:
            # Bangun figure manual agar warna & legenda sepenuhnya terkontrol
            fig = go.Figure()

            # Proyeksi McKinsey — garis putus-putus
            for agency in selected_agencies:
                agency_proj = proj_filtered[proj_filtered['Agency'] == agency]
                if agency_proj.empty:
                    continue
                fig.add_trace(go.Scatter(
                    x=agency_proj['Month'],
                    y=agency_proj['Recovery'],
                    mode='lines+markers',
                    name=agency,
                    legendgroup=agency,
                    line=dict(
                        color=COLOR_MAP.get(agency, '#333333'),
                        dash='dash',
                        width=2
                    ),
                    marker=dict(size=4),
                    showlegend=True
                ))

            # Data Aktual MTA — garis tebal solid, warna sama per agency
            if show_actual and df_act is not None:
                act_filtered = df_act[df_act['Agency'].isin(selected_agencies)]
                for agency in selected_agencies:
                    agency_act = act_filtered[act_filtered['Agency'] == agency]
                    if agency_act.empty:
                        continue
                    fig.add_trace(go.Scatter(
                        x=agency_act['Month'],
                        y=agency_act['Recovery'],
                        mode='lines+markers',
                        name=f"Actual: {agency}",
                        legendgroup=f"actual_{agency}",
                        line=dict(
                            color=COLOR_MAP.get(agency, '#333333'),
                            dash='solid',
                            width=3
                        ),
                        marker=dict(size=4),
                        showlegend=True
                    ))

            # Garis referensi 100%
            fig.add_hline(
                y=100, line_dash='dot', line_color='red',
                annotation_text='Level 2019 (100%)',
                annotation_position='top right'
            )

            fig.update_layout(
                title=f"Tren Pemulihan Penumpang (Skenario: {scenario})",
                xaxis_title='Month',
                yaxis_title='Ridership % vs 2019',
                legend=dict(orientation='v', x=1.01),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info(
                "💡 **Legenda:** Garis **putus-putus** = Proyeksi McKinsey | "
                "Garis **tebal solid** = Data Aktual MTA | "
                "Garis **merah titik-titik** = Level pre-pandemi 2019 | "
                "Warna sama = agency yang sama"
            )

        with col2:
            st.write("### Key Metrics")
            latest_proj_date = proj_filtered['Month'].max()
            latest_proj_avg  = proj_filtered[proj_filtered['Month'] == latest_proj_date]['Recovery'].mean()
            st.metric(f"Avg. Recovery Proyeksi ({latest_proj_date.year})", f"{latest_proj_avg:.1f}%")

            if show_actual and df_act is not None:
                act_filtered = df_act[df_act['Agency'].isin(selected_agencies)]
                if not act_filtered.empty:
                    latest_act_date = act_filtered['Month'].max()
                    latest_act_avg  = act_filtered[act_filtered['Month'] == latest_act_date]['Recovery'].mean()
                    delta = latest_act_avg - latest_proj_avg
                    st.metric(
                        f"Avg. Recovery Aktual ({latest_act_date.strftime('%b %Y')})",
                        f"{latest_act_avg:.1f}%",
                        delta=f"{delta:+.1f}% vs Proyeksi",
                        delta_color="normal"
                    )
                    st.caption("**(+) = Aktual lebih baik dari proyeksi**")
    else:
        st.warning("Silakan pilih moda transportasi.")

# =========================================================
# TAB 2 — ANALITIK STATISTIK
# =========================================================
with tab_stats:
    st.subheader("Analisis Volatilitas & Ketidakpastian")

    if selected_agencies:
        # Spread Chart
        spread_df = (
            df_proj[df_proj['Agency'].isin(selected_agencies)]
            .groupby(['Month', 'Agency'])['Recovery']
            .agg(['min', 'max'])
            .reset_index()
        )
        spread_df['Spread'] = spread_df['max'] - spread_df['min']
        fig_spread = px.area(
            spread_df, x='Month', y='Spread', color='Agency',
            title="Rentang Ketidakpastian (Selisih Best vs Worst Case)",
            color_discrete_map=COLOR_MAP
        )
        st.plotly_chart(fig_spread, use_container_width=True)

        # Tabel Deskriptif
        with st.expander("📊 Lihat Tabel Statistik Deskriptif (Akurat per Agency)", expanded=True):
            proj_stats = df_proj[df_proj['Agency'].isin(selected_agencies)][['Agency', 'Recovery']].copy()
            proj_stats['Source'] = 'McKinsey Projection'

            all_stats = proj_stats.copy()
            if show_actual and df_act is not None:
                act_stats = df_act[df_act['Agency'].isin(selected_agencies)][['Agency', 'Recovery']].copy()
                act_stats['Source'] = 'MTA Actual'
                all_stats = pd.concat([proj_stats, act_stats], ignore_index=True)

            stats_df = (
                all_stats.groupby(['Agency', 'Source'])['Recovery']
                .describe()
                .round(2)
            )
            stats_df['count'] = stats_df['count'].astype(int)
            stats_df.rename(columns={
                'count': 'Data Points', 'mean': 'Rata-rata (%)', 'std': 'Std Dev',
                'min': 'Min (%)', '25%': 'Q1 (25%)', '50%': 'Median (%)',
                '75%': 'Q3 (75%)', 'max': 'Max (%)'
            }, inplace=True)

            st.dataframe(
                stats_df.style
                .background_gradient(cmap='Blues', axis=0)
                .format("{:.2f}", subset=stats_df.columns[1:]),
                use_container_width=True
            )

        # MAE Akurasi
        if show_actual and df_act is not None:
            st.write("### 🎯 Akurasi Proyeksi McKinsey vs Realita")
            act_filtered = df_act[df_act['Agency'].isin(selected_agencies)]
            merged = pd.merge(
                proj_filtered[['Month', 'Agency', 'Recovery']].rename(columns={'Recovery': 'Proj'}),
                act_filtered[['Month', 'Agency', 'Recovery']].rename(columns={'Recovery': 'Actual'}),
                on=['Month', 'Agency'], how='inner'
            )
            if not merged.empty:
                merged['Error'] = merged['Actual'] - merged['Proj']
                merged['AbsError'] = merged['Error'].abs()
                mae_df = merged.groupby('Agency').agg(
                    MAE=('AbsError', 'mean'),
                    Mean_Error=('Error', 'mean')
                ).round(2).reset_index()
                mae_df['Status'] = mae_df['Mean_Error'].apply(
                    lambda x: '✅ Conservative (Aktual > Proyeksi)' if x > 0 else '⚠️ Optimistic (Aktual < Proyeksi)'
                )
                st.dataframe(mae_df, use_container_width=True)
            else:
                st.info("Tidak ada overlap bulan antara proyeksi & aktual untuk menghitung MAE.")
    else:
        st.warning("Pilih minimal satu Agency.")

# =========================================================
# TAB 3 — SIMULASI FINANSIAL
# =========================================================
with tab_finance:
    st.subheader("Simulasi Estimasi Kerugian Pendapatan")
    if not proj_filtered.empty:
        col_input, col_result = st.columns([1, 2])
        with col_input:
            annual_rev_2019 = st.number_input(
                "Target Pendapatan Tahunan 2019 ($ Billion)", value=8.0
            )
            fare_ratio = st.slider("Kontribusi Tiket (%)", 10, 100, 50)

        with col_result:
            # Buang MTA Consolidated (double counting)
            proj_individual = proj_filtered[proj_filtered['Agency'] != 'MTA Consolidated']

            avg_gap    = proj_individual['Revenue_Gap_Pct'].mean() / 100
            total_loss = annual_rev_2019 * (fare_ratio / 100) * avg_gap
            st.metric("Potensi Kerugian Tahunan (Skenario Terpilih)", f"${total_loss:.2f} Billion")
            st.caption("*MTA Consolidated dikecualikan untuk mencegah double counting.*")

            # Semua agency ditampilkan — BT muncul sebagai bar negatif (surplus)
            loss_df = proj_individual.copy()
            loss_df['Loss_Val_Monthly'] = (
                annual_rev_2019 * (fare_ratio / 100) * loss_df['Revenue_Gap_Pct'] / 100
            ) / 12

            fig_loss = px.bar(
                loss_df, x='Month', y='Loss_Val_Monthly', color='Agency',
                title="Estimasi Kerugian Bulanan ($ Billion) — Semua Agency",
                labels={'Loss_Val_Monthly': 'Kerugian ($ Billion)'},
                color_discrete_map=COLOR_MAP,
                barmode='relative'
            )
            fig_loss.add_hline(y=0, line_color='black', line_width=1)
            st.plotly_chart(fig_loss, use_container_width=True)

            # Deteksi agency yang sudah surplus
            surplus_agencies = (
                proj_individual.groupby('Agency')['Revenue_Gap_Pct']
                .mean()
                .loc[lambda x: x < 0]
                .index.tolist()
            )
            if surplus_agencies:
                st.success(
                    f"✅ **{', '.join(surplus_agencies)}** rata-rata sudah melampaui level 2019 "
                    "(bar negatif = surplus, bukan kerugian)."
                )

            st.info(
                f"💡 **Crosscheck:** ${total_loss:.2f}B ÷ 12 = "
                f"**${total_loss/12:.3f}B/bulan** rata-rata. "
                "Bar di atas 0 = masih rugi | Bar di bawah 0 = sudah surplus."
            )
    else:
        st.warning("Silakan pilih moda transportasi.")

# =========================================================
st.divider()
st.caption("EL5069 Data Science & Web Technology | Ardiansah")
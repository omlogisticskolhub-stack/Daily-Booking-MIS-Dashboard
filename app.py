from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration - Clean Dashboard
st.set_page_config(
    page_title="Daily Booking MIS Dashboard - Om Logistics", layout="wide"
)

# ==========================================
# 🔒 PASSWORD PROTECTION SYSTEM
# ==========================================
DASHBOARD_PASSWORD = st.secrets.get("DASHBOARD_PASSWORD", "Dhiraj@01072026")


def check_password():
    """Returns True if the user enters the correct password."""

    def password_entered():
        if st.session_state["entered_password"] == DASHBOARD_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["entered_password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🚛 Daily Booking MIS - Om Logistics")
            st.text_input(
                "🔒 Enter Dashboard Password to Access:",
                type="password",
                on_change=password_entered,
                key="entered_password",
            )
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🚛 Daily Booking MIS - Om Logistics")
            st.text_input(
                "🔒 Enter Dashboard Password to Access:",
                type="password",
                on_change=password_entered,
                key="entered_password",
            )
            st.error("❌ Incorrect Password! Please try again.")
        return False
    else:
        return True


if not check_password():
    st.stop()

# ==========================================
# 🎨 DASHBOARD STYLING
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        color: #0f172a !important;
    }

    .stApp {
        background-color: #f8fafc;
    }

    .hub-header {
        background-color: #ffffff;
        padding: 16px 28px;
        margin: -4rem -2rem 20px -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 3px solid #d32f2f;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .hub-title {
        font-size: 24px !important;
        font-weight: 900 !important;
        color: #d32f2f !important;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hub-subtitle {
        font-size: 13px;
        color: #475569;
        font-weight: 700;
    }

    /* Fix multiselect tag wrapping */
    .stMultiSelect div[data-baseweb="select"] {
        flex-wrap: wrap !important;
        height: auto !important;
        min-height: 42px !important;
    }

    div[data-testid="stMetric"] {
        background: #ffffff !important;
        padding: 14px 16px !important;
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        color: #0f172a !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #475569 !important;
        text-transform: uppercase;
        font-weight: 700 !important;
    }

    .section-head {
        font-size: 17px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 2px solid #d32f2f;
    }

    #MainMenu { visibility: hidden !important; }
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    </style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 🔑 Account Actions")
    if st.button("🔒 Lock Dashboard / Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

st.markdown(
    """
    <div class="hub-header">
        <div>
            <div class="hub-title"><span>🚛</span> DAILY BOOKING & DISPATCH MIS ANALYTICS</div>
            <div class="hub-subtitle">Om Logistics - Control Tower & Operations Management</div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)


def format_weight(kg_val):
    if kg_val >= 1000:
        return f"{kg_val / 1000:.2f} Ton"
    else:
        return f"{kg_val:.1f} KG"


# ==========================================
# FILE UPLOADER & DATA LOADING
# ==========================================
uploaded_file = st.file_uploader(
    "📥 Upload Daily Booking MIS Excel / CSV File", type=["xlsx", "xls", "csv"]
)

if uploaded_file is not None:
    @st.cache_data
    def load_data(file):
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        df.columns = df.columns.str.strip().str.upper()
        return df

    df_raw = load_data(uploaded_file)

    # Deduplicate based on CN Number
    cn_col = next(
        (
            c
            for c in df_raw.columns
            if "CN_CN_NO" in c or "CN_NO" in c or "DOCKET" in c
        ),
        df_raw.columns[2],
    )
    df = df_raw.drop_duplicates(subset=[cn_col]).copy()

    # Column Mapping
    dest_col = next(
        (c for c in df.columns if "DESTINATION" in c or "TODIST" in c),
        "DESTINATION",
    )
    from_col = next(
        (c for c in df.columns if "FROMSOURCE" in c or "SOURCE" in c),
        "FROMSOURCE",
    )
    date_col = next(
        (c for c in df.columns if "CN_DATE" in c or "BOOKING_DATE" in c),
        "CN_DATE",
    )
    pkg_col = next(
        (c for c in df.columns if "CN_PKG" in c or "PKG" in c or "BOX" in c),
        "CN_PKG",
    )
    wt_col = next(
        (
            c
            for c in df.columns
            if "ACTUAL_WEIGHT" in c or "WT" in c or "WEIGHT" in c
        ),
        "ACTUAL_WEIGHT",
    )
    inv_col = next(
        (c for c in df.columns if "CN_INV_VALUE" in c or "VALUE" in c),
        "CN_INV_VALUE",
    )
    cee_col = next(
        (c for c in df.columns if "CEE" in c or "CONSIGNEE" in c), "CEE"
    )
    status_col = next(
        (c for c in df.columns if "STATUS" in c), "STATUS"
    )
    reason_col = next(
        (c for c in df.columns if "REASON" in c), "REASON"
    )
    mode_col = next(
        (c for c in df.columns if "TPTR_MODE" in c or "MODE" in c),
        "TPTR_MODE",
    )
    branch_col = next(
        (c for c in df.columns if "CN_BRANCH_CODE" in c or "BRANCH" in c),
        "CN_BRANCH_CODE",
    )

    # Date formatting
    df["BOOKING_DATE_OBJ"] = pd.to_datetime(
        df[date_col], dayfirst=True, errors="coerce"
    )
    df["BOOKING_DAY"] = (
        df["BOOKING_DATE_OBJ"].dt.strftime("%d-%b-%Y").fillna("Date Missing")
    )

    # Numeric conversions
    df["PKG_NUM"] = (
        pd.to_numeric(df[pkg_col], errors="coerce").fillna(0).astype(int)
        if pkg_col
        else 0
    )
    df["WT_NUM"] = (
        pd.to_numeric(df[wt_col], errors="coerce").fillna(0).round(2)
        if wt_col
        else 0.0
    )
    df["INV_NUM"] = (
        pd.to_numeric(df[inv_col], errors="coerce").fillna(0).round(2)
        if inv_col
        else 0.0
    )

    # Status cleaning
    df["STATUS_CLEAN"] = (
        df[status_col].fillna("Pending / In Transit").astype(str)
        if status_col
        else "Pending"
    )

    kpi_container = st.container()
    st.markdown("---")

    # ==========================================
    # 🔍 FILTERS PANEL
    # ==========================================
    st.markdown("### 🔍 Filters Panel")

    dest_list = sorted(df[dest_col].dropna().astype(str).unique().tolist())
    cee_list = sorted(df[cee_col].dropna().astype(str).unique().tolist()) if cee_col else []
    mode_list = sorted(df[mode_col].dropna().astype(str).unique().tolist()) if mode_col else []
    branch_list = sorted(df[branch_col].dropna().astype(str).unique().tolist()) if branch_col else []

    if "dest_ms" not in st.session_state:
        st.session_state["dest_ms"] = dest_list
    if "cee_ms" not in st.session_state:
        st.session_state["cee_ms"] = cee_list
    if "branch_ms" not in st.session_state:
        st.session_state["branch_ms"] = branch_list

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        st.markdown("📍 **Destination Name**")
        def toggle_dest():
            if st.session_state.get("all_dest", False):
                st.session_state["dest_ms"] = dest_list
            else:
                st.session_state["dest_ms"] = []

        st.checkbox("Select All Destinations", value=True, key="all_dest", on_change=toggle_dest)
        selected_destinations = st.multiselect("Filter By Destination:", options=dest_list, key="dest_ms", label_visibility="collapsed")

    with fc2:
        st.markdown("🏢 **Consignee / CEE Name**")
        def toggle_cee():
            if st.session_state.get("all_cee", False):
                st.session_state["cee_ms"] = cee_list
            else:
                st.session_state["cee_ms"] = []

        st.checkbox("Select All CEE", value=True, key="all_cee", on_change=toggle_cee)
        selected_cees = st.multiselect("Filter By CEE:", options=cee_list, key="cee_ms", label_visibility="collapsed")

    with fc3:
        st.markdown("🏢 **Branch Code (CN_BRANCH_CODE)**")
        def toggle_branch():
            if st.session_state.get("all_branch", False):
                st.session_state["branch_ms"] = branch_list
            else:
                st.session_state["branch_ms"] = []

        st.checkbox("Select All Branches", value=True, key="all_branch", on_change=toggle_branch)
        selected_branches = st.multiselect("Filter By Branch:", options=branch_list, key="branch_ms", label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("🚛 **Transport Mode**")
        selected_modes = st.multiselect("Filter By Transport Mode:", options=mode_list, default=mode_list)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("⚡ **Delivery Status Filter**")
        status_options = ["All Status"] + sorted(df["STATUS_CLEAN"].unique().tolist())
        selected_status = st.selectbox("Status:", options=status_options, label_visibility="collapsed")

    # APPLY FILTERS
    df_filtered = df.copy()
    if selected_destinations:
        df_filtered = df_filtered[df_filtered[dest_col].astype(str).isin(selected_destinations)]
    else:
        df_filtered = df_filtered.iloc[0:0]

    if cee_col and selected_cees:
        df_filtered = df_filtered[df_filtered[cee_col].astype(str).isin(selected_cees)]
    elif cee_col:
        df_filtered = df_filtered.iloc[0:0]

    if branch_col and selected_branches:
        df_filtered = df_filtered[df_filtered[branch_col].astype(str).isin(selected_branches)]
    elif branch_col:
        df_filtered = df_filtered.iloc[0:0]

    if mode_col and selected_modes:
        df_filtered = df_filtered[df_filtered[mode_col].astype(str).isin(selected_modes)]

    if selected_status != "All Status":
        df_filtered = df_filtered[df_filtered["STATUS_CLEAN"] == selected_status]

    st.markdown("---")

    # ==========================================
    # 📊 TOP 5 KEY PERFORMANCE INDICATORS (KPIs)
    # ==========================================
    with kpi_container:
        st.markdown("### 📊 Operational Summary KPIs")

        tot_cn = len(df_filtered)
        tot_pkg = int(df_filtered["PKG_NUM"].sum())
        tot_wt_raw = df_filtered["WT_NUM"].sum()
        formatted_wt = format_weight(tot_wt_raw)
        tot_inv = df_filtered["INV_NUM"].sum()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total CNs (Unique)", f"{tot_cn:,}")
        c2.metric("Total Packages", f"{tot_pkg:,}")
        c3.metric("Total Weight Load", formatted_wt)
        c4.metric("Total Invoice Value", f"₹ {tot_inv:,.2f}")
        c5.metric("Active Filter Rows", f"{len(df_filtered):,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 📈 CHARTS & ANALYTICS SECTION
    # ==========================================
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("<div class='section-head'>📍 Top Destinations Breakdown</div>", unsafe_allow_html=True)
        if tot_cn > 0:
            dest_summary = (
                df_filtered.groupby(dest_col)
                .agg(CN_Count=(cn_col, "count"), Total_Weight=("WT_NUM", "sum"))
                .reset_index()
                .sort_values(by="CN_Count", ascending=False)
                .head(10)
            )
            fig_dest = px.bar(
                dest_summary,
                x="CN_Count",
                y=dest_col,
                orientation="h",
                text="CN_Count",
                color="CN_Count",
                color_continuous_scale="Reds",
            )
            fig_dest.update_layout(
                showlegend=False,
                height=320,
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis={"categoryorder": "total ascending"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_dest, use_container_width=True)
        else:
            st.info("No data available for chart.")

    with ch2:
        st.markdown("<div class='section-head'>⚡ Status Distribution (Weight Wise)</div>", unsafe_allow_html=True)
        if tot_cn > 0:
            status_summary = (
                df_filtered.groupby("STATUS_CLEAN")["WT_NUM"]
                .sum()
                .reset_index()
            )
            status_summary.columns = ["Status", "Total_Weight"]
            fig_status = px.pie(
                status_summary,
                names="Status",
                values="Total_Weight",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu,
            )
            fig_status.update_layout(
                height=320,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No data available for chart.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 📋 MASTER DETAILS TABLE WITH CN SEARCH
    # ==========================================
    st.markdown("<div class='section-head'>📋 Filtered Master Details Table</div>", unsafe_allow_html=True)

    # CN Search Box
    search_cn = st.text_input("🔍 Search by CN Number (Docket No):", placeholder="Enter CN No to search...")
    
    df_table = df_filtered.copy()
    if search_cn.strip():
        df_table = df_table[df_table[cn_col].astype(str).str.contains(search_cn.strip(), case=False, na=False)]

    display_cols = [
        c
        for c in [
            branch_col,
            cn_col,
            date_col,
            from_col,
            dest_col,
            cee_col,
            pkg_col,
            wt_col,
            inv_col,
            mode_col,
            status_col,
        ]
        if c in df.columns
    ]

    master_table = df_table[display_cols].copy().reset_index(drop=True)
    master_table.index = master_table.index + 1
    st.dataframe(master_table, height=350, use_container_width=True)

    # Download Button
    csv_data = master_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Filtered MIS Data (CSV)",
        data=csv_data,
        file_name="Daily_Booking_MIS_Filtered.csv",
        mime="text/csv",
    )

else:
    st.info("💡 Kripya ऊपर दिए गए **File Uploader** से अपनी **Daily Booking MIS** Excel या CSV फाइल अपलोड करें।")

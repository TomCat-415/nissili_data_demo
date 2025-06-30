# --- Imports ---
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from PIL import Image
import base64
from io import BytesIO
import io

# --- Database Connection ---
# Set up connection to SQLite database containing inventory/sales data
engine = create_engine('sqlite:///nissili_bilingual_inventory.db')

# --- Streamlit Page Config ---
st.set_page_config(page_title="NISSILI Dashboard", layout="wide")

# --- Language Selector (JP/EN toggle at very top) ---
lang = st.radio("言語 / Language", ["日本語", "English"], horizontal=True)

# --- Global Font & Style (Apple-inspired) ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family:
          -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
        color: #222;
        background: #181b20;  /* or #fff for light mode */
    }
    </style>
""", unsafe_allow_html=True)

# --- Image Utility: Convert Logo to Base64 for HTML Embedding ---
def image_to_base64(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return base64.b64encode(byte_im).decode("utf-8")

# --- Load and Prepare Logo Image ---
logo = Image.open("nissili-logo.PNG")
logo_base64 = image_to_base64(logo)

# --- Mobile-Friendly Logo + Title Section (JP/EN toggle) ---
if lang == "日本語":
    header_title = "<span style='font-size:2.3rem; font-weight:800;'>在庫・販売ダッシュボード</span><br>"
    header_subtitle = "<span style='font-size:1.1rem; color:#888;'>最新の在庫と販売データを一目で確認</span>"
else:
    header_title = "<span style='font-size:2.3rem; font-weight:800;'>Inventory & Sales Dashboard</span><br>"
    header_subtitle = "<span style='font-size:1.1rem; color:#888;'>See the latest inventory and sales data at a glance</span>"

st.markdown(
    f"""
    <div style='text-align:center; margin-bottom:2.5rem;'>
        <img src='data:image/png;base64,{logo_base64}' width='240' style='margin-bottom:1.3rem;'/>
        <div>{header_title}{header_subtitle}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Load Data From Database ---
df = pd.read_sql('SELECT * FROM inventory', engine)

# --- Language-Based Column Mapping ---
# Display different columns/labels based on JP or EN
if lang == "日本語":
    display_cols = ['日付', '顧客', '地域', '製品名', '販売数量', '単価（円）', '売上（円）', '現在庫', '要補充', '発注点', '最終補充日']
    rename_cols = {
        '日付': '日付',
        '顧客': '顧客',
        '地域': '地域',
        '製品名': '製品名',
        '販売数量': '販売数量',
        '単価（円）': '単価（円）',
        '売上（円）': '売上（円）',
        '現在庫': '現在庫',
        '要補充': '要補充',
        '発注点': '発注点',
        '最終補充日': '最終補充日'
    }
else:
    display_cols = ['Date', 'Client', 'Region', 'Product Name', 'Units Sold', 'Unit Price (¥)', 'Revenue (¥)', 'Current Stock', 'Needs Restock?', 'Reorder Level', 'Last Restock Date']
    rename_cols = {
        'Date': 'Date',
        'Client': 'Client Name',
        'Region': 'Region',
        'Product Name': 'Product Name',
        'Units Sold': 'Units Sold',
        'Unit Price (¥)': 'Unit Price (¥)',
        'Revenue (¥)': 'Revenue (¥)',
        'Current Stock': 'Current Stock',
        'Needs Restock?': 'Needs Restock?',
        'Reorder Level': 'Reorder Level',
        'Last Restock Date': 'Last Restock Date'
    }
df_display = df[display_cols].rename(columns=rename_cols)

# --- About / How To Use (Expandable Info Block) ---
if lang == "日本語":
    with st.expander("ℹ️ ダッシュボードの使い方", expanded=False):
        st.markdown("""
**NISSILI 在庫・販売ダッシュボードへようこそ！**

- **言語切り替え:** 上部のボタンで日本語と英語を切り替えできます。
- **サイドバーのフィルター:** 取引先、製品、月別にデータを絞り込み可能。
- **KPI:** 売上合計、販売数量、要補充件数、取引先数を一目で確認。
- **チャート:** 製品別販売数や月別トレンドがすぐに分かります。
- **要補充リスト:** 赤字で表示されている在庫は至急対応が必要です。
- **全在庫リスト:** 最新の在庫・販売データを検索・並べ替えできます。

**想定利用者:**  
- マネージャー、営業、物流担当者

**データ更新:**  
- 新しいデータがアップロードされるたび自動更新されます。

**サポート・お問い合わせ:**  
- メール: [thomasharuo415@gmail.com](mailto:thomasharuo415@gmail.com)

**更新履歴:**  
- 最終更新日: 2025年6月

_ご不明点はデータ担当までご連絡ください。_
""")
else:
    with st.expander("ℹ️ About / How to Use This Dashboard", expanded=False):
        st.markdown("""
**Welcome to the NISSILI Inventory & Sales Dashboard!**

- **Language Toggle:** Use the button above to switch between Japanese and English.
- **Sidebar Filters:** Narrow data by client, product, or transaction month in the left panel.
- **KPIs:** See total revenue, units sold, clients, and items needing restock at a glance.
- **Charts:** Visualize sales volume and trends to spot what’s selling and when.
- **Low Inventory:** Instantly see which items need urgent attention (highlighted in red).
- **Full Inventory Table:** Browse, sort, or search the latest inventory and sales records.

**Who is this for?**  
- Managers, sales staff, and logistics teams who want clear, up-to-date info with zero Excel headaches.

**How is it updated?**  
- Whenever new inventory or sales data is uploaded, the dashboard refreshes automatically.

**Support / Contact:**  
- Email: [thomasharuo415@gmail.com](mailto:thomasharuo415@gmail.com)

**Changelog:**  
- Last updated: June 2025

_Questions or need help? Ping your data team!_
""")

        # --- Get unique values for filters ---
if lang == "日本語":
    clients = ["すべて"] + sorted(df['顧客'].dropna().unique().tolist())
    products = ["すべて"] + sorted(df['製品名'].dropna().unique().tolist())
    months = ["すべて"] + sorted(df['日付'].dropna().astype(str).str[:7].unique().tolist())  # "YYYY-MM"
else:
    clients = ["All"] + sorted(df['Client'].dropna().unique().tolist())
    products = ["All"] + sorted(df['Product Name'].dropna().unique().tolist())
    months = ["All"] + sorted(df['Date'].dropna().astype(str).str[:7].unique().tolist())  # "YYYY-MM"

    # --- Add filter widgets ---
with st.sidebar:
    st.header("🔎 Filter Data" if lang == "English" else "🔎 データ絞り込み")
    if lang == "日本語":
        selected_client = st.selectbox("顧客で絞り込み", clients)
        selected_product = st.selectbox("製品名で絞り込み", products)
        selected_month = st.selectbox("月で絞り込み", months)
    else:
        selected_client = st.selectbox("Filter by Client", clients)
        selected_product = st.selectbox("Filter by Product", products)
        selected_month = st.selectbox("Filter by Month (YYYY-MM)", months)

    # --- Filter DataFrame based on selection ---
df_filtered = df.copy()

if lang == "日本語":
    if selected_client != "すべて":
        df_filtered = df_filtered[df_filtered['顧客'] == selected_client]
    if selected_product != "すべて":
        df_filtered = df_filtered[df_filtered['製品名'] == selected_product]
    if selected_month != "すべて":
        df_filtered = df_filtered[df_filtered['日付'].astype(str).str[:7] == selected_month]
else:
    if selected_client != "All":
        df_filtered = df_filtered[df_filtered['Client'] == selected_client]
    if selected_product != "All":
        df_filtered = df_filtered[df_filtered['Product Name'] == selected_product]
    if selected_month != "All":
        df_filtered = df_filtered[df_filtered['Date'].astype(str).str[:7] == selected_month]

# --- Map filtered DataFrame to display columns with correct language/labels for the UI ---
df_display_filtered = df_filtered[display_cols].rename(columns=rename_cols)

# --- KPI Metrics (Summary Numbers at a Glance) ---
if lang == "English":
    latest = df_filtered.sort_values('Date').groupby(['Client', 'Product Name'], as_index=False).tail(1)
    needs_restock_now = latest['Needs Restock?'].fillna('').str.lower().eq('yes').sum()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue (¥)", f"{df_filtered['Revenue (¥)'].sum():,}")
    col2.metric("📦 Total Units Sold", f"{df_filtered['Units Sold'].sum():,}")
    col3.metric("⚠️ Items Needing Restock", int(needs_restock_now))
    col4.metric("👥 Unique Clients", df['Client'].nunique())
else:
    latest_jp = df_filtered.sort_values('日付').groupby(['顧客', '製品名'], as_index=False).tail(1)
    needs_restock_now_jp = latest_jp['要補充'].fillna('').str.lower().eq('yes').sum()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 売上合計", f"{df_filtered['売上（円）'].sum():,} 円")
    col2.metric("📦 販売数量合計", f"{df_filtered['販売数量'].sum():,}")
    col3.metric("⚠️ 要補充件数", int(needs_restock_now_jp))
    col4.metric("👥 取引先数", df['顧客'].nunique())

st.divider()

# --- Sales by Product Bar Chart ---
if lang == "English":
    sales_by_product = df_filtered.groupby('Product Name', as_index=False)['Units Sold'].sum()
    sales_col = 'Units Sold'
    product_col = 'Product Name'
    chart_title = "Sales Volume by Product"
else:
    sales_by_product = df_filtered.groupby('製品名', as_index=False)['販売数量'].sum()
    sales_col = '販売数量'
    product_col = '製品名'
    chart_title = "製品別販売数量"

fig = px.bar(
    sales_by_product,
    x=product_col,
    y=sales_col,
    text=sales_col,
    title=chart_title
)
max_y = sales_by_product[sales_col].max()
fig.update_yaxes(range=[0, max_y * 1.15])
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Monthly Sales Trend (Line Chart) ---
if lang == "English":
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
    df_filtered['Month'] = df_filtered['Date'].dt.to_period('M').astype(str)
    monthly_sales = df_filtered.groupby('Month', as_index=False)['Units Sold'].sum()
    st.divider()
    st.subheader("📈 Monthly Sales Trend")
    fig_month = px.line(
        monthly_sales,
        x="Month",
        y="Units Sold",
        markers=True,
        title="Monthly Sales Trend"
    )
    fig_month.update_traces(line=dict(width=3), marker=dict(size=8))
    st.plotly_chart(fig_month, use_container_width=True)
else:
    df_filtered['日付'] = pd.to_datetime(df_filtered['日付'], format="%Y年%m月%d日")
    df_filtered['月'] = df_filtered['日付'].dt.to_period('M').astype(str)
    monthly_sales_jp = df_filtered.groupby('月', as_index=False)['販売数量'].sum()
    st.divider()
    st.subheader("📈 月別販売数量の推移")
    fig_month_jp = px.line(
        monthly_sales_jp,
        x="月",
        y="販売数量",
        markers=True,
        title="月別販売数量の推移"
    )
    fig_month_jp.update_traces(line=dict(width=3), marker=dict(size=8))
    st.plotly_chart(fig_month_jp, use_container_width=True)

st.divider()
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Current Low Inventory List (Highlights Red) ---
def highlight_low_stock(s):
    # Color the Current Stock column red, leave others alone
    return ['color: red; font-weight: bold;' if col == 'Current Stock' else '' for col in s.index]

if lang == "English":
    latest_filtered = df_filtered.sort_values('Date').groupby(['Client', 'Product Name'], as_index=False).tail(1)
    low_stock_now = latest_filtered[latest_filtered['Needs Restock?'].fillna('').str.lower() == 'yes']
    st.subheader("⚠️ Current Low Inventory List")
    styled_low = low_stock_now[['Client', 'Product Name', 'Current Stock', 'Reorder Level']].style.apply(
        lambda x: ['color: red; font-weight: bold;' if x.name == 'Current Stock' else '' for _ in x], subset=['Current Stock']
    )
    st.dataframe(styled_low, use_container_width=True, hide_index=True)

elif lang == "日本語":
    latest_filtered_jp = df_filtered.sort_values('日付').groupby(['顧客', '製品名'], as_index=False).tail(1)
    low_stock_now_jp = latest_filtered_jp[latest_filtered_jp['要補充'].fillna('').str.lower() == 'yes']
    st.subheader("⚠️ 現在の低在庫リスト")
    styled_low_jp = low_stock_now_jp[['顧客', '製品名', '現在庫', '発注点']].style.apply(
        lambda x: ['color: red; font-weight: bold;' if x.name == '現在庫' else '' for _ in x], subset=['現在庫']
    )
    st.dataframe(styled_low_jp, use_container_width=True, hide_index=True)

    # --- Simulated Email Alert for Low Stock ---
if lang == "English":
    if not low_stock_now.empty:
        st.divider()
        st.subheader("📧 Simulated Email Notification")
        st.info("This is a preview of an automated email alert triggered when stock falls below reorder level.")
        st.markdown(f"""
        **To:** inventory-team@nissili.com  
        **Subject:** 🚨 Low Stock Alert — Immediate Restock Required  
        **Body:**  

        The following products are below their reorder level:  
        **{', '.join(low_stock_now['Product Name'].unique())}**

        Please initiate restock procedures as soon as possible.  
        This alert was generated by the NISSILI Inventory Dashboard.
        """)
elif lang == "日本語":
    if not low_stock_now_jp.empty:
        st.divider()
        st.subheader("📧 メール通知シミュレーション")
        st.info("在庫が発注点を下回った際に送信される自動メール通知のプレビューです。")
        st.markdown(f"""
        **宛先:** inventory-team@nissili.com  
        **件名:** 🚨 在庫不足アラート — 補充が必要です  
        **本文:**  

        以下の製品が発注点を下回っています:  
        **{', '.join(low_stock_now_jp['製品名'].unique())}**

        至急、補充手配をお願いいたします。  
        この通知はNISSILI在庫ダッシュボードによって自動生成されました。
        """)

st.divider()
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Full Inventory Table (Filtered) ---
if lang == "日本語":
    st.subheader("📋 フィルター適用中の在庫リスト")
    st.caption("現在の条件で絞り込まれた取引、商品、在庫データを表示しています。")
else:
    st.subheader("📋 Filtered Inventory List")
    st.caption("Shows transaction, product, and stock data based on active filters.")

# Show the filtered table
st.dataframe(df_display_filtered, use_container_width=True)

# Download filtered table as Excel
excel_buffer = io.BytesIO()
df_display_filtered.to_excel(excel_buffer, index=False, engine='openpyxl')
excel_buffer.seek(0)
excel_label = "📥 Excel形式でダウンロード (フィルター適用データ)" if lang == "日本語" else "📥 Download Filtered Data as Excel"

st.download_button(
    label=excel_label,
    data=excel_buffer,
    file_name="filtered_inventory.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- All Data (Unfiltered) in Expander ---
with st.expander("全在庫データ（フィルターなし）" if lang == "日本語" else "Show All Inventory Data (Unfiltered)"):
    st.caption("すべての取引、商品、在庫データを表示します。" if lang == "日本語" else "Displays all transaction, product, and stock data (no filters).")
    st.dataframe(df_display, use_container_width=True)

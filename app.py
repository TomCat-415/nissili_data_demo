import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from PIL import Image
import base64
from io import BytesIO

# Connect to your SQLite database
engine = create_engine('sqlite:///nissili_bilingual_inventory.db')

st.set_page_config(page_title="NISSILI Dashboard", layout="wide")

# Language selector (keep at the very top)
lang = st.radio("言語 / Language", ["日本語", "English"], horizontal=True)

# --- Apple-like font/style ---
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

def image_to_base64(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return base64.b64encode(byte_im).decode("utf-8")

logo = Image.open("nissili-logo.PNG")
logo_base64 = image_to_base64(logo)

# --- Mobile-friendly stacked logo + JP/EN title section ---
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

# Query the whole inventory table
df = pd.read_sql('SELECT * FROM inventory', engine)

# Choose columns to display based on language
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

if lang == "日本語":
    with st.expander("ℹ️ ダッシュボードの使い方", expanded=False):
        st.markdown("""
        **NISSILI 在庫・販売ダッシュボードへようこそ！**

        - **言語切り替え:** 上部のボタンで日本語と英語を切り替えできます。
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

# KPI summary (English)
if lang == "English":
    latest = df.sort_values('Date').groupby(['Client', 'Product Name'], as_index=False).tail(1)
    needs_restock_now = latest['Needs Restock?'].fillna('').str.lower().eq('yes').sum()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue (¥)", f"{df['Revenue (¥)'].sum():,}")
    col2.metric("📦 Total Units Sold", f"{df['Units Sold'].sum():,}")
    col3.metric("⚠️ Items Needing Restock", int(needs_restock_now))
    col4.metric("👥 Unique Clients", df['Client'].nunique())
else:
    latest_jp = df.sort_values('日付').groupby(['顧客', '製品名'], as_index=False).tail(1)
    needs_restock_now_jp = latest_jp['要補充'].fillna('').str.lower().eq('yes').sum()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 売上合計", f"{df['売上（円）'].sum():,} 円")
    col2.metric("📦 販売数量合計", f"{df['販売数量'].sum():,}")
    col3.metric("⚠️ 要補充件数", int(needs_restock_now_jp))
    col4.metric("👥 取引先数", df['顧客'].nunique())

st.divider()

# Decide which columns to use based on language
if lang == "English":
    sales_by_product = df.groupby('Product Name', as_index=False)['Units Sold'].sum()
    sales_col = 'Units Sold'
    product_col = 'Product Name'
    chart_title = "Sales Volume by Product"
else:
    sales_by_product = df.groupby('製品名', as_index=False)['販売数量'].sum()
    sales_col = '販売数量'
    product_col = '製品名'
    chart_title = "製品別販売数量"

# Create bar chart
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

# --- Monthly Sales Trend Chart ---

if lang == "English":
    # Prepare data
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    monthly_sales = df.groupby('Month', as_index=False)['Units Sold'].sum()
    
    # Header & divider
    st.divider()
    st.subheader("📈 Monthly Sales Trend")
    
    # Plot
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
    # Prepare data
    df['日付'] = pd.to_datetime(df['日付'], format="%Y年%m月%d日")
    df['月'] = df['日付'].dt.to_period('M').astype(str)
    monthly_sales_jp = df.groupby('月', as_index=False)['販売数量'].sum()
    
    # Header & divider
    st.divider()
    st.subheader("📈 月別販売数量の推移")
    
    # Plot
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


# 2. Low Inventory List (Current)
def highlight_low_stock(s):
    # Color the Current Stock column red, leave others alone
    return ['color: red; font-weight: bold;' if col == 'Current Stock' else '' for col in s.index]

if lang == "English":
    # Already have latest from earlier KPI code
    low_stock_now = latest[latest['Needs Restock?'].fillna('').str.lower() == 'yes']
    st.subheader("⚠️ Current Low Inventory List")
    styled_low = low_stock_now[['Client', 'Product Name', 'Current Stock', 'Reorder Level']].style.apply(
        lambda x: ['color: red; font-weight: bold;' if x.name == 'Current Stock' else '' for _ in x], subset=['Current Stock']
    )
    st.dataframe(styled_low, use_container_width=True, hide_index=True)

def highlight_low_stock_jp(s):
    # Color the 現在庫 column red, leave others alone
    return ['color: red; font-weight: bold;' if col == '現在庫' else '' for col in s.index]

if lang == "日本語":
    low_stock_now_jp = latest_jp[latest_jp['要補充'].fillna('').str.lower() == 'yes']
    st.subheader("⚠️ 現在の低在庫リスト")
    styled_low_jp = low_stock_now_jp[['顧客', '製品名', '現在庫', '発注点']].style.apply(
        lambda x: ['color: red; font-weight: bold;' if x.name == '現在庫' else '' for _ in x], subset=['現在庫']
    )
    st.dataframe(styled_low_jp, use_container_width=True, hide_index=True)

st.divider()

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if lang == "日本語":
    st.subheader("📋 全在庫リスト")
    st.caption("すべての取引、商品、在庫データを表示しています。")
else:
    st.subheader("📋 Full Inventory List")
    st.caption("Displays all transaction, product, and stock data.")

st.dataframe(df_display)

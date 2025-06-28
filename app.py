import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Connect to your SQLite database
engine = create_engine('sqlite:///nissili_bilingual_inventory.db')

st.set_page_config(page_title="NISSILI Dashboard", layout="wide")

# Language selector
lang = st.radio("言語 / Language", ["日本語", "English"], horizontal=True)

if lang == "日本語":
    st.title("NISSILI 在庫・販売ダッシュボード")
else:
    st.title("NISSILI Inventory & Sales Dashboard")

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

# 1. Find current needs restock
latest = df.sort_values('Date').groupby(['Client', 'Product Name'], as_index=False).tail(1)
restock_keys = set(
    latest[latest['Needs Restock?'].fillna('').str.lower() == 'yes'][['Client', 'Product Name']]
    .apply(tuple, axis=1)
)

def highlight_current_restock(row):
    key = (row['Client'], row['Product Name'])
    if key in restock_keys and str(row['Needs Restock?']).lower() == 'yes':
        return ['color: red; font-weight: bold' if col == 'Needs Restock?' else '' for col in row.index]
    else:
        return ['' for _ in row]

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

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt
import os

# Set tema seaborn
sns.set(style='white')

# Set konfigurasi halaman streamlit
st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

# --- FUNGSI LOAD & CLEAN DATA ---
@st.cache_data
def load_data():
    # Mendapatkan path absolut dari file app.py saat ini berada
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Menggabungkan path saat ini dengan folder dataset
    # Ini akan selalu dinamis mencari folder 'Data Ecommerce' yang sejajar dengan folder 'Dashboard'
    base_path = os.path.join(current_dir, '../Data Ecommerce/')
    
    # Load Data
    orders_df = pd.read_csv(base_path + "orders_dataset.csv")
    order_items_df = pd.read_csv(base_path + "order_items_dataset.csv")
    order_payments_df = pd.read_csv(base_path + "order_payments_dataset.csv")
    products_df = pd.read_csv(base_path + "products_dataset.csv")
    category_translation_df = pd.read_csv(base_path + "product_category_name_translation.csv")
    customers_df = pd.read_csv(base_path + "customers_dataset.csv")

    # Cleaning & Merge Awal
    products_df = pd.merge(products_df, category_translation_df, how="left", on="product_category_name")
    products_df['product_category_name_english'] = products_df['product_category_name_english'].fillna('Unknown')
    
    orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"], errors='coerce')
    # Filter pesanan yang sukses (delivered) dan hapus NaT pada tanggal
    orders_df = orders_df[orders_df['order_status'] == 'delivered'].copy()
    orders_df.dropna(subset=['order_purchase_timestamp'], inplace=True)
    
    # Urutkan berdasarkan tanggal
    orders_df.sort_values(by="order_purchase_timestamp", inplace=True)
    orders_df.reset_index(inplace=True, drop=True)
    
    return orders_df, order_items_df, order_payments_df, products_df, customers_df

orders_df, order_items_df, order_payments_df, products_df, customers_df = load_data()

# --- SIDEBAR & FILTER ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Dicoding Data Analysis")
    st.markdown("**Nama:** Jibran Tsaqif") 
    
    st.markdown("---")
    st.header("Filter Data (Tahun 2018)")
    
    # Memfilter dataset khusus tahun 2018 untuk referensi batas kalender
    orders_2018_filter = orders_df[orders_df["order_purchase_timestamp"].dt.year == 2018]
    
    # Menetapkan batas minimum (1 Januari 2018) dan maksimum (transaksi terakhir di 2018)
    min_date = dt.date(2018, 1, 1)
    max_date = orders_2018_filter["order_purchase_timestamp"].max().date()
    
    # Widget kalender: hanya bisa memilih rentang waktu di dalam tahun 2018
    date_range = st.date_input(
        label='Pilih Rentang Waktu:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date] 
    )

# Memastikan rentang waktu berupa tuple dengan 2 nilai (start & end)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

# Memfilter data utama berdasarkan input kalender dari sidebar
main_orders_df = orders_df[(orders_df["order_purchase_timestamp"].dt.date >= start_date) & 
                           (orders_df["order_purchase_timestamp"].dt.date <= end_date)]

# --- PREPARASI DATAFRAME BERDASARKAN FILTER ---
# 1. Agregasi Tren (Pertanyaan 1)
order_pay_agg = order_payments_df.groupby('order_id')['payment_value'].sum().reset_index()
orders_revenue_df = pd.merge(main_orders_df, order_pay_agg, how='left', on='order_id')
orders_revenue_df['order_month'] = orders_revenue_df['order_purchase_timestamp'].dt.to_period('M').astype(str)

monthly_orders_df = orders_revenue_df.groupby('order_month').agg({
    'order_id': 'nunique',
    'payment_value': 'sum'
}).reset_index()
monthly_orders_df.rename(columns={'order_id': 'order_count', 'payment_value': 'revenue'}, inplace=True)

# 2. Agregasi Kategori Produk (Pertanyaan 2)
items_products_df = pd.merge(order_items_df, products_df, how='left', on='product_id')
orders_items_filtered = pd.merge(main_orders_df, items_products_df, how='inner', on='order_id')

category_orders_df = orders_items_filtered.groupby('product_category_name_english').agg({
    'order_id': 'nunique'
}).reset_index()
category_orders_df.rename(columns={'order_id': 'order_count'}, inplace=True)
category_orders_df = category_orders_df.sort_values(by='order_count', ascending=False)

# 3. Agregasi RFM Analysis
rfm_base_df = pd.merge(orders_revenue_df, customers_df, how="left", on="customer_id")
if not rfm_base_df.empty:
    recent_date = rfm_base_df['order_purchase_timestamp'].max() + dt.timedelta(days=1)
    rfm_df = rfm_base_df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()
    rfm_df.rename(columns={'order_purchase_timestamp': 'recency', 'order_id': 'frequency', 'payment_value': 'monetary'}, inplace=True)


# --- DASHBOARD UTAMA ---
st.title('E-Commerce Public Analytics Dashboard')
st.markdown("---")

if main_orders_df.empty:
    st.warning("Data tidak ditemukan untuk rentang waktu yang dipilih. Silakan ubah filter kalender.")
else:
    # Tampilan ringkasan metrik utama
    st.subheader('Ringkasan Performa')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_revenue = monthly_orders_df['revenue'].sum()
        st.metric("Total Pendapatan (R$)", value=f"{total_revenue:,.2f}")
    with col2:
        total_orders = monthly_orders_df['order_count'].sum()
        st.metric("Total Pesanan Terkirim", value=f"{total_orders:,}")
    with col3:
        total_customers = rfm_df['customer_unique_id'].nunique()
        st.metric("Total Pelanggan Unik", value=f"{total_customers:,}")
    
    st.markdown("---")

    # Grafik 1: Tren Pendapatan dan Pesanan
    st.subheader("Tren Pendapatan dan Pesanan Bulanan")
    st.write("Visualisasi di bawah ini menjawab **Pertanyaan Bisnis 1**: *Bagaimana tren total pendapatan (revenue) dan jumlah pesanan bulanan e-commerce?*")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig1a, ax1a = plt.subplots(figsize=(10, 6))
        sns.lineplot(x="order_month", y="revenue", data=monthly_orders_df, marker="o", color="tab:blue", linewidth=2, ax=ax1a)
        ax1a.set_title("Tren Pendapatan Bulanan", fontsize=18)
        ax1a.set_xlabel("Bulan", fontsize=15)
        ax1a.set_ylabel("Total Pendapatan (R$)", fontsize=15)
        ax1a.tick_params(axis='x', rotation=45)
        ax1a.grid(linestyle='--', alpha=0.5)
        st.pyplot(fig1a)
    
    with col_b:
        fig1b, ax1b = plt.subplots(figsize=(10, 6))
        sns.lineplot(x="order_month", y="order_count", data=monthly_orders_df, marker="o", color="#27ae60", linewidth=2, ax=ax1b)
        ax1b.set_title("Tren Jumlah Pesanan Bulanan", fontsize=18)
        ax1b.set_xlabel("Bulan", fontsize=15)
        ax1b.set_ylabel("Jumlah Pesanan", fontsize=15)
        ax1b.tick_params(axis='x', rotation=45)
        ax1b.grid(linestyle='--', alpha=0.5)
        st.pyplot(fig1b)
    
    st.markdown("---")
    
    # Grafik 2: Performa Kategori Produk
    st.subheader("Performa Kategori Produk: Terlaris vs Tersepi")
    st.write("Visualisasi di bawah ini menjawab **Pertanyaan Bisnis 2**: *Kategori produk apa saja yang menyumbang angka penjualan tertinggi dan terendah?*")
    
    col_c, col_d = st.columns(2)
    
    colors_top = ["#3498db"] + ["#d3d3d3"] * 4
    colors_bottom = ["#e74c3c"] + ["#d3d3d3"] * 4
    
    with col_c:
        fig2a, ax2a = plt.subplots(figsize=(10, 6))
        sns.barplot(x="order_count", y="product_category_name_english", data=category_orders_df.head(5), palette=colors_top, ax=ax2a)
        ax2a.set_title("5 Kategori Produk Terlaris", fontsize=18)
        ax2a.set_xlabel("Jumlah Pesanan", fontsize=15)
        ax2a.set_ylabel(None)
        st.pyplot(fig2a)
        
    with col_d:
        fig2b, ax2b = plt.subplots(figsize=(10, 6))
        sns.barplot(x="order_count", y="product_category_name_english", data=category_orders_df.tail(5).sort_values(by="order_count", ascending=True), palette=colors_bottom, ax=ax2b)
        ax2b.set_title("5 Kategori Produk Tersepi", fontsize=18)
        ax2b.set_xlabel("Jumlah Pesanan", fontsize=15)
        ax2b.set_ylabel(None)
        st.pyplot(fig2b)
        
    st.markdown("---")
    
    # Grafik 3: RFM Analysis
    st.subheader("RFM Analysis (Segmentasi Pelanggan)")
    
    fig3, ax3 = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))
    rfm_colors = ["#3498db"] * 5
    
    sns.barplot(y="recency", x="customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=rfm_colors, ax=ax3[0])
    ax3[0].set_ylabel(None)
    ax3[0].set_xlabel("Customer ID")
    ax3[0].set_title("Berdasarkan Recency (days)", fontsize=16)
    ax3[0].tick_params(axis='x', rotation=45, labelsize=8)
    
    sns.barplot(y="frequency", x="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=rfm_colors, ax=ax3[1])
    ax3[1].set_ylabel(None)
    ax3[1].set_xlabel("Customer ID")
    ax3[1].set_title("Berdasarkan Frequency", fontsize=16)
    ax3[1].tick_params(axis='x', rotation=45, labelsize=8)
    
    sns.barplot(y="monetary", x="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=rfm_colors, ax=ax3[2])
    ax3[2].set_ylabel(None)
    ax3[2].set_xlabel("Customer ID")
    ax3[2].set_title("Berdasarkan Monetary", fontsize=16)
    ax3[2].tick_params(axis='x', rotation=45, labelsize=8)
    
    st.pyplot(fig3)

   # Tambahan Kesimpulan Akhir
    st.markdown("---")
    st.subheader("Kesimpulan Akhir")
    st.write("""
    - **Menjawab Pertanyaan 1 (Tren Pendapatan & Pesanan):** Terlihat bahwa performa pendapatan dan jumlah pesanan memiliki pergerakan tren yang saling berbanding lurus. Berdasarkan data historis, terjadi tren penurunan pesanan yang cukup tajam dan konsisten ketika memasuki kuartal ketiga (bulan Juni hingga Agustus). 
    - **Menjawab Pertanyaan 2 (Performa Kategori Produk):** Terdapat ketimpangan minat produk yang sangat jelas. Kategori *health_beauty* dan *bed_bath_table* menjadi primadona utama yang menopang angka penjualan e-commerce. Sebaliknya, kategori hiburan fisik seperti *cds_dvds_musicals* berada di posisi terendah yang mengindikasikan rendahnya relevansi produk tersebut di pasar saat ini.
    """)

    # Tambahan Rekomendasi Bisnis
    st.subheader("Rekomendasi Bisnis")
    st.write("""
    1. **Antisipasi Penurunan Tren Pertengahan Tahun:** Melihat adanya tren penurunan pesanan di bulan Juni hingga Agustus, Tim Marketing direkomendasikan untuk merancang kampanye promosi khusus (seperti *Mid-Year Sale*, gratis ongkir, atau *cashback*) pada periode tersebut untuk mendongkrak dan menstabilkan penjualan.
    2. **Optimasi Inventaris & Strategi Bundling:** Tim Operasional harus memprioritaskan ketersediaan stok untuk kategori *top-tier* seperti **health_beauty** dan **bed_bath_table** agar terhindar dari *stockout*. Untuk produk *bottom-tier* seperti CD/DVD, disarankan membuat strategi *bundling* dengan produk laris agar perputaran barang di gudang tetap efisien.
    3. **Pemanfaatan RFM untuk Retensi Pelanggan:** Berdasarkan analisis RFM, perusahaan harus mempertahankan pelanggan-pelanggan di posisi puncak dengan memberikan program loyalitas eksklusif (VIP *Membership* atau *Reward Points*). Untuk pelanggan dengan skor *Recency* yang buruk (sudah lama tidak berbelanja), tim dapat mengirimkan promosi *win-back* via *email* untuk memancing mereka bertransaksi kembali.
    """)

st.caption("Dicoding Data Analysis Project - Jibran Tsaqif")
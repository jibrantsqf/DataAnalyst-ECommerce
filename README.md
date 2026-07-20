# 🛒 E-Commerce Public Analytics - Data Analysis Project

Proyek ini merupakan proyek eksplorasi dan analisis data menggunakan dataset E-Commerce publik dari Olist (platform e-commerce terbesar di Brasil). Tujuan utama dari proyek ini adalah untuk menggali wawasan bisnis (*business insights*), menganalisis tren penjualan, mengevaluasi performa produk, serta melakukan segmentasi pelanggan menggunakan teknik **RFM Analysis**.

## 📌 Business Questions
Analisis dalam proyek ini dirancang untuk menjawab pertanyaan bisnis berikut:
1. Bagaimana tren total pendapatan (*revenue*) dan jumlah pesanan bulanan e-commerce sepanjang tahun 2018?
2. Kategori produk apa saja yang menyumbang angka penjualan tertinggi dan terendah selama tahun 2018?
3. Bagaimana karakteristik segmen pelanggan terbaik berdasarkan *Recency, Frequency,* dan *Monetary* (RFM Analysis)?

## 📂 Project Structure.
├── Dashboard

│   ├── app.py

│   └── requirements.txt

├── Data Ecommerce

│   ├── customers_dataset.csv

│   ├── geolocation_dataset.csv

│   ├── order_items_dataset.csv

│   ├── order_payments_dataset.csv

│   ├── order_reviews_dataset.csv

│   ├── orders_dataset.csv

│   ├── product_category_name_translation.csv

│   ├── products_dataset.csv

│   └── sellers_dataset.csv

├── Project_Data_Analyst_E_Commerce.ipynb

└── README.md

## 🛠️ Setup Environment

Jika Anda ingin menjalankan proyek ini secara lokal di mesin Anda, ikuti langkah-langkah berikut:

**1. Clone Repositori**

git clone https://github.com/jibrantsqf/DataAnalyst-ECommerce.git

cd DataAnalyst-ECommerce

**2. Instalasi Library yang Dibutuhkan**
Pastikan Anda memiliki Python yang sudah terinstal, kemudian jalankan perintah berikut untuk menginstal dependensi:

pip install -r Dashboard/requirements.txt

*(Library utama yang digunakan: `pandas`, `matplotlib`, `seaborn`, `streamlit`)*

## 🚀 Run Streamlit App

Untuk menjalankan *dashboard* interaktif secara lokal, arahkan terminal Anda ke dalam folder `Dashboard` lalu jalankan perintah Streamlit:

cd Dashboard
streamlit run app.py

Aplikasi akan secara otomatis terbuka di *browser* Anda melalui `http://localhost:8501`.

## 🌐 Live Dashboard

Anda dapat mengakses *dashboard* interaktif yang sudah di-*deploy* melalui Streamlit Cloud pada tautan berikut:
**https://dataanalyst-ecommerce.streamlit.app/**

## 👤 Author

* **Jibran Tsaqif**
* Data Science Enthusiast | Politeknik Negeri Banyuwangi

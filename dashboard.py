# Import Library
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Load Berkas main_data.csv
all_df = pd.read_csv("main_data.csv")
# Ubah tipe data menjadi datetime
datetime_columns = ['order_purchase_timestamp', 
                    'order_approved_at', 
                    'order_delivered_carrier_date', 
                    'order_delivered_customer_date', 
                    'order_estimated_delivery_date', 
                    'review_creation_date', 
                    'review_answer_timestamp']
# Mengurutkan berdasarkan tanggal pembelian
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

# Buat tabel revenue_df
def create_revenue_df(df): 
    revenue_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    revenue_df.index = revenue_df.index.strftime('%b-%Y') # Mengubah format menjadi Bulan(3 huruf)-Tahun
    revenue_df = revenue_df.reset_index()
    revenue_df.rename(columns={
        "order_purchase_timestamp": "order_date",
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return revenue_df

# Buat tabel review_df
def create_review_df(df):
    review_df = df.groupby(by="review_score").order_id.nunique().reset_index()
    review_df.rename(columns={
        "order_id": "count",
    }, inplace=True)
    review_df['review_score'] = review_df['review_score'].astype(int)    # Convert 'review_score' column to integer

    return review_df

# Buat tabel bycity_df
def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=False).reset_index()
    bycity_df.rename(columns={
        "customer_id": "count",
    }, inplace=True)

    return bycity_df

# Buat tabel bystate_df
def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().sort_values(ascending=False).reset_index()
    bystate_df.rename(columns={
        "customer_id": "count",
    }, inplace=True)

    return bystate_df

# Buat tabel RFM
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "payment_value": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

# Mengubah data type menjadi datetime 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter Sidebar
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan foto pribadi
    st.subheader("Zada Alfarras Rasendriya (ML-28)")
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Tanggal :calendar:',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Menyesuaikan df dengan filter tanggal
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

revenue_df = create_revenue_df(main_df)
review_df = create_review_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# Mengisi Dashboard
st.title("Dashboard E-Commerce")

# Pemisahan Visualisasi dengan tab
tab1, tab2, tab3, tab4 = st.tabs([":money_with_wings: Revenue", ":people_holding_hands: Demographic", ":star: Reviews", ":bar_chart: RFM Analysis"])


# Jumlah Pesanan
with tab1:
    st.subheader(':money_with_wings: Revenue per Bulan')

    col1, col2 = st.columns(2)

    with col1:
        total_orders = revenue_df.order_count.sum()
        st.metric("Jumlah Pesanan", value=total_orders)

    with col2:
        total_revenue = format_currency(revenue_df.revenue.sum(), "BRL", locale='es_CO') 
        st.metric("Jumlah Pendapatan", value=total_revenue)

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(
        revenue_df["order_date"],
        revenue_df["order_count"],
        marker='o', 
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15, rotation=45)

    st.pyplot(fig)

# Demografi Pelanggan
with tab2:
    st.subheader(":people_holding_hands: Customer Demographics")

    # Berdasarkan Kota
    fig, ax = plt.subplots(figsize=(25, 10))

    sns.barplot(
        y="count", 
        x="customer_city",
        data=bycity_df.sort_values(by="count", ascending=False).head(10),
        palette='pastel',
        edgecolor='black',
        linewidth=1.5,
        ax=ax
    )
    ax.set_title("Jumlah Customer per Kota", loc="center", fontsize=40)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35, labelrotation=45)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

    # Berdasarkan Negara Bagian
    fig, ax = plt.subplots(figsize=(25, 10))

    sns.barplot(
        y="count", 
        x="customer_state",
        data=bystate_df.sort_values(by="count", ascending=False).head(10),
        palette='pastel',
        edgecolor='black',
        linewidth=1.5,
        ax=ax
    )
    ax.set_title("Jumlah Customer per Negara Bagian", loc="center", fontsize=40)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

# Review
with tab3:
    st.subheader(':star: Review Customer')
    fig, ax = plt.subplots(figsize=(25, 10))
    sns.barplot(
        y="count",
        x="review_score",
        data=review_df,
        edgecolor='black',
        color='lightblue'
    )

    ax.set_title("Jumlah Review", loc="center", fontsize=40)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

# RFM
with tab4:
    st.subheader(":bar_chart: Best Customer Based on RFM Analysis (customer_id)")

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 10))
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)

    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)

    with col3:
        avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL", locale='es_CO') 
        st.metric("Average Monetary", value=avg_frequency)


    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), color="lightblue", edgecolor='black', ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("customer_id", fontsize=30)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=45)
    ax[0].set_xticks([])
    ax[0].tick_params(axis='y', labelsize=30)

    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), color="lightblue", edgecolor='black', ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("customer_id", fontsize=30)
    ax[1].set_title("By Frequency", loc="center", fontsize=45)
    ax[1].set_xticks([])
    ax[1].tick_params(axis='y', labelsize=30)

    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), color="lightblue", edgecolor='black', ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("customer_id", fontsize=30)
    ax[2].set_title("By Monetary", loc="center", fontsize=45)
    ax[2].set_xticks([])
    ax[2].tick_params(axis='y', labelsize=30)

    st.pyplot(fig)

st.caption('Copyright (c) Zada Alfarras Rasendriya 2024')
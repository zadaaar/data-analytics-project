# Proyek Analisis Data ✨

## Deskripsi Proyek
Dalam proyek ini, dilakukan analisis terhadap dataset E-Commerce Publik yang bertujuan untuk menghasilkan informasi dan memberikan pemahaman terhadap dataset E-Commerce.

## Penjelasan Direktori
- /dataset: Direktori ini berisi kumpulan data yang digunakan pada proyek ini, menggunakan format .csv.
- notebook.ipynb: File ini digunakan untuk melakukan pengambilan, pengolahan, analisis, dan visualisasi data.
- main_data.csv: File ini merupakan gabungan data dari /dataset yang selanjutnya digunakan pada dashboard.py.
- dashboard.py: File ini digunakan untuk membuat dashboard menggunakan library streamlit.
- requirements.txt: File ini merupakan prasyarat yang dibutuhkan untuk menjalankan seluruh program pada direktori

## Setup environment
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install numpy pandas scipy matplotlib seaborn jupyter streamlit babel
```

## Run steamlit app
```
streamlit run dashboard.py
```


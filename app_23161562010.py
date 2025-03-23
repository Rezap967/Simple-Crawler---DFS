import requests
from bs4 import BeautifulSoup
import mysql.connector
from urllib.parse import urljoin  # Untuk menggabungkan URL dengan benar

# Koneksi ke database
conn = mysql.connector.connect(
    host='localhost',
    user='root',  # Sesuaikan dengan user MySQL Anda
    password='',  # Jika tidak ada password, biarkan kosong
    database='web_scraper'
)
cursor = conn.cursor()

# Set dasar URL server XAMPP (pastikan sesuai dengan server yang berjalan)
base_url = "http://localhost:8000/"

# Set untuk menyimpan URL yang sudah dikunjungi
visited = set()


def dfs(url):
    """ Fungsi DFS untuk merayapi halaman web """
    if url in visited:
        return
    
    visited.add(url)
    print(f"Mengunjungi: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Cek apakah request berhasil
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ambil judul dan paragraf pertama
        title = soup.title.text.strip() if soup.title else "No Title"
        paragraph = soup.p.text.strip() if soup.p else "No Content"

        # Simpan ke database
        cursor.execute("INSERT INTO pages (url, title, paragraph) VALUES (%s, %s, %s)",
                       (url, title, paragraph))
        conn.commit()

        # Cari semua link di halaman
        for link in soup.find_all('a', href=True):
            next_url = urljoin(base_url, link['href'])  # Pastikan URL yang benar
            dfs(next_url)

    except requests.exceptions.RequestException as e:
        print(f"Gagal mengakses {url}: {e}")

# Mulai dari halaman utama
dfs(base_url + "index.html")

# Tutup koneksi database setelah scraping selesai
cursor.close()
conn.close()
print("Scraping selesai dan data telah disimpan di database!")

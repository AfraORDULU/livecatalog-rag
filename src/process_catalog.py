import os
import sqlite3
import random
import pandas as pd

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "flipkart_com-ecommerce_sample.csv")
DB_PATH = os.path.join(DATA_DIR, "products.db")

def filter_and_populate_db():
    print("⏳ CSV taranıyor...")
    if not os.path.exists(CSV_PATH):
        print("❌ CSV dosyası bulunamadı!")
        return

    df = pd.read_csv(CSV_PATH)

    # Tüm tüketici elektroniği kategorilerini alıyoruz
    tech_keywords = "Mobiles & Accessories|Computers|Electronics|Audio|Headphones|Televisions|Cameras"
    tech_df = df[df["product_category_tree"].str.contains(tech_keywords, case=False, na=False)].copy()
    tech_df = tech_df.dropna(subset=["product_name", "description"])

    print(f"🎯 Toplam aktarılacak gerçek teknoloji ürünü sayısı: {len(tech_df)}")

    fast_cities_pool = [
        "İstanbul, İzmir, Ankara, Bursa, Kocaeli",
        "İstanbul, İzmir, Ankara",
        "İstanbul",
        "İzmir, Manisa, Balıkesir",
        "Tüm Türkiye (Standart Kargo)"
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        brand TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        fast_delivery_cities TEXT NOT NULL,
        specs TEXT NOT NULL
    )
    """)

    cursor.execute("DELETE FROM products")

    records = []
    # head(150) kaldırıldı; TÜM teknoloji ürünleri (1800+) SQLite'a ekleniyor
    for _, row in tech_df.iterrows():
        name = str(row["product_name"]).strip()
        cat_raw = str(row["product_category_tree"]).split(">>")
        category = cat_raw[1].replace('"', '').strip() if len(cat_raw) > 1 else "Electronics"
        brand = str(row["brand"]).strip() if pd.notna(row["brand"]) else "Genel Marka"

        # Fiyat kontrolü
        try:
            raw_p = row["discounted_price"] if pd.notna(row["discounted_price"]) else row["retail_price"]
            if pd.isna(raw_p) or str(raw_p).strip() == "" or str(raw_p).lower() == "nan":
                price = 2499.0
            else:
                price = float(str(raw_p).replace(",", "").replace("₹", "").strip())
        except:
            price = 2499.0

        stock = random.choice([0, 3, 7, 12, 25])
        fast_delivery = random.choice(fast_cities_pool)
        specs = str(row["description"]).strip()[:350]

        records.append((name, category, brand, price, stock, fast_delivery, specs))

    cursor.executemany("""
    INSERT INTO products (name, category, brand, price, stock, fast_delivery_cities, specs)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    conn.close()
    print(f"🎉 Harika! {len(records)} adet teknoloji ürünü eksiksiz olarak {DB_PATH} içine aktarıldı!")

if __name__ == "__main__":
    filter_and_populate_db()
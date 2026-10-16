import sqlite3
import os


# Veritabanı dosyasının kaydedileceği konumu belirliyoruz (data/products.db).
# os.path.join kullanmamızın sebebi: Mac, Linux ve Windows işletim sistemlerinde
# dosya yolu ayraçları (/ veya \) farklıdır. Bu fonksiyon platformdan bağımsız çalışır.
DB_PATH = os.path.join("data", "products.db")


def init_product_database():
    """
    E-ticaret ürün kataloğu için SQLite veritabanını ve tablosunu oluşturur,
    test amaçlı başlangıç verilerini tabloya ekler.
    """
    
    
    # 'data' klasörü yoksa disk üzerinde oluşturur.
    # exist_ok=True: Klasör zaten mevcutsa hata fırlatmasını engeller.
    os.makedirs("data", exist_ok=True)
    
    
    # SQLite veritabanı dosyasına bağlantı açar.
    # Eğer data/products.db dosyası diskte yoksa, bu satır çalıştığında otomatik yaratılır.
    conn = sqlite3.connect(DB_PATH)
    
    # Cursor (İmleç): Veritabanı üzerinde SQL komutlarını çalıştırmamızı sağlayan nesnedir.
    cursor = conn.cursor()

   
    # 'products' adında bir tablo oluşturuyoruz (daha önce yoksa).
    # Tablo alanları:
    # - id: Otomatik artan benzersiz birincil anahtar (Primary Key).
    # - name: Ürünün tam adı.
    # - category: Ürünün kategorisi (Kulaklık, Laptop vb.).
    # - brand: Marka adı.
    # - price: Ürün fiyatı (ondalıklı sayı - REAL).
    # - stock: Stoktaki adet sayısı (tam sayı - INTEGER).
    # - fast_delivery_cities: Ertesi gün hızlı teslimat destekleyen şehirler.
    # - specs: Teknik özellikler ve açıklamalar (arama filtresi için).
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

    
    # Bu script her çalıştırıldığında aynı ürünlerin tekrar tekrar (mükerrer)
    # eklenmesini önlemek için tabloyu sıfırlıyoruz.
    cursor.execute("DELETE FROM products")

   
    # RAG ve SQL hibrit aramalarını test edebileceğimiz gerçekçi örnek ürünler:
    # - Sony: Stokta olan ve ANC özelliği bulunan ürün.
    # - AirPods: Stoğu 0 olan (modelin 'stokta yok' uyarısı vermesini test etmek için).
    # - Dell: Yüksek fiyatlı, farklı teslimat şehirleri olan laptop.
    # - Samsung & Philips: Farklı kategorileri test etmek için monitör ve kahve makinesi.
    sample_products = [
        (
            "Sony WH-1000XM5 Kablosuz Kulaklık",
            "Kulaklık",
            "Sony",
            14500.0,
            5,  # Stokta mevcut
            "İstanbul, İzmir, Ankara",
            "Aktif gürültü engelleme (ANC), 30 saat pil ömrü, Bluetooth 5.2, LDAC desteği."
        ),
        (
            "Apple AirPods Pro 2. Nesil",
            "Kulaklık",
            "Apple",
            9800.0,
            0,  # Stok tükenme senaryosu kontrolü
            "İstanbul, İzmir",
            "H2 çip, Adaptif Şeffaf Mod, MagSafe şarj kutusu, Kişiselleştirilmiş Mekansal Ses."
        ),
        (
            "Apple İphone 18 Pro Max",
            "Telefon",
            "Apple",
            145000.0,
            10,
            "İstanbul, İzmir, Ankara",
            "A17 Pro çip, 6.7 inç Super Retina XDR ekran, 48MP kamera, 12MP telekamera, 48MP ana kamera."
        ),
        (
            "Dell XPS 13 Plus 9320",
            "Dizüstü Bilgisayar",
            "Dell",
            48500.0,
            3,
            "İstanbul, Ankara",
            "Intel Core i7-1360P, 16GB RAM, 512GB SSD, 13.4 inç OLED Dokunmatik Ekran."
        ),
        (
            "Samsung Odyssey G7 27 inç Oyuncu Monitörü",
            "Monitör",
            "Samsung",
            16200.0,
            8,
            "İstanbul, İzmir, Bursa, Ankara",
            "240Hz yenileme hızı, 1ms tepki süresi, 1000R kavisli QLED panel, WQHD çözünürlük."
        ),
        (
            "Philips LatteGo 5400 Tam Otomatik Kahve Makinesi",
            "Küçük Ev Aletleri",
            "Philips",
            21900.0,
            2,
            "İzmir, Manisa",
            "12 farklı kahve çeşidi, LatteGo süt sistemi, seramik öğütücü, dokunmatik renkli ekran."
        )
    ]

   
    # executemany metodu, listedeki tüm kayıtları tek bir SQL işlemiyle veritabanına ekler.
    # Soru işaretleri (?) 'Parameterized Query' yapısıdır; SQL Injection açıklarını önler.
    cursor.executemany("""
    INSERT INTO products (name, category, brand, price, stock, fast_delivery_cities, specs)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_products)

    
    # conn.commit(): Yapılan INSERT ve DELETE işlemlerini kalıcı olarak dosyaya yazar.
    conn.commit()
    # conn.close(): Açık olan veritabanı bağlantısını güvenle sonlandırır.
    conn.close()
    
    print(f"✅ Ürün veritabanı başarıyla oluşturuldu: {DB_PATH}")


# Bu dosya doğrudan terminalden çalıştırıldığında (python3 src/init_db.py) aşağıdaki kod çalışır.
# Dosya başka bir Python dosyasından 'import' edildiğinde fonksiyonun kendiliğinden çalışmasını engeller.
if __name__ == "__main__":
    init_product_database()
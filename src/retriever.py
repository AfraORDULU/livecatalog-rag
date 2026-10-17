import os       # İşletim sistemi dosya yollarını yönetmek için
import sqlite3  # Ürün stok ve fiyatlarının tutulduğu SQLite veritabanına bağlanmak için

# LangChain kütüphanesinden Hugging Face embedding sarmalayıcısı:
# Metinleri anlamsal sayılara (vektörlere) çeviren modeli yerel çalıştırmak için kullanılır.
from langchain_community.embeddings import HuggingFaceEmbeddings

# Daha önce ingest_docs.py ile diske kaydettiğimiz ChromaDB vektör tabanını okumak için
from langchain_community.vectorstores import Chroma


#DOSYA YOLLARI VE EMBEDDING MODEL TANIMLAMALARI

# ingest_docs.py çalıştırıldığında vektörlerin yazıldığı klasörün adı
CHROMA_PERSIST_DIR = "chroma_db"

# Ürünlerin fiyat ve stok bilgilerini tutan SQLite dosyasının yolu ("data/products.db")
DB_PATH = os.path.join("data", "products.db")

# DİKKAT: Dokümanları vektörleştirirken hangi modeli kullandıysak,
# arama yaparken de BİREBİR AYNI modeli kullanmak zorundayız.
# Aksi takdirde üretilen vektör uzayları uyuşmaz ve semantik arama çalışmaz.
EMBEDDING_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v1"


# CHROMADB VEKTÖR TABANININ YÜKLENMESİ (RAG MOTORU)


# Hugging Face modelini hafızaya alıyoruz (CPU üzerinde çalışacak şekilde)
print("🧠 Embedding modeli arama için hafızaya alınıyor...")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"device": "cpu"} # Modeli işlemcide (CPU) çalıştırır.
)

# Önceden diske kaydedilmiş ChromaDB veritabanını belleğe yüklüyoruz.
# persist_directory: Vektör dosyalarının bulunduğu klasör
# embedding_function: Kullanıcı bir soru sorduğunda o soruyu anında vektöre çevirecek model
vector_store = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=embeddings
)


def search_policy_documents(query: str, n_results: int = 2):
    """
    RAG (Retrieval) Fonksiyonu:
    Kullanıcının doğal dilde yazdığı kural/politika sorusunu alır.
    ChromaDB içinde semantik (anlamsal kosinüs benzerliği) arama yapar.
    En alakalı 'n_results' adet metin parçasını ve kaynak dosya bilgisini döndürür.
    
    Örnek Sorgu: "Kulaklık jelatini açılırsa iade olur mu?"
    """
    # similarity_search fonksiyonu arka planda iki iş yapar:
    # 1. 'query' cümlesini embedding modeline verip vektörünü çıkartır.
    # 2. ChromaDB'deki tüm parçalarla kosinüs benzerliğini hesaplayıp en yakın 'k' tanesini seçer.
    matched_docs = vector_store.similarity_search(query, k=n_results)
    
    results = []
    for doc in matched_docs:
        results.append({
            "content": doc.page_content,                          # İlgili metin parçası (paragraf)
            "source": doc.metadata.get("source", "Bilinmeyen Doküman")  # Parçanın geldiği dosya (örn: iade_politikasi.md)
        })
    return results



# SQL VERİTABANI ARAMASI (DİNAMİK ÜRÜN MOTORU)


def search_products_db(keyword: str):
    """
    SQL Arama Fonksiyonu:
    Kullanıcının ilgilendiği ürün, marka veya kategoriyi SQLite veritabanında arar.
    Anlık stok, fiyat ve hızlı teslimat şehirlerini liste olarak döndürür.
    
    Örnek Sorgu: "kulaklık", "sony", "laptop", "iphone"
    """
    # Veritabanına bağlantı aç
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # SQL 'LIKE' araması için aranan kelimenin sağına ve soluna '%' işareti koyuyoruz.
    # Bu sayede kelime cümlenin veya ürün adının neresinde geçerse geçsin eşleşir.
    search_term = f"%{keyword}%"
    
    # name, category veya specs (teknik özellikler) sütunlarında esnek arama yapıyoruz:
    query = """
    SELECT name, category, brand, price, stock, fast_delivery_cities, specs
    FROM products
    WHERE name LIKE ? OR category LIKE ? OR specs LIKE ?
    """
    
    # Güvenlik standardı: SQL Injection açıklarını önlemek için parametreleri tuple olarak geçiyoruz
    cursor.execute(query, (search_term, search_term, search_term))
    rows = cursor.fetchall()
    
    # Bağlantıyı kapatıp kaynakları serbest bırakıyoruz
    conn.close()

    # Dönen ham SQL satırlarını okunabilir bir Python sözlük (dictionary) listesine çeviriyoruz
    products = []
    for row in rows:
        products.append({
            "name": row[0],                  # Ürün adı
            "category": row[1],              # Kategori
            "brand": row[2],                 # Marka
            "price": row[3],                 # Fiyat (TL)
            "stock": row[4],                 # Anlık stok adedi
            "fast_delivery_cities": row[5],  # Hızlı kargonun geçerli olduğu şehirler
            "specs": row[6]                  # Teknik özellikler
        })
    return products


# 4. KENDİNİ TEST ETME BLOĞU (LOCAL TEST)

# Bu dosya doğrudan terminalden 'python3 src/retriever.py' diye çalıştırıldığında
# yazdığımız iki arama fonksiyonunun da sorunsuz çalışıp çalışmadığını test eder.
if __name__ == "__main__": # bu testlerin yalnızca siz bu dosyayı doğrudan çalıştırdığınızda devreye girmesini sağlar
    print("\n" + "="*50)
    print("🔍 1. RAG POLİTİKA ARAMASI TESTİ")
    print("Sorgu: 'kulaklık ambalajı açılırsa iade edilir mi?'")
    print("="*50)
    policy_results = search_policy_documents("kulaklık ambalajı açılırsa iade edilir mi?", n_results=1)
    for res in policy_results:
        print(f"📄 Bulunan Belge: {res['source']}")
        print(f"📝 İçerik: {res['content']}\n")

    print("="*50)
    print("📦 2. SQL ÜRÜN VERİTABANI ARAMASI TESTİ")
    print("Aranan Kelime: 'kulaklık'")
    print("="*50)
    product_results = search_products_db("kulaklık")
    for prod in product_results:
        print(f"🔹 Ürün: {prod['name']}")
        print(f"   Fiyat: {prod['price']} TL | Stok: {prod['stock']} adet")
        print(f"   Hızlı Teslimat İlleri: {prod['fast_delivery_cities']}")
        print(f"   Özellikler: {prod['specs']}\n")
    print("="*50)
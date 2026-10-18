#LiveCatalogRAG: Hibrit E-Ticaret Destek Asistanı

🛒 LiveCatalog-RAG: Hibrit E-Ticaret Destek Asistanı
Deterministik SQL katalog sorgulamaları ile yoğun vektör benzerliği (RAG) mimarisini tek bir yapay zekâ katmanında harmanlayan, halüsinasyonsuz müşteri destek motoru.

📌 Genel Bakış ve Problem Tanımı
Geleneksel Retrieval-Augmented Generation (RAG) mimarileri, PDF gibi statik belgeler üzerinde anlamsal arama yaparken başarılı olsa da dinamik stok, değişen fiyatlar ve lokasyon bazlı teslimat rotaları gibi deterministik verilere ulaştığında yetersiz kalır ve sıklıkla halüsinasyon üretir.
LiveCatalog-RAG, bu sorunu çift yönlü hibrit bir veri hattıyla çözer:
📄 Yapılandırılmamış Veri (Unstructured Data): Teknosa'nın resmi iade, cayma hakkı ve teslimat prosedürleri vektörleştirilerek anlamsal aramaya açılır.
🗄️ Yapılandırılmış Veri (Structured Data): 1.800'ün üzerinde tüketici elektroniği ürününün yer aldığı ilişkisel SQL veritabanı doğrudan sorgulanır.
🧠 LLM Orkestrasyonu: Her iki kaynaktan süzülen bağlam birleştirilerek kullanıcıya doğrulanmış ve kaynak referanslı yanıtlar sunulur.
🏗️ Sistem Mimarisi
Kullanıcı sorgusu sisteme girdiği andan itibaren işletilen veri akışı:
                      ┌────────────────────────┐
                      │   Kullanıcı Sorgusu    │
                      └───────────┬────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌─────────────────────────┐                     ┌─────────────────────┐
│  Varlık Çıkarıcı (NLP)  │                     │ Dense Retrieval     │
│   (Çok Dilli Eşleme)    │                     │ (ChromaDB - Cosine) │
└────────────┬────────────┘                     └──────────┬──────────┘
             ▼                                             ▼
┌─────────────────────────┐                     ┌─────────────────────┐
│ İlişkisel Sorgu (SQLite)│                     │ Prosedür Parçaları  │
│  (Stok, Fiyat, Rota)    │                     │  (İade & Teslimat)  │
└────────────┬────────────┘                     └──────────┬──────────┘
             └────────────────────┬────────────────────────┘
                                  ▼
                     ┌─────────────────────────┐
                     │  Dinamik Prompt Motoru  │
                     └────────────┬────────────┘
                                  ▼
                     ┌─────────────────────────┐
                     │ Google Gemini API (LLM) │
                     └────────────┬────────────┘
                                  ▼
                     ┌─────────────────────────┐
                     │   Gradio Chat UI (Web)  │
                     └─────────────────────────┘
⚡ Temel Mühendislik Yetkinlikleri
🔄 Hibrit Bilgi Getirme (Hybrid Retrieval): products.db üzerindeki ilişkisel filtrelemeler ile chroma_db üzerindeki anlamsal yoğun vektör araması tek bir yanıtta senkronize edilir.
📑 RAG Bilgi Tabanı: Resmi şirket dokümanları RecursiveCharacterTextSplitter ile 74 semantik parçaya bölünmüş, distiluse-base-multilingual-cased-v1 embedding modeli ile çok boyutlu uzayda indekslenmiştir.
🛠️ ETL Veri Hattı: 20.000 satırlık ham pazar yeri verisi (flipkart_com-ecommerce_sample.csv) filtrelenerek 1.848 adet gerçek teknoloji ürünü ayıklanmış, veri tipleri dönüştürülmüş ve SQLite şemasına yazılmıştır.
🌐 Çok Dilli Eşleme Köprüsü: Kullanıcının Türkçe sorguları (kulaklık, telefon, şarj) veri tabanındaki global terimlerle (headphone, smartphone, charger) otomatik olarak eşleştirilir.
🛡️ Sıfır Halüsinasyon Prensibi: Modele verilen sistem direktifleriyle, veri tabanında bulunmayan stok veya dokümanda yer almayan kurallar hakkında uydurma yanıt vermesi engellenmiştir.
💻 Teknoloji Yığını
Katman	Teknoloji / Model	Açıklama
Dil	Python 3.10+	Ana geliştirme ortamı
Büyük Dil Modeli (LLM)	Google Gemini API	Yanıt üretimi ve orkestrasyon
Vektör Veritabanı	ChromaDB	Doküman vektörlerinin saklanması ve benzerlik araması
Embedding Modeli	Hugging Face Multilingual	distiluse-base-multilingual-cased-v1
İlişkisel Veritabanı	SQLite3	Ürün kataloğu, fiyat, stok ve lojistik rotaları
Veri İşleme (ETL)	Pandas, PyPDF, LangChain	CSV ve PDF veri temizleme/bölme
Arayüz (UI)	Gradio	Gerçek zamanlı interaktif sohbet arayüzü
📂 Proje Ağacı
Bash
livecatalog-rag/
├── chroma_db/            # Vektörleştirilmiş politika dokümanları (ChromaDB)
├── data/
│   ├── documents/        # Ham kargo ve iade PDF dokümanları
│   └── products.db       # 1.800+ teknoloji ürününü içeren SQLite veritabanı
├── src/
│   ├── __init__.py
│   ├── generator.py      # Prompt mühendisliği ve Gemini LLM entegrasyonu
│   ├── ingest_docs.py    # PDF chunking ve vektör tabanına aktarım hattı
│   ├── process_catalog.py# Ham CSV verisini temizleyen ETL pipeline'ı
│   └── retriever.py      # SQL sorgulama ve vektör benzerlik arama motoru
├── .gitignore
├── app.py                # Gradio arayüzü ve uygulama ana giriş noktası
├── requirements.txt      # Bağımlılık listesi
└── README.md             # Proje dokümantasyonu
🚀 Kurulum ve Çalıştırma
1. Depoyu Klonlayın
Bash
git clone https://github.com/AfraORDULU/livecatalog-rag.git
cd livecatalog-rag
2. Sanal Ortamı Hazırlayın ve Bağımlılıkları Yükleyin
Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
3. Ortam Değişkenini Ekleyin
Ana dizinde bir .env dosyası oluşturup API anahtarınızı tanımlayın:
Kod snippet'i
GEMINI_API_KEY=your_gemini_api_key_here
4. Veri Tabanlarını Sıfırdan Üretin (Opsiyonel)
Bash
# PDF dokümanlarını vektörleştirir
python3 src/ingest_docs.py

# Ürün kataloğunu filtreleyip SQLite'a aktarır
python3 src/process_catalog.py
5. Uygulamayı Başlatın
Bash
python3 app.py
Uygulama başladığında tarayıcınızdan [http://127.0.0.1:7860](http://127.0.0.1:7860) adresine giderek asistanı test edebilirsiniz.
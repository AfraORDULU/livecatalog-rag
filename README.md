# 🛒 Teknosa AI Destek Asistanı (LiveCatalog-RAG)

Bu proje; e-ticaret sitelerindeki müşteri sorularını yanıtlamak için **şirket kurallarını (PDF)** ve **canlı ürün kataloğunu (SQL)** aynı anda tarayan akıllı bir destek asistanıdır.

---

## 🎯 Projenin Amacı ve Çözdüğü Sorun

Klasik yapay zekâ sohbet botları ürün stoklarını veya fiyatları bilemez, çoğunlukla yanlış bilgi (halüsinasyon) uydurur. 

Bu asistan ise soruyu iki farklı kaynaktan doğrular:
1. **Şirket Kuralları (RAG):** Teknosa'nın resmi iade şartları, garanti ve teslimat kuralları (PDF dokümanları).
2. **Canlı Ürün Kataloğu (SQL):** 1.800+ gerçek tüketici elektroniği ürününün anlık stok, fiyat ve hızlı teslimat yapılan şehir bilgileri.

---

## ⚙️ Nasıl Çalışıyor?

1. **Kullanıcı Soru Sorar:** *"İstanbul'dayım, kulaklık alırsam aynı gün gelir mi, iadesi nasıl olur?"*
2. **Katalog Taranır (SQLite):** Sistem veritabanına bakıp stoktaki kulaklıkları, fiyatlarını ve İstanbul'a hızlı teslimat olup olmadığını bulur.
3. **Kurallar Taranır (ChromaDB):** Teknosa iade/kargo PDF'lerinden kulaklık hijyen kuralları ve aynı gün teslimat şartları çekilir.
4. **Yanıt Üretilir (Gemini API):** Yapay zekâ iki bilgiyi birleştirip kullanıcıya tek, net ve doğru bir cevap sunar.

---

## 🛠️ Kullanılan Teknolojiler

- **Python:** Temel programlama dili
- **LangChain & ChromaDB:** PDF dokümanlarını hafızaya alıp benzerlik araması yapmak için
- **SQLite:** 1.800+ teknoloji ürününü saklamak ve filtrelemek için
- **Google Gemini API:** Bilgileri birleştirip mantıklı yanıt üreten yapay zekâ modeli
- **Pandas:** Ham pazar yeri verisinden teknoloji ürünlerini ayıklamak için (ETL)
- **Gradio:** Sohbet ekranı (web arayüzü)

---

## 📁 Dosya Yapısı

```text
livecatalog-rag/
├── data/
│   ├── documents/         # Teknosa kargo ve iade PDF'leri
│   └── products.db        # 1.800+ filtrelenmiş teknoloji ürünü (SQLite)
├── src/
│   ├── generator.py       # Bilgileri toplayıp Gemini'ye ileten kod
│   ├── ingest_docs.py     # PDF'leri okuyup vektör tabanına (ChromaDB) aktaran kod
│   ├── process_catalog.py # Ham CSV'den teknoloji ürünlerini süzen kod
│   └── retriever.py       # SQL ve PDF aramasını yapan modül
├── app.py                 # Gradio sohbet arayüzü
├── requirements.txt       # Gerekli Python kütüphaneleri
└── README.md


🚀 Nasıl Çalıştırılır?
Gereksinimleri yükleyin:
pip install -r requirements.txt

.env dosyasına API anahtarınızı ekleyin:
GEMINI_API_KEY=api_anahtariniz

Uygulamayı başlatın:
python3 app.py

🙌🏻 Tarayıcınızda açılan yerel adresten (http://127.0.0.1:7860) asistanla sohbet edebilirsiniz.
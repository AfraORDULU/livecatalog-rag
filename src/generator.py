import os
from dotenv import load_dotenv
from google import genai

# arama fonksiyonunu çağırıyoruz
from retriever import search_policy_documents, search_products_db


# ORTAM DEĞİŞKENLERİ VE GEMINI İSTEMCİSİ

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY ortam değişkeni bulunamadı! .env dosyasını kontrol edin.")

client = genai.Client(api_key=api_key)
# Senin de test edip doğruladığın çalışan model adı:
MODEL_NAME = "gemini-flash-latest"


# SİSTEM YÖNLENDİRMESİ (SYSTEM PROMPT)

# Notlarındaki 114. sayfada yer alan halüsinasyonu engelleyen kurallar:
SYSTEM_INSTRUCTION = """
Sen LiveCatalog platformunun profesyonel, kibar ve yardımsever E-Ticaret Destek Asistanısın.

GÖREVİN VE KURALLARIN:
1. Yalnızca sana sağlanan 'POLİTİKA METİNLERİ (RAG)' ve 'ÜRÜN BİLGİLERİ (SQL)' bağlamını kullanarak yanıt ver.
2. Bağlamda yer almayan kuralları, ürün özelliklerini veya stok durumlarını ASLA kafandan uydurma (halüsinasyon görme).
3. Stok adedi 0 olan bir ürün sorulursa, ürünün tükendiğini açıkça belirt.
4. Kargo veya iade kurallarına değindiğinde, bilginin hangi dokümandan geldiğini parantez içinde belirt (Örn: [Kaynak: iade_politikasi.md]).
5. Eğer kullanıcının sorusu sağlanan bağlamla yanıtlanamıyorsa, dürüstçe 'Şirket politikalarımız veya ürün kataloğumuz kapsamında bu bilgiye ulaşamadım' de.
6. Yanıtların Türkçe, açık, profesyonel ve müşteri odaklı olsun.
"""


def generate_response(user_query: str, product_keyword: str = "") -> str:
    """
    Kullanıcı sorusunu alır:
    1. ChromaDB'den ilgili politika metinlerini çeker (RAG).
    2. İlgili ürün kelimesi varsa SQLite'tan ürün bilgilerini çeker (SQL).
    3. Hepsini tek bir bağlamda birleştirip Gemini'ye sorar.
    """
    
    # --- A) RAG Politika Metinlerini Çekme ---
    policy_docs = search_policy_documents(user_query, n_results=2)
    context_policy = ""
    for idx, doc in enumerate(policy_docs, start=1):
        context_policy += f"\n[Doküman {idx} - Kaynak: {doc['source']}]\n{doc['content']}\n"
    
    # --- B) SQL Ürün Bilgilerini Çekme ---
    context_products = ""
    if product_keyword:
        matched_products = search_products_db(product_keyword)
        if matched_products:
            for prod in matched_products:
                context_products += (
                    f"\n- Ürün: {prod['name']}\n"
                    f"  Marka/Kategori: {prod['brand']} / {prod['category']}\n"
                    f"  Fiyat: {prod['price']} TL | Stok: {prod['stock']} adet\n"
                    f"  Hızlı Teslimat Şehirleri: {prod['fast_delivery_cities']}\n"
                    f"  Teknik Özellikler: {prod['specs']}\n"
                )
        else:
            context_products = "\nAranan kriterde veritabanında ürün bulunamadı.\n"
    else:
        context_products = "\nHerhangi bir spesifik ürün sorgulanmadı.\n"

    # --- C) LLM için Birleştirilmiş Kullanıcı Prompt'u ---
    prompt = f"""
KULLANICI SORUSU:
{user_query}

---
GÜNCEL ÜRÜN VERİTABANI BİLGİLERİ (SQL):
{context_products}

---
ŞİRKET POLİTİKA METİNLERİ (RAG):
{context_policy}

Lütfen yukarıdaki kurallara ve ürün durumuna sadık kalarak kullanıcıya kapsamlı bir yanıt hazırla.
"""

    # --- D) Gemini API Çağrısı ---
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.2  # Halüsinasyonu en aza indirmek için düşük yaratıcılık/yüksek gerçekçilik
        }
    )

    return response.text



# YEREL TEST BLOĞU

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 HİBRİT RAG + SQL CEVAP ÜRETİCİ TESTİ")
    print("="*60)
    
    test_question = "İzmir'de oturuyorum. Gürültü engelleyici bir kulaklık almak istiyorum, hızlı teslimatla yarın gelir mi? Bir de kutusunu açarsam iade edebilir miyim?"
    print(f"Kullanıcı Sorusu: {test_question}\n")
    print("⏳ Cevap üretiliyor...")
    
    cevap = generate_response(user_query=test_question, product_keyword="kulaklık")
    print("\n" + "-"*40 + " MODELİN YANITI " + "-"*40)
    print(cevap)
    print("-"*(80 + len(" MODELİN YANITI ")))
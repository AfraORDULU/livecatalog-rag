import os
import sqlite3
from typing import List, Dict, Any

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ---------------------------------------------------------
# 1. DOSYA YOLLARI
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "products.db")
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v1"

# ---------------------------------------------------------
# 2. VEKTÖR TABANI (CHROMA) - PDF ARAMA FONKSİYONU
# ---------------------------------------------------------
_embeddings = None
_vector_store = None


def get_vector_store():
    global _embeddings, _vector_store
    if _vector_store is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"}
        )
        _vector_store = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=_embeddings
        )
    return _vector_store


def search_policy_documents(query: str, n_results: int = 3, **kwargs) -> List[Dict[str, Any]]:
    """
    Kullanıcı sorusuyla anlamsal olarak en yakın Teknosa politika metinlerini getirir.
    """
    try:
        store = get_vector_store()
        results = store.similarity_search(query, k=n_results)
        
        extracted_docs = []
        for doc in results:
            extracted_docs.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "teknosa_belgesi.pdf")
            })
        return extracted_docs
    except Exception as e:
        print(f"⚠️ ChromaDB sorgulama hatası: {e}")
        return []


# ---------------------------------------------------------
# 3. İLİŞKİSEL VERİTABANI (SQLITE) - ÜRÜN ARAMA FONKSİYONU
# ---------------------------------------------------------
def search_products_db(keyword: str) -> List[Dict[str, Any]]:
    """
    SQL Arama Fonksiyonu:
    Türkçe ve İngilizce eşleşmeleri hesaba katarak katalogda arama yapar.
    """
    if not keyword or not keyword.strip():
        return []

    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    term_map = {
        "kulaklık": ["headphone", "earphone", "headset", "audio", "kulaklık"],
        "telefon": ["phone", "mobile", "smartphone", "telefon"],
        "bilgisayar": ["laptop", "computer", "notebook", "pc", "bilgisayar"],
        "saat": ["watch", "smartwatch", "saat"],
        "hoparlör": ["speaker", "soundbar", "hoparlör"],
        "kablo": ["cable", "usb", "kablo"],
        "şarj": ["charger", "adapter", "şarj"],
        "apple": ["apple", "iphone", "ipad", "macbook"],
        "samsung": ["samsung", "galaxy"],
        "sony": ["sony"]
    }

    cleaned_kw = keyword.lower().strip()
    search_terms = term_map.get(cleaned_kw, [cleaned_kw])

    conditions = []
    params = []
    for term in search_terms:
        like_pattern = f"%{term}%"
        conditions.append("(name LIKE ? OR category LIKE ? OR brand LIKE ? OR specs LIKE ?)")
        params.extend([like_pattern, like_pattern, like_pattern, like_pattern])

    where_clause = " OR ".join(conditions)
    query = f"""
    SELECT name, category, brand, price, stock, fast_delivery_cities, specs
    FROM products
    WHERE {where_clause}
    LIMIT 6
    """

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        products.append({
            "name": row[0],
            "category": row[1],
            "brand": row[2],
            "price": row[3],
            "stock": row[4],
            "fast_delivery_cities": row[5],
            "specs": row[6]
        })
    return products
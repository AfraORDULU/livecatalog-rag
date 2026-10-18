import os
import glob

# LangChain PDF yükleyicisi
from langchain_community.document_loaders import PyPDFLoader

# Metin parçalama (Chunking)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embedding ve ChromaDB vektör tabanı
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


# AYARLAR VE DİZİNLER

DOCUMENTS_DIR = os.path.join("data", "documents")
CHROMA_PERSIST_DIR = "chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v1"


def load_pdf_documents(folder_path):
    """
    data/documents klasöründeki tüm PDF'leri tarar,
    PyPDFLoader ile sayfa sayfa okur.
    """
    all_docs = []
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

    if not pdf_files:
        print("⚠️ data/documents klasöründe hiç .pdf dosyası bulunamadı!")
        return []

    for pdf_path in pdf_files:
        file_name = os.path.basename(pdf_path)
        print(f"📖 PDF taranıyor: {file_name}...")
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            for page in pages:
                page.metadata["source"] = file_name
                all_docs.append(page)
        except Exception as e:
            print(f"❌ {file_name} okunurken hata: {e}")

    print(f"📄 Toplam {len(all_docs)} sayfa PDF içeriği başarıyla hafızaya alındı.")
    return all_docs


def build_vector_store():
    """
    PDF sayfalarını mantıksal parçalara ayırır, vektörleştirir ve ChromaDB'ye kaydeder.
    """
    documents = load_pdf_documents(DOCUMENTS_DIR)
    if not documents:
        return

    # Chunking stratejisi
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=450,
        chunk_overlap=60,
        separators=["\n\n", "\n", "?", ".", " "]
    )
    
    chunked_docs = text_splitter.split_documents(documents)
    print(f"✂️ Dokümanlar toplam {len(chunked_docs)} adet anlamsal parçaya (chunk) bölündü.")

    # Embedding modeli
    print(f"🧠 Embedding modeli yükleniyor: {EMBEDDING_MODEL_NAME}...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"}
    )

    # ChromaDB'ye yazma
    print("💾 Vektörler ChromaDB'ye kaydediliyor...")
    vector_store = Chroma.from_documents(
        documents=chunked_docs,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )

    print(f"✅ Vektör veritabanı resmi Teknosa dokümanlarıyla mühürlendi! ('{CHROMA_PERSIST_DIR}')")


if __name__ == "__main__":
    build_vector_store()
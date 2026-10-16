import os       # İşletim sistemi dosya ve klasör yollarını (path) yönetmek için
import glob     # Klasör içindeki belirli uzantıya sahip dosyaları (örn. *.md) topluca bulmak için

# LangChain kütüphanesinden metin bölücü:
# RecursiveCharacterTextSplitter: Metni rastgele bir yerden kesmek yerine
# sırasıyla paragraflar, yeni satırlar ve boşluklardan bölerek anlam bütünlüğünü korur.
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Hugging Face üzerindeki açık kaynaklı embedding modellerini yerel bilgisayarda çalıştırmak için
from langchain_community.embeddings import HuggingFaceEmbeddings

# Metin parçalarını ve sayısal vektörleri (embedding) diske kaydedip semantik arama yapacağımız vektör tabanı
from langchain_community.vectorstores import Chroma


# TEMEL DİZİN VE MODEL AYARLARI

# Şirket politika dokümanlarının (iade, teslimat vb.) bulunduğu klasör yolu ("data/documents")
DOCUMENTS_DIR = os.path.join("data", "documents")

# Vektör tabanının dosyalarının diske kalıcı olarak kaydedileceği klasör adı
# (.gitignore içine yazdığımız için bu klasör GitHub'a yüklenmez, yerelde kalır)
CHROMA_PERSIST_DIR = "chroma_db"

# Kullanacağımız embedding modeli:
# Çok dilli (Multilingual), özellikle Türkçe semantik benzerlikte çok başarılı ve hafiftir.
# Bilgisayarın CPU'sunda harici bir API anahtarına veya ücrete ihtiyaç duymadan yerel çalışır.
EMBEDDING_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v1"


def load_documents_from_folder(folder_path):
    """
    Belirtilen klasördeki tüm .md (Markdown) dosyalarını tek tek okur.
    Her belgenin ham metnini ve hangi dosyadan geldiğini belirten 'metadata' bilgisini toplar.
    """
    documents = []
    
    # "data/documents/*.md" kalıbına uyan tüm dosya yollarını bir liste olarak alır
    file_paths = glob.glob(os.path.join(folder_path, "*.md"))

    for file_path in file_paths:
        # Dosyayı Türkçe karakter problemi yaşamamak için utf-8 formatında açıp okuyoruz
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
            # os.path.basename: "/Users/.../data/documents/iade_politikasi.md" yolundan
            # sadece dosyanın adı olan "iade_politikasi.md" kısmını ayıklar.
            file_name = os.path.basename(file_path)
            
            # Belgeyi içerik ve kaynak bilgisi (metadata) ile birlikte listemize ekliyoruz
            documents.append({
                "page_content": text,
                "metadata": {"source": file_name}  # Modelin cevabı hangi dosyadan aldığını bilmesi için kritik
            })
    
    print(f"📄 Toplam {len(documents)} adet doküman klasörden başarıyla okundu.")
    return documents


def build_vector_store():
    """
    RAG akışının ana boru hattı (Pipeline):
    1. Ham metinleri yükler.
    2. Metinleri mantıksal küçük parçalara (chunk) böler.
    3. Parçaları embedding modelinden geçirerek vektörlere dönüştürür.
    4. Vektörleri ChromaDB'ye yazar.
    """
    
  
    # DOKÜMANLARI KLASÖRDEN OKUMA
    
    raw_docs = load_documents_from_folder(DOCUMENTS_DIR)
    
    # Eğer klasör boşsa veya dosya bulunamazsa programın çökmemesi için kontrol
    if not raw_docs:
        print("⚠️ Doküman klasöründe okunacak dosya bulunamadı! İşlem durduruldu.")
        return

   
    # METİN PARÇALAMA (CHUNKING) STRATEJİSİ
    
    # Neden bölüyoruz? 
    # LLM'ler ve embedding modelleri kısıtlı bağlam penceresine (token limit) sahiptir.
    # Ayrıca tüm dokümanı tek parça verirsek model tam aranan cümleyi bulmakta zorlanır.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,         # Her metin parçasının azami karakter uzunluğu (~70-90 kelime)
        chunk_overlap=60,       # İki parça arasında ortak kalacak karakter payı. 
                                # Bir cümlenin tam ortadan kesilip anlamının kaybolmasını önler.
        separators=["\n## ", "\n\n", "\n", " ", ""] # Bölme önceliği: Önce Markdown başlıkları, 
                                                    # sonra paragraflar, en son kelimeler.
    )

    texts = []       # Ayrıştırılan metin parçaları
    metadatas = []   # Her bir parçanın hangi dosyaya ait olduğu bilgisi

    for doc in raw_docs:
        # Ham metni tanımladığımız kurallara göre parçalara ayırıyoruz
        chunks = text_splitter.split_text(doc["page_content"])
        
        for chunk in chunks:
            texts.append(chunk)
            metadatas.append(doc["metadata"])

    print(f"✂️ Dokümanlar toplam {len(texts)} adet anlamlı parçaya (chunk) bölündü.")

   
    # EMBEDDING MODELİNİ ÇALIŞTIRMA
    
    # Metinleri çok boyutlu uzayda anlamsal birer sayı vektörüne (örn. 512 boyutlu vektör) çeviren yapay zeka modeli
    print(f"🧠 Embedding modeli yükleniyor: {EMBEDDING_MODEL_NAME}...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"}  # Modeli Mac'in işlemcisi (CPU) üzerinde çalıştırıyoruz
    )

   
    # CHROMADB'YE VEKTÖRLERİ YAZMA VE İNDEKSLENME
    
    # from_texts fonksiyonu arka planda iki işi aynı anda yapar:
    # 1. texts listesindeki her bir parçayı alır ve embeddings modeline gönderip vektörünü çıkarır.
    # 2. Üretilen vektörleri, orijinal metinleri ve metadataları 'chroma_db' dizinine kaydeder.
    print("💾 Metin parçaları embedding vektörlerine dönüştürülüyor ve ChromaDB'ye kaydediliyor...")
    
    vector_store = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=CHROMA_PERSIST_DIR  # Diskte kalıcı olacağı hedef klasör
    )

    print(f"✅ Vektör veritabanı başarıyla oluşturuldu ve '{CHROMA_PERSIST_DIR}' dizinine mühürlendi!")


# Bu dosya terminalden doğrudan çağrıldığında çalışacak başlangıç noktası:
if __name__ == "__main__":
    build_vector_store()
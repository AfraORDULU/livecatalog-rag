import os
from dotenv import load_dotenv
from google import genai

# .env dosyasındaki değişkenleri sisteme yükler
load_dotenv()

# Ortam değişkeninden anahtarı okuyoruz
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ HATA: GEMINI_API_KEY bulunamadı! .env dosyasını kontrol et.")
else:
    print("🔑 API Anahtarı başarıyla algılandı.")
    # Gemini istemcisini başlatıyoruz
    client = genai.Client(api_key=api_key)
    
    # Test çağrısı yapıyoruz
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="Merhaba, bana tek bir cümleyle kendini tanıt."
    )
    
    print("\n🤖 Gemini Yanıtı:")
    print(response.text)
    print("\n✅ Gemini API bağlantısı sorunsuz çalışıyor!")
import os
import sys

# src klasöründeki modülleri içeri alabilmek için dizin ekliyoruz
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import gradio as gr
from generator import generate_response


# SOHBET VE SORGULAMA MANTIĞI

def chat_with_assistant(message: str, history):
    """
    Kullanıcı mesajındaki teknoloji anahtar kelimelerini yakalar;
    Teknosa PDF dokümanları (ChromaDB) ve SQLite ürün kataloğunu
    hibrit olarak harmanlayarak yanıt üretir.
    """
    if not message.strip():
        return "Lütfen Teknosa ürünleri veya sipariş/teslimat süreçleri hakkında bir soru girin."

    message_lower = message.lower()
    
    # Veritabanında eşleşebilecek popüler teknoloji terimleri
    keywords_to_check = [
        "kulaklık", "headphone", "earphone", "sony", "apple", "samsung", 
        "telefon", "mobile", "phone", "laptop", "bilgisayar", "computer", 
        "kablo", "cable", "şarj", "charger", "kamera", "camera", "hoparlör", "speaker"
    ]
    
    detected_keyword = ""
    for kw in keywords_to_check:
        if kw in message_lower:
            detected_keyword = kw
            break

    try:
        # Hibrit motoru çalıştırıyoruz
        response_text = generate_response(user_query=message, product_keyword=detected_keyword)
        return response_text
    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"



# GRADIO KULLANICI ARAYÜZÜ (UI)

demo = gr.ChatInterface(
    fn=chat_with_assistant,
    title="🛒 Teknosa AI Destek Asistanı",
    description="Resmi Teknosa kargo/iade prosedürleri (RAG) ve 150+ gerçek teknoloji ürün kataloğunu (SQL) birlikte sorgulayan akıllı destek motoru.",
    examples=[
        "İstanbul'dayım, bugün sipariş verirsem aynı gün teslimat şartları nelerdir?",
        "Mağazanızda kulaklık var mı? Kutusunu açarsam iade edebilir miyim?",
        "Standart kargoda ücretsiz teslimat için alt sepet limiti nedir?",
        "Sipariş ettiğim ürün kargoda hasarlı çıkarsa ne yapmalıyım?"
    ]
)

if __name__ == "__main__":
    demo.launch()
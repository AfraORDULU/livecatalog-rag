import os
import sys

# src klasöründeki modüllerin rahatça import edilebilmesi için yolu ekliyoruz
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import gradio as gr
from generator import generate_response


# SOHBET VE SORGULAMA MANTIĞI

def chat_with_assistant(message: str, history):
    """
    Gradio arayüzünden gelen kullanıcı mesajını alır,
    basit anahtar kelime tespitiyle ürün kataloğunu ve
    ChromaDB politika dokümanlarını tarayarak yanıt üretir.
    """
    if not message.strip():
        return "Lütfen bir soru veya ürün talebi girin."

    message_lower = message.lower()
    
    # Kullanıcı mesajında geçen olası ürün anahtar kelimelerini yakalıyoruz
    product_keywords = ["kulaklık", "airpods", "sony", "laptop", "bilgisayar", "dell", "monitör", "samsung", "kahve", "philips", "iphone", "telefon"]
    
    detected_keyword = ""
    for kw in product_keywords:
        if kw in message_lower:
            detected_keyword = kw
            break

    # Hibrit RAG + SQL motorunu çalıştırıyoruz
    try:
        response_text = generate_response(user_query=message, product_keyword=detected_keyword)
        return response_text
    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"



# GRADIO KULLANICI ARAYÜZÜ (UI)

#tema:
demo = gr.ChatInterface(
    fn=chat_with_assistant,
    title="🛒 LiveCatalog RAG: Akıllı E-Ticaret Destek Asistanı",
    description="Statik şirket politikaları (ChromaDB) ve dinamik stok/fiyat veritabanını (SQLite) hibrit olarak sorgulayan akıllı müşteri destek asistanı.",
    examples=[
        "İzmir'de yaşıyorum, ANC özellikli bir kulaklık yarın teslim edilir mi? Kutusunu açarsam iade edebilir miyim?",
        "AirPods Pro almak istiyorum, güncel stok ve fiyat durumu nedir?",
        "iPhone 18 Pro Max için kargo teslimat süresi ve koşulları nelerdir?",
        "500 TL altındaki siparişlerde kargo ücreti öder miyim?"
    ]
)

if __name__ == "__main__":
    # Tarayıcıda yerel bir sunucu başlatır (http://127.0.0.1:7860)
    demo.launch()
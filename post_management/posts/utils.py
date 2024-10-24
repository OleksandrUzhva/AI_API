import google.generativeai as genai
import os

# Настройка модели генеративного AI
genai.configure(api_key=os.getenv("AI_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def to_markdown(text):
     return text.replace('•', '  *')

def check_toxicity(text):
    try:
        # Генерация ответа для проверки цензурности
        response = model.generate_content([f"Этот текст содержит нецензурную лексику? '{text}'"])
        
        # Проверка ответа от AI (он отвечает "Да" или "Нет")
        toxicity_check = response.candidates[0].content.parts[0].text.strip().lower()
        is_blocked = 'да' in toxicity_check  # Если AI ответил "Да", значит, что пост содержит нецензурную лексику
        
        return is_blocked
    except Exception as e:
        raise Exception(f"Ошибка при проверке текста: {e}")

def generate_auto_reply(post_content, comment_content):
    # Вызов AI для генерации релевантного ответа
    response = model.generate_content([
        f"Ответь на этот комментарий: '{comment_content}' с учетом содержания поста: '{post_content}'"
    ])
    
    # Получаем ответ от AI
    reply = response.candidates[0].content.parts[0].text.strip()
    return reply
 
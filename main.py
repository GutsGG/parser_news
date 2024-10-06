import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler
import logging

# Настройки бота
TOKEN = '5145453997:AAGwBbU7eM6STVpGspvzTu5zH8kyDOE13zk'
bot = Bot(token=TOKEN)

# Ключевые слова для фильтрации новостей
KEYWORDS = ["Энергетики", "свет", "электричество", "Липецкэнерго", "Тело", "мужчина", "дожди", "Труп"]

# URL сайта для парсинга
GOROD_URL = 'https://gorod48.ru/news/'
VESTI_URL = 'https://vesti-lipetsk.ru/novosti/'

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция парсинга новостей с сайта gorod48.ru
def parse_news():
    response = requests.get(GOROD_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Находим все блоки новостей
    articles = soup.find_all('div', class_='main-card')
    news_links = []

    for article in articles:
        title_tag = article.find('div', class_='main-card-title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            link_tag = article.find('a', class_='main-card--content')
            if link_tag and link_tag.get('href'):
                link = link_tag['href']

                if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                    full_link = "https://gorod48.ru" + link
                    if full_link not in news_links:
                        news_links.append(full_link)

    return news_links

# Функция парсинга новостей с сайта vesti-lipetsk.ru
def parse_vesti_news():
    response = requests.get(VESTI_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    articles = soup.find_all('div', class_='news-item__inner')
    news_links = []

    for article in articles:
        title_tag = article.find('div', class_='news-item__title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            link_tag = title_tag.find('a')
            if link_tag and link_tag.get('href'):
                link = link_tag['href']

                if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                    full_link = "https://vesti-lipetsk.ru" + link
                    if full_link not in news_links:
                        news_links.append(full_link)

    return news_links

# Функция обработки команды /update для получения новых новостей
async def update_news(update: Update, context):
    chat_id = update.message.chat_id
    
    gorod_news = parse_news()
    vesti_news = parse_vesti_news()
    
    all_news = gorod_news + vesti_news

    if all_news:
        for link in all_news:
            await context.bot.send_message(chat_id=chat_id, text=link)
    else:
        await context.bot.send_message(chat_id=chat_id, text="Новостей с заданными ключевыми словами не найдено.")

# Основная функция для запуска бота
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("update", update_news))
    application.run_polling()

# Запускаем бота
if __name__ == '__main__':
    main()

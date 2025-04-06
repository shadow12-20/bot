import requests
from bs4 import BeautifulSoup
import re
import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ✅ NAME MAPPING
name_mappings = {
    "Connor McDonald": "Aditya Verma",
    "New York": "Mumbai",
}

# ✅ Chinese Name Conversion
chinese_to_indian = {
    "Li Wei": ("Wei", "Li"),
    "Zhao Yun": ("Yun", "Zhao")
}
indian_name_map = {
    "Wei Li": "Vikram Mehra",
    "Yun Zhao": "Arjun Sinha"
}

def replace_names(text, mappings):
    for original, indian in mappings.items():
        text = re.sub(r'\b' + re.escape(original) + r'\b', indian, text)
    return text

def convert_chinese_name(text):
    for chinese, (given, surname) in chinese_to_indian.items():
        indian_format = f"{given} {surname}"
        indian_name = indian_name_map.get(indian_format, indian_format)
        text = re.sub(r'\b' + re.escape(chinese) + r'\b', indian_name, text)
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("नमस्ते! 📚 मैं पहले 20 चैप्टर डाउनलोड कर रहा हूँ...")

    base_url = "https://novelbin.me/novel-book/getting-10-trillion-out-of-nowhere"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    chapter_links = []
    for a_tag in soup.find_all('a', href=True):
        if '/chapter/' in a_tag['href'] and a_tag['href'] not in chapter_links:
            chapter_links.append(a_tag['href'])
        if len(chapter_links) == 20:
            break

    all_chapters = []
    for link in chapter_links:
        chapter_url = f"https://novelbin.me{link}"
        chapter_response = requests.get(chapter_url, headers=headers)
        chapter_soup = BeautifulSoup(chapter_response.content, 'html.parser')
        title_tag = chapter_soup.find('h1')
        content_tag = chapter_soup.find('div', class_='chapter-content')
        if not title_tag or not content_tag:
            continue
        chapter_title = title_tag.text.strip()
        chapter_content = content_tag.text.strip()
        chapter_content = convert_chinese_name(chapter_content)
        chapter_content = replace_names(chapter_content, name_mappings)
        all_chapters.append(f"{chapter_title}\n\n{chapter_content}")

    file_path = "first_20_chapters_indian_version.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("\n\n".join(all_chapters))

    await update.message.reply_document(document=open(file_path, "rb"))
    os.remove(file_path)

# 🟩 START BOT
def main():
    application = ApplicationBuilder().token("BOT_TOKEN_HERE").build()
    application.add_handler(CommandHandler("start", start))
    print("✅ Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()

# 🏗️ Telegram Architect Bot (MVP)

> Modular Telegram bot for converting user architectural requirements into validated JSON, generating DXF plans, and PNG previews.

---

## Features
- **/start** va matnli so‘rovlar uchun Telegram bot (aiogram)
- AI yordamida (Groq yoki boshqa LLM) foydalanuvchi so‘rovini qat’iy JSON sxemaga aylantirish
- JSON sxemani tekshirish va default qiymatlarni to‘ldirish
- 2D arxitektura chizmasini DXF formatida generatsiya qilish (ezdxf)
- PNG preview (matplotlib)
- DXF va PNG fayllarni avtomatik foydalanuvchiga yuborish
- Kengaytiriladigan va modulli arxitektura

## Loyihaning tuzilishi

```
telegram_architect_bot/
├── ai/           # AI integratsiyasi va promptlar
├── bot/          # Telegram bot logikasi
├── config/       # Sozlamalar va konstantalar
├── dxf_gen/      # DXF generatsiya modullari
├── preview/      # PNG preview generatsiyasi
├── schema/       # JSON sxema va validator
├── utils/        # Foydali yordamchi funksiyalar
├── requirements.txt
├── .env.example
└── README.md
```

## O‘rnatish
1. Python 3.11 o‘rnating
2. Virtual muhit yarating va faollashtiring:
	```sh
	python -m venv venv
	venv\Scripts\activate  # Windows
	# yoki
	source venv/bin/activate  # Linux/Mac
	```
3. Kerakli kutubxonalarni o‘rnating:
	```sh
	pip install --upgrade pip
	pip install -r requirements.txt
	```
4. `.env` faylini to‘ldiring (`.env.example` asosida):
	```env
	TELEGRAM_BOT_TOKEN=your_token_here
	AI_PROVIDER=mock
	AI_API_KEY=
	OUTPUT_DIR=output
	```

## Ishga tushirish
```sh
python -m bot.main
```

## Foydalanish
1. Botga /start yuboring
2. Arxitektura talablaringizni matn ko‘rinishida yuboring
3. Bot sizga DXF va PNG preview fayllarni qaytaradi

## Texnologiyalar
- Python 3.11
- aiogram
- ezdxf
- matplotlib
- Pillow
- jsonschema
- Groq yoki boshqa LLM (mock default)

## Litsenziya
MIT

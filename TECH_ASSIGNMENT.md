# Texnik Topshiriq: Build-CAD ArchDesign Bot

Ushbu hujjat loyihaning yakuniy talablarini va amalga oshirilgan professional standartlarni o'z ichiga oladi.

## 1. Loyihaning Maqsadi

Foydalanuvchi tomonidan berilgan oddiy matnli so'rovlar asosida (masalan: "10x15m yer, 3 xonali uy") professional me'moriy chizmalarni (DXF formatida) avtomatik ravishda tayyorlaydigan Telegram bot yaratish.

## 2. Funksional Talablar

### 2.1. AI Integratsiyasi (Mantiqiy Qism)

* **Matnni tahlil qilish**: Foydalanuvchi so'rovidan yer o'lchami, xonalar soni va umumiy talablarni ajratib olish.
* **Spatial Logic**: Xonalarning bir-biri bilan bog'liqligini (connectivity) va mantiqiy joylashuvini ta'minlash.
* **Arxitektura qoidalari**: Eskalator/zina, eshik va derazalarni to'g'ri joylashtirish.

### 2.2. CAD (DXF) Generatsiya Engine

* **Professional Qatlamlar (Layers)**: Har bir element o'z qatlamida (A-WALL, A-DOOR, A-DIM, va h.k.) bo'lishi.
* **GOST Standarti**: Chizma GOST 21.1101-2013 talablariga muvofiq bo'lishi:
  * **Ramka**: 20/5/5/5 mm hoshiyalar.
  * **Shtamp**: 185x55mm o'lchamdagi rasmiy "Asosiy shtamp".
  * **O'lchamlar**: Zanjir ko'rinishidagi o'lcham chiziqlari va 3mm arxitektura seriflari (ticks).
* **O'lchamlar va Masshtab**:
  * Avtomatik masshtab: 1:50 yoki 1:100.
  * Qog'oz formati: A3 yoki A4 (loyiha hajmiga qarab).

### 2.3. Vizualizatsiya va Preview

* **PNG Preview**: DXF faylidan oldin foydalanuvchiga yuqori sifatli qora-oq (professional) texnik rasm taqdim etish.
* **Matnlar tiniqligi**: Xona nomlari va o'lchamlar tagida "masking" (oq fon) bo'lishi.

## 3. Texnik Talablar

### 3.1. Texnologiyalar

* **Python 3.10+**: Asosiy dasturlash tili.
* **Aiogram 3.x**: Telegram bot interfeysi uchun.
* **ezdxf**: DXF fayllarini professional darajada generatsiya qilish uchun.
* **Matplotlib**: Preview rasmlarini tayyorlash uchun.

### 3.2. Chizma Layout (Joylashuv)

* Chizma varaqning **yuqori chap** qismida joylashishi kerak.
* O'ng/pastki qism shtamp va "Xonalar eksplikatsiyasi" uchun foydalaniladi.

## 4. UI/UX Talablar

* **Til**: O'zbek va Ingliz tillarini to'liq qo'llab-quvvatlava (Bilingual support).
* **Boshqaruv**: "/start", "/yordam" komandalari va "Bekor qilish" tugmasi.
* **Xavfsizlik**: Foydalanuvchi kirishlarini validator orqali tekshirish.

## 5. Kelgusidagi Rivojlanish

* 3D model (OBJ/IFC) generatsiya qilish.
* Binoning umumiy tannarxini (smetasini) hisoblash.
* Interyer dizayn elementlarini qo'shish.

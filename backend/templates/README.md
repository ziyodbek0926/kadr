# Hujjat shablonlari

`docx_generator.py` hozircha "Obyektivka"ni python-docx bilan dasturiy ravishda (koddan)
quradi — bu yerga tashkilotning haqiqiy rasmiy `.docx` shabloni qo'yilmagan, chunki aniq
shablon fayli taqdim etilmagan.

Ishlab chiqarishga o'tishda tavsiya etiladigan yo'l: shu papkaga tashkilotning rasmiy
"Obyektivka" shablonini (`obyektivka_template.docx`) joylashtirib, `docxtpl`
kutubxonasi orqali `{{ to_lower_case }}`-uslubidagi placeholder'lar bilan to'ldirish —
bu yondashuv shablon formatini (logotip, shtamp joylari, aniq shrift/joylashuv) aynan
saqlab qoladi va python-docx bilan qo'lda qurishdan ko'ra ancha kam kod talab qiladi.

# BayMavi Telegram İçerik Otomasyonu — Haftalık Talimatlar

Bu dosya, her Pazartesi 12:00'de çalışan otomasyon görevinin izlediği talimattır.

## Amaç
Klasördeki hazır görsellerden, kanal + rakip verisi analiziyle, gelecek haftanın deneysel içerik takvimini caption'larıyla hazırlayıp Slack'e onaya göndermek.

## Sabit bilgiler
- **İçerik klasörü:** C:\Users\Beyza Taylan\Desktop\Telegram-Otomasyon
  - `upcoming-games/<oyun>/` — yeni oyun görselleri (video öncelikli, yoksa web_banner)
  - `Game-Of-The-Week/<hafta>/` — haftanın oyunu görselleri
  - `Bonuslar/` — bonus görselleri
- **Kendi kanal (public feed):** https://t.me/s/BayMavi_Resmi2026
- **Slack onay kanalı:** #marketing-agent (C0BJ8UK5LLF)
- **Yeni oyun takvimi (Drive):** "Upcoming Games" (id 1k8TpO1jw-LJ2gcV5QVcmVLTxSTd8sizuV2TI03x5EWU) — çıkış tarihi + oyun + sağlayıcı
- **Rakip listesi (Drive):** "Competitors C6" (id 19NtrkFOfg27BnO9xH5mUin-eVXgfAy3Q7hEh3N4Nk1I) — Telegram handle'ları

## Haftalık adımlar
1. **Kendi performans analizi:** Chrome ile https://t.me/s/BayMavi_Resmi2026 feed'ini oku. Geçen haftanın postları için saat + görüntülenme + reaksiyon çıkar. Saat penceresi (sabah 09-11 / öğle 11-14 / öğleden sonra 14-17 / akşam 17-21) bazında performansı güncelle. Not: görüntülenme post yaşından ve içerik türünden etkilenir, buna göre yorumla.
2. **Rakip taraması:** Competitors C6'daki Telegram handle'larından public önizlemesi AÇIK olanları (ör. t.me/s/casibom) Chrome ile tara. Kim, ne zaman, ne paylaşıyor + etkileşim özeti çıkar. Önizlemesi kapalı olanları (Xslot, Matadorbet) atla.
3. **Yeni içerik envanteri:** Klasörde görseli HAZIR olan oyun/bonusları tespit et. Drive "Upcoming Games"ten çıkış tarihlerini eşle.
4. **Takvim üret:** Gelecek 7 günün deneysel takvimini kur.
   - Zamanlama DENEYSEL: saatleri sabit tutma; sabah/öğle/öğleden sonra/akşam pencerelerini dönüşümlü dene ve etiketle ki performans ölçülebilsin. Mevcut eğilim: öğle–öğleden sonra (11:00–16:00) güçlü.
   - Oyunları yalnızca çıkış günü değil, boşluk kaldıkça araya da yerleştir (filler).
   - Spor: takip edilen ligler (Süper Lig, Ziraat Kupası, hazırlık/milli maçlar, Premier League + büyük ligler; basketbol A Milli + NBA; voleybol milli + VNL + Avrupa Şampiyonası) için fikstürü Chrome'dan çek; her maça T-1 gün + maç günü FOMO slotu, güncel giriş linkiyle.
5. **Caption yaz:** Kanalın sesinde ve ŞU FORMATTA (boş satırlarla):

   ```
   🎰 Yeni Oyun: {Oyun Adı} {emoji}

   {emoji} {Sağlayıcı}'in ... BayMavi'de!
   {kısa ikinci açıklama satırı}

   🤔 {clickbait soru}
   🎯 {CTA}
   ```

   Yani: başlık → BOŞ SATIR → açıklama (2 satır) → BOŞ SATIR → soru + CTA. Oyun temasını gerekiyorsa web'den doğrula. Uygun postlarda A/B varyant üret. Her posta 3 buton ekle (👤 Güncel Giriş https://bit.ly/bymvtlgrm · 📱 Twitter https://x.com/BayMavi_Resmi26 · 📸 Instagram https://bit.ly/baymavi-guncel). **18+/sorumlu oyna notu EKLEME** (sitede mevcut). Custom animated emoji kullanma (bot gönderemez), standart emoji seç.
6. **Slack'e gönder:** Takvim + caption'lar + kısa performans/rakip özetini #marketing-agent (C0BJ8UK5LLF) kanalına onaya gönder. Her slot için ✅/✏️ onay talimatı ekle.
7. **Yayın:** Onaylanan slotlar mevcut Telegram botu + Chrome ile programlanır (video öncelikli, yoksa web_banner). Onay olmadan yayınlama.

## Kurallar
- Onaysız yayın yok. CAPTCHA/bot-doğrulama geçme. 18+ notu ekleme.
- Kesin kazanç vaadi verme; oyun spec'leri (çarpan, max win) gerçek olmalı.
- **Görsel önceliği:** video varsa video; yoksa adında `banner` / `web_banner` geçen YATAY görsel. Asla `story` (dikey) veya `e_posta`/mail görseli kullanma.
- **Aralık:** iki gönderim arası en az 20 dakika; aynı anda toplu gönderme yok (her çalıştırmada tek post). Saatleri gün içine yay (ör. 11:00 / 15:00 / 19:00).
- Karışık sıra: aynı tür (oyun/bonus/turnuva) arka arkaya gelmesin.

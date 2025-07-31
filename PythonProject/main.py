import json

import pygame
import sys
import math
import random
import os


class SuperZiplayanTopOyunu:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Ekran ayarları
        self.GENISLIK = 1000
        self.YUKSEKLIK = 700
        self.ekran = pygame.display.set_mode((self.GENISLIK, self.YUKSEKLIK))
        pygame.display.set_caption("Süper Zıplayan Top - Ultra Gelişmiş Versiyon")

        self.oyun_durumu = 'ana_menu'  # 'ana_menu', 'oyun', 'game_over', 'ayarlar', 'nasil_oynanir', 'yukle'
        self.menu_secim = 0  # Menü seçimi
        self.ayarlar = {
            'ses_seviyesi': 0.7,
            'zorluk': 'normal',
            'otomatik_gecis': True
        }
        self.kayit_dosyasi = 'oyun_kaydi.json'

        # Ses dosyalarını yükle
        self.ses_hedef_kirilma = None
        self.ses_top_carpma = None
        self.ses_power_up = None
        self.ses_engel_carpisma = None

        self.kalan_atis = 5  # 5 atış hakkı
        self.menu_secim = 0  # Menü seçimi

        # Menu font
        self.menu_font = pygame.font.SysFont('Arial', 48)
        self.info_font = pygame.font.SysFont('Arial', 24)

        try:
            if not os.path.exists("glass_break.ogg"):
                import urllib.request
                urllib.request.urlretrieve("https://assets.mixkit.co/sfx/preview/mixkit-glass-break-756.mp3",
                                           "glass_break.ogg")

            if not os.path.exists("ball_bounce.wav"):
                import urllib.request
                urllib.request.urlretrieve("https://assets.mixkit.co/sfx/preview/mixkit-ball-bounce-476.mp3",
                                           "ball_bounce.wav")

            self.ses_hedef_kirilma = pygame.mixer.Sound("glass_break.ogg")
            self.ses_top_carpma = pygame.mixer.Sound("ball_bounce.wav")
            self.ses_top_carpma.set_volume(0.5)
        except Exception as e:
            print(f"Ses dosyaları yüklenirken hata: {e}")

        # Renkler
        self.BEYAZ = (255, 255, 255)
        self.SIYAH = (0, 0, 0)
        self.KIRMIZI = (255, 0, 0)
        self.MAVI = (0, 0, 255)
        self.YESIL = (0, 255, 0)
        self.GRI = (200, 200, 200)
        self.SARI = (255, 255, 0)
        self.TURUNCU = (255, 165, 0)
        self.MOR = (138, 43, 226)
        self.KOYU_MAVI = (25, 25, 112)
        self.ACIK_MAVI = (135, 206, 235)
        self.PEMBE = (255, 20, 147)
        self.ACIK_YESIL = (144, 238, 144)
        self.KOYU_KIRMIZI = (139, 0, 0)

        # Oyun değişkenleri
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.yercekimi = 0.8
        self.surtunme = 0.99

        # Sınırlar
        self.tavan_y = 50

        # Top özellikleri
        self.top_yaricap = 12
        self.top_x = 100
        self.top_y = self.YUKSEKLIK - 50 - self.top_yaricap
        self.top_hiz_x = 0
        self.top_hiz_y = 0
        self.top_firlatildi = False
        self.top_cekiliyor = False
        self.cekme_uzunlugu = 0
        self.cekme_aci = 0
        self.max_cekme_uzunlugu = 250

        # Power-up özellikleri
        self.top_buyuk = False
        self.top_buyuk_sure = 0
        self.top_hizli = False
        self.top_hizli_sure = 0

        self.magnet_aktif = False
        self.magnet_sure = 0

        # Parçacık efektleri
        self.parcaciklar = []
        self.hedef_parcaciklar = []
        self.ozel_efektler = []

        # Hedef özellikleri
        self.hedef_genislik = 50
        self.hedef_yukseklik = 30
        self.hedefler = []
        self.hedef_vuruldu = False
        self.hedef_parcalanma_suresi = 0

        # Skor
        self.skor = 0
        self.font = pygame.font.SysFont('Arial', 24)
        self.buyuk_font = pygame.font.SysFont('Arial', 36)

        # Zemin
        self.zemin_y = self.YUKSEKLIK - 50

        # Oyun durumu
        self.oyun_bitti = False

        # Level sistemi
        self.mevcut_level = 1
        self.max_level = 15
        self.combo = 0
        self.level_tamamlandi = False
        self.level_gecis_suresi = 0
        self.otomatik_gecis = True  # YENİ: Otomatik level geçişi

        # Engeller
        self.engeller = []
        self.hareketli_engeller = []

        # YENİ: Power-up'lar
        self.power_ups = []

        # YENİ: Özel hedefler
        self.ozel_hedefler = []

        # YENİ: Atış sayısı ve çoklu top
        self.atis_sayisi = 1
        self.toplar = []  # Çoklu top için

        # YENİ: Zaman tabanlı özellikler
        self.zaman_yavaslama = False
        self.zaman_yavaslama_sure = 0

        # İlk level'i başlat
        self.yeni_level_baslat()

    def oyunu_baslat(self):
        """Yeni oyun başlatırken top durumunu sıfırla"""
        self.oyun_durumu = 'oyun'
        self.kalan_atis = 5
        self.skor = 0
        self.combo = 0
        self.mevcut_level = 1
        self.top_firlatildi = False  # EKLE
        self.top_cekiliyor = False  # EKLE
        self.yeni_level_baslat()

    def nasil_oynanir_ciz(self):
        """Oyun kuralları ekranı"""
        # Arka plan
        self.gradient_ciz(self.ekran, self.KOYU_MAVI, self.ACIK_MAVI,
                          pygame.Rect(0, 0, self.GENISLIK, self.YUKSEKLIK))

        # Başlık
        baslik = self.buyuk_font.render("NASIL OYNANIR", True, self.SARI)
        baslik_rect = baslik.get_rect(center=(self.GENISLIK // 2, 50))
        self.ekran.blit(baslik, baslik_rect)

        # Kurallar
        kurallar = [
            "🎯 AMAÇ: Tüm hedefleri vurarak level'leri geç!",
            "",
            "🎮 KONTROLLER:",
            "• Fare ile topu çek ve bırak",
            "• R tuşu: Yeniden başla",
            "• ESC tuşu: Ana menüye dön",
            "",
            "🎯 HEDEFLER ve PUANLAR:",
            "• 🎈 Yeşil Balon: 100 puan",
            "• 🍾 Kırmızı Şişe: 200 puan (2 kez vur)",
            "• ❤️ Sarı Kalp: 500 puan (bonus)",
            "",
            "⚡ POWER-UP'LAR:",
            "• 🟠 Büyük Top (10 saniye)",
            "• 🟡 Hızlı Top (8 saniye)",
            "• 🟣 Magnet (12 saniye)",
            "",
            "⚠️ DİKKAT: 5 atış hakkın var!",
            "",
            "ESC - Ana Menüye Dön"
        ]

        y_pos = 100
        for kural in kurallar:
            if kural == "":
                y_pos += 10
                continue

            renk = self.SARI if kural.startswith(("🎯", "🎮", "⚡", "⚠️")) else self.BEYAZ
            font = self.font if not kural.startswith(("🎯", "🎮", "⚡", "⚠️")) else self.font

            yazi = font.render(kural, True, renk)
            self.ekran.blit(yazi, (50, y_pos))
            y_pos += 25

            def game_over_ciz(self):
                """YENİ: Game over ekranı"""
                # Yarı saydam overlay
                overlay = pygame.Surface((self.GENISLIK, self.YUKSEKLIK))
                overlay.set_alpha(200)
                overlay.fill(self.SIYAH)
                self.ekran.blit(overlay, (0, 0))

                # Game Over yazısı
                game_over_yazi = pygame.font.SysFont('Arial', 72).render("GAME OVER", True, self.KIRMIZI)
                game_over_rect = game_over_yazi.get_rect(center=(self.GENISLIK // 2, self.YUKSEKLIK // 2 - 100))
                self.ekran.blit(game_over_yazi, game_over_rect)

                # Final skor
                skor_yazi = self.buyuk_font.render(f"Final Skor: {self.skor}", True, self.BEYAZ)
                skor_rect = skor_yazi.get_rect(center=(self.GENISLIK // 2, self.YUKSEKLIK // 2 - 20))
                self.ekran.blit(skor_yazi, skor_rect)

                # Level
                level_yazi = self.font.render(f"Ulaşılan Level: {self.mevcut_level}", True, self.BEYAZ)
                level_rect = level_yazi.get_rect(center=(self.GENISLIK // 2, self.YUKSEKLIK // 2 + 20))
                self.ekran.blit(level_yazi, level_rect)

                # Yeniden başla
                restart_yazi = self.font.render("R - Yeniden Başla    ESC - Ana Menü", True, self.SARI)
                restart_rect = restart_yazi.get_rect(center=(self.GENISLIK // 2, self.YUKSEKLIK // 2 + 80))
                self.ekran.blit(restart_yazi, restart_rect)

    def atis_hakki_kontrol(self):
        """YENİ: Atış hakkı kontrolü"""
        if not self.top_firlatildi and len(self.toplar) == 0:
            # Tüm toplar durmuş
            all_targets_missed = True

            # En azından bir hedef vurulmuş mu kontrol et
            for hedef in self.hedefler + self.ozel_hedefler:
                if hedef['vuruldu']:
                    all_targets_missed = False
                    break

            # Hiçbir hedef vurulmadıysa atış hakkını azalt
            if all_targets_missed and self.kalan_atis > 0:
                self.kalan_atis -= 1
                self.combo = 0  # Combo sıfırla

                if self.kalan_atis <= 0:
                    self.oyun_durumu = 'game_over'
                else:
                    self.topu_resetle()

    def menu_ciz(self):
        """Ana menü çiz"""
        # Arka plan
        self.gradient_ciz(self.ekran, self.KOYU_MAVI, self.ACIK_MAVI,
                          pygame.Rect(0, 0, self.GENISLIK, self.YUKSEKLIK))

        # Başlık
        baslik = self.buyuk_font.render("SÜPER ZIPLAYAN TOP", True, self.SARI)
        baslik_rect = baslik.get_rect(center=(self.GENISLIK // 2, 100))
        self.ekran.blit(baslik, baslik_rect)

        # Menü seçenekleri
        menu_secenekleri = ["YENİ OYUN", "DEVAM ET", "AYARLAR", "NASIL OYNANIR", "ÇIKIŞ"]

        for i, secenek in enumerate(menu_secenekleri):
            renk = self.BEYAZ if i == self.menu_secim else self.GRI
            yazi = self.font.render(secenek, True, renk)
            yazi_rect = yazi.get_rect(center=(self.GENISLIK // 2, 250 + i * 60))

            # Seçili olan seçeneği vurgula
            if i == self.menu_secim:
                pygame.draw.rect(self.ekran, self.SARI,
                                 (yazi_rect.x - 10, yazi_rect.y - 5,
                                  yazi_rect.width + 20, yazi_rect.height + 10), 3)

            self.ekran.blit(yazi, yazi_rect)

    def yeni_level_baslat(self):
        """Yeni level başlat - GELİŞTİRİLDİ"""
        self.hedefler = []
        self.engeller = []
        self.hareketli_engeller = []
        self.power_ups = []
        self.ozel_hedefler = []
        self.toplar = []
        self.level_tamamlandi = False
        self.level_gecis_suresi = 0
        self.hedef_vuruldu = False

        # Level'e göre hedef sayısı
        hedef_sayisi = min(2 + (self.mevcut_level - 1), 8)

        # Hedefleri oluştur
        for i in range(hedef_sayisi):
            self.hedef_olustur()

        # Özel hedefler (level 5'ten sonra)
        if self.mevcut_level >= 5:
            ozel_hedef_sayisi = min((self.mevcut_level - 4) // 2, 2)
            for _ in range(ozel_hedef_sayisi):
                self.ozel_hedef_olustur()

        # Hareketsiz engeller (level 3'ten sonra)
        if self.mevcut_level >= 3:
            engel_sayisi = min(self.mevcut_level - 2, 4)
            for _ in range(engel_sayisi):
                engel = {
                    'x': random.randint(300, self.GENISLIK - 200),
                    'y': random.randint(200, 400),
                    'genislik': random.randint(60, 100),
                    'yukseklik': 20,
                    'tip': 'normal'
                }
                self.engeller.append(engel)

        # Hareketli engeller (level 6'dan sonra)
        if self.mevcut_level >= 6:
            hareketli_engel_sayisi = min((self.mevcut_level - 5) // 2, 3)
            for _ in range(hareketli_engel_sayisi):
                self.hareketli_engel_olustur()

        # Power-up'lar (level 4'ten sonra)
        if self.mevcut_level >= 4:
            power_up_sayisi = random.randint(1, 2)
            for _ in range(power_up_sayisi):
                self.power_up_olustur()

        # Topu resetle
        self.topu_resetle()

    def hedef_olustur(self):
        """Hedef oluştur - GELİŞTİRİLDİ"""
        tip_rastgele = random.random()
        if tip_rastgele < 0.2:
            tip = 'bonus'
        elif tip_rastgele < 0.35:
            tip = 'coklu_vurum'  # 2 kez vurulması gereken hedef
        else:
            tip = 'normal'

        hedef = {
            'x': random.randint(100, self.GENISLIK - 100),
            'y': random.randint(self.tavan_y + 10, self.YUKSEKLIK // 2),
            'genislik': self.hedef_genislik,
            'yukseklik': self.hedef_yukseklik,
            'vuruldu': False,
            'parcalanma_suresi': 0,
            'tip': tip,
            'vurum_sayisi': 2 if tip == 'coklu_vurum' else 1,
            'mevcut_vurum': 0
        }
        self.hedefler.append(hedef)

    def ozel_hedef_olustur(self):
        """YENİ: Özel hedefler oluştur"""
        ozel_tipler = ['hareketli', 'buyuyen', 'kaybolan']
        tip = random.choice(ozel_tipler)

        hedef = {
            'x': random.randint(150, self.GENISLIK - 150),
            'y': random.randint(self.tavan_y + 50, self.YUKSEKLIK // 2 - 50),
            'genislik': 60,
            'yukseklik': 40,
            'vuruldu': False,
            'tip': tip,
            'hiz_x': random.uniform(-2, 2) if tip == 'hareketli' else 0,
            'hiz_y': random.uniform(-1, 1) if tip == 'hareketli' else 0,
            'boyut_degisim': 0 if tip == 'buyuyen' else 0,
            'gorunurluk': 255,
            'gorunurluk_degisim': -2 if tip == 'kaybolan' else 0
        }
        self.ozel_hedefler.append(hedef)

    def hareketli_engel_olustur(self):
        """YENİ: Hareketli engel oluştur"""
        hareket_tipleri = ['yatay', 'dikey', 'dairesel', 'rastgele']
        tip = random.choice(hareket_tipleri)

        engel = {
            'x': random.randint(200, self.GENISLIK - 200),
            'y': random.randint(150, 450),
            'genislik': random.randint(80, 120),
            'yukseklik': 25,
            'tip': tip,
            'hiz_x': random.uniform(-3, 3),
            'hiz_y': random.uniform(-2, 2),
            'merkez_x': 0,
            'merkez_y': 0,
            'aci': 0,
            'yaricap': random.randint(50, 100)
        }

        if tip == 'dairesel':
            engel['merkez_x'] = engel['x']
            engel['merkez_y'] = engel['y']

        self.hareketli_engeller.append(engel)

    def power_up_olustur(self):
        """YENİ: Power-up oluştur - Geçici top kaldırıldı"""
        power_up_tipleri = ['buyuk_top', 'hizli_top', 'magnet', 'coklu_top', 'yavaslama']  # gecici_top kaldırıldı
        tip = random.choice(power_up_tipleri)

        power_up = {
            'x': random.randint(100, self.GENISLIK - 100),
            'y': random.randint(self.tavan_y + 30, self.YUKSEKLIK - 150),
            'genislik': 30,
            'yukseklik': 30,
            'tip': tip,
            'alinma_suresi': 0,
            'alinmis': False,
            'animasyon': 0
        }
        self.power_ups.append(power_up)

    def topu_resetle(self):
        """Top resetleme - aynı"""
        self.top_x = 100
        self.top_y = self.YUKSEKLIK - 50 - self.top_yaricap
        self.top_hiz_x = 0
        self.top_hiz_y = 0
        self.top_firlatildi = False
        self.top_cekiliyor = False
        self.cekme_uzunlugu = 0
        self.parcaciklar = []

    def power_up_al(self, power_up):
        """YENİ: Power-up alma - Geçici top kaldırıldı"""
        if power_up['tip'] == 'buyuk_top':
            self.top_buyuk = True
            self.top_buyuk_sure = 600  # 10 saniye (60 FPS * 10)
        elif power_up['tip'] == 'hizli_top':
            self.top_hizli = True
            self.top_hizli_sure = 480  # 8 saniye
        elif power_up['tip'] == 'magnet':
            self.magnet_aktif = True
            self.magnet_sure = 720  # 12 saniye
        elif power_up['tip'] == 'coklu_top':
            self.atis_sayisi = 3
        elif power_up['tip'] == 'yavaslama':
            self.zaman_yavaslama = True
            self.zaman_yavaslama_sure = 600  # 10 saniye

        power_up['alinmis'] = True
        power_up['alinma_suresi'] = 30

    def power_up_guncelle(self):
        """YENİ: Power-up güncellemeleri - Geçici top kaldırıldı"""
        # Power-up sürelerini azalt
        if self.top_buyuk_sure > 0:
            self.top_buyuk_sure -= 1
            if self.top_buyuk_sure == 0:  # Süre bittiğinde
                self.top_buyuk = False

        if self.top_hizli_sure > 0:
            self.top_hizli_sure -= 1
            if self.top_hizli_sure == 0:  # Süre bittiğinde
                self.top_hizli = False

        if self.magnet_sure > 0:
            self.magnet_sure -= 1
            if self.magnet_sure == 0:  # Süre bittiğinde
                self.magnet_aktif = False

        if self.zaman_yavaslama_sure > 0:
            self.zaman_yavaslama_sure -= 1
            if self.zaman_yavaslama_sure == 0:  # Süre bittiğinde
                self.zaman_yavaslama = False

    def parcacik_ekle(self, x, y, renkler, sayi=20, hiz=5):
        """Parçacık ekleme - aynı"""
        for _ in range(sayi):
            renk = random.choice(renkler)
            self.parcaciklar.append([
                [x, y],
                [random.uniform(-hiz, hiz), random.uniform(-hiz, hiz)],
                random.randint(2, 6),
                renk,
                random.randint(20, 40)
            ])

    def ozel_efekt_ekle(self, x, y, tip, renk):
        """YENİ: Özel efektler"""
        self.ozel_efektler.append({
            'x': x,
            'y': y,
            'tip': tip,
            'renk': renk,
            'sure': 60,
            'boyut': 1,
            'alpha': 255
        })

    def hedef_parcalanma_efekti(self, hedef):
        """Hedef parçalanma efekti - HATA DÜZELTİLDİ"""
        if self.ses_hedef_kirilma:
            self.ses_hedef_kirilma.play()

        # Özel efekt ekle
        self.ozel_efekt_ekle(int(hedef['x'] + hedef['genislik'] // 2),
                             int(hedef['y'] + hedef['yukseklik'] // 2),
                             'patlama', self.SARI)

        for _ in range(30):
            renk = random.choice([self.KIRMIZI, self.TURUNCU, self.SARI])
            self.hedef_parcaciklar.append([
                [random.randint(int(hedef['x']), int(hedef['x'] + hedef['genislik'])),
                 random.randint(int(hedef['y']), int(hedef['y'] + hedef['yukseklik']))],
                [random.uniform(-5, 5), random.uniform(-8, 0)],
                random.randint(3, 8),
                renk,
                random.randint(30, 50)
            ])

    def carpma_sesi_cal(self):
        """Çarpma sesi - aynı"""
        if self.ses_top_carpma:
            hiz = math.sqrt(self.top_hiz_x ** 2 + self.top_hiz_y ** 2)
            ses_seviyesi = min(hiz / 20, 1.0)
            self.ses_top_carpma.set_volume(ses_seviyesi)
            self.ses_top_carpma.play()

    def parcaciklari_guncelle(self):
        """Parçacık güncelleme - GELİŞTİRİLDİ"""
        # Normal parçacıklar
        i = 0
        while i < len(self.parcaciklar):
            parcacik = self.parcaciklar[i]
            parcacik[0][0] += parcacik[1][0]
            parcacik[0][1] += parcacik[1][1]
            parcacik[1][1] += 0.2
            parcacik[4] -= 1
            if parcacik[4] <= 0:
                self.parcaciklar.pop(i)
            else:
                i += 1

        # Hedef parçacıkları
        i = 0
        while i < len(self.hedef_parcaciklar):
            parcacik = self.hedef_parcaciklar[i]
            parcacik[0][0] += parcacik[1][0]
            parcacik[0][1] += parcacik[1][1]
            parcacik[1][1] += 0.15
            parcacik[4] -= 1
            if parcacik[4] <= 0:
                self.hedef_parcaciklar.pop(i)
            else:
                i += 1

        # Özel efektler
        i = 0
        while i < len(self.ozel_efektler):
            efekt = self.ozel_efektler[i]
            efekt['sure'] -= 1
            efekt['boyut'] += 0.1
            efekt['alpha'] -= 4
            if efekt['sure'] <= 0:
                self.ozel_efektler.pop(i)
            else:
                i += 1

    def ozel_hedefleri_guncelle(self):
        """YENİ: Özel hedefleri güncelle"""
        for hedef in self.ozel_hedefler:
            if hedef['vuruldu']:
                continue

            if hedef['tip'] == 'hareketli':
                hedef['x'] += hedef['hiz_x']
                hedef['y'] += hedef['hiz_y']

                # Sınırları kontrol et
                if hedef['x'] <= 0 or hedef['x'] + hedef['genislik'] >= self.GENISLIK:
                    hedef['hiz_x'] *= -1
                if hedef['y'] <= self.tavan_y or hedef['y'] + hedef['yukseklik'] >= self.YUKSEKLIK - 100:
                    hedef['hiz_y'] *= -1

            elif hedef['tip'] == 'buyuyen':
                hedef['boyut_degisim'] += 0.05
                buyume = math.sin(hedef['boyut_degisim']) * 10
                hedef['genislik'] = max(40, min(80, 60 + buyume))
                hedef['yukseklik'] = max(30, min(60, 40 + buyume))

            elif hedef['tip'] == 'kaybolan':
                hedef['gorunurluk'] += hedef['gorunurluk_degisim']
                if hedef['gorunurluk'] <= 50:
                    hedef['gorunurluk_degisim'] = 2
                elif hedef['gorunurluk'] >= 255:
                    hedef['gorunurluk_degisim'] = -2

    def hareketli_engelleri_guncelle(self):
        """YENİ: Hareketli engelleri güncelle"""
        for engel in self.hareketli_engeller:
            if engel['tip'] == 'yatay':
                engel['x'] += engel['hiz_x']
                if engel['x'] <= 0 or engel['x'] + engel['genislik'] >= self.GENISLIK:
                    engel['hiz_x'] *= -1

            elif engel['tip'] == 'dikey':
                engel['y'] += engel['hiz_y']
                if engel['y'] <= self.tavan_y or engel['y'] + engel['yukseklik'] >= self.YUKSEKLIK - 100:
                    engel['hiz_y'] *= -1

            elif engel['tip'] == 'dairesel':
                engel['aci'] += 0.05
                engel['x'] = engel['merkez_x'] + math.cos(engel['aci']) * engel['yaricap']
                engel['y'] = engel['merkez_y'] + math.sin(engel['aci']) * engel['yaricap']

            elif engel['tip'] == 'rastgele':
                engel['x'] += engel['hiz_x']
                engel['y'] += engel['hiz_y']

                if random.random() < 0.02:  # %2 şans ile yön değiştir
                    engel['hiz_x'] = random.uniform(-3, 3)
                    engel['hiz_y'] = random.uniform(-2, 2)

                if (engel['x'] <= 0 or engel['x'] + engel['genislik'] >= self.GENISLIK or
                        engel['y'] <= self.tavan_y or engel['y'] + engel['yukseklik'] >= self.YUKSEKLIK - 100):
                    engel['hiz_x'] *= -1
                    engel['hiz_y'] *= -1

    def hedef_vuruldu_mu(self):
        """Hedef vurulma kontrolü - GELİŞTİRİLDİ"""
        hedef_vuruldu = False
        mevcut_yaricap = self.top_yaricap * 1.5 if self.top_buyuk else self.top_yaricap

        # Normal hedefler
        for hedef in self.hedefler:
            if hedef['vuruldu']:
                continue

            if self.carpisma_kontrol(self.top_x, self.top_y, mevcut_yaricap,
                                     hedef['x'], hedef['y'], hedef['genislik'], hedef['yukseklik']):

                if hedef['tip'] == 'coklu_vurum':
                    hedef['mevcut_vurum'] += 1
                    if hedef['mevcut_vurum'] >= hedef['vurum_sayisi']:
                        hedef['vuruldu'] = True
                        hedef['parcalanma_suresi'] = 30
                        self.hedef_parcalanma_efekti(hedef)
                else:
                    hedef['vuruldu'] = True
                    hedef['parcalanma_suresi'] = 30
                    self.hedef_parcalanma_efekti(hedef)

                # Puan hesapla
                puan = 500 if hedef['tip'] == 'bonus' else 200 if hedef['tip'] == 'coklu_vurum' else 100
                self.combo += 1
                puan += self.combo * 15
                self.skor += puan

                self.parcacik_ekle(self.top_x, self.top_y, [self.MAVI, self.SARI, self.BEYAZ], 30, 7)
                self.carpma_sesi_cal()
                hedef_vuruldu = True
                break

        # Özel hedefler
        for hedef in self.ozel_hedefler:
            if hedef['vuruldu']:
                continue

            if self.carpisma_kontrol(self.top_x, self.top_y, mevcut_yaricap,
                                     hedef['x'], hedef['y'], hedef['genislik'], hedef['yukseklik']):
                hedef['vuruldu'] = True
                self.hedef_parcalanma_efekti(hedef)
                self.skor += 300 + self.combo * 20
                self.combo += 1
                hedef_vuruldu = True
                break

        # Power-up'ları kontrol et
        for power_up in self.power_ups:
            if power_up['alinmis']:
                continue

            if self.carpisma_kontrol(self.top_x, self.top_y, mevcut_yaricap,
                                     power_up['x'], power_up['y'], power_up['genislik'], power_up['yukseklik']):
                self.power_up_al(power_up)
                self.parcacik_ekle(power_up['x'], power_up['y'], [self.MOR, self.PEMBE], 20, 6)

        # Tüm hedefler vuruldu mu kontrol et - YENİ: Otomatik geçiş
        normal_hedefler_bitti = all(hedef['vuruldu'] for hedef in self.hedefler)
        ozel_hedefler_bitti = all(hedef['vuruldu'] for hedef in self.ozel_hedefler)

        if normal_hedefler_bitti and ozel_hedefler_bitti and not self.level_tamamlandi:
            self.level_tamamlandi = True
            self.level_gecis_suresi = 180 if self.otomatik_gecis else 0  # 3 saniye otomatik geçiş

        return hedef_vuruldu

    def carpisma_kontrol(self, top_x, top_y, top_yaricap, nesne_x, nesne_y, nesne_genislik, nesne_yukseklik):
        """YENİ: Genel çarpışma kontrolü"""
        top_sol = top_x - top_yaricap
        top_sag = top_x + top_yaricap
        top_ust = top_y - top_yaricap
        top_alt = top_y + top_yaricap

        nesne_sol = nesne_x
        nesne_sag = nesne_x + nesne_genislik
        nesne_ust = nesne_y
        nesne_alt = nesne_y + nesne_yukseklik

        return (top_sag > nesne_sol and top_sol < nesne_sag and
                top_alt > nesne_ust and top_ust < nesne_alt)

    def engel_carpisma_kontrol(self):
        """Engel çarpışma kontrolü - DÜZELTİLDİ"""
        mevcut_yaricap = self.top_yaricap * 1.5 if self.top_buyuk else self.top_yaricap

        # Hareketsiz engeller
        for engel in self.engeller:
            if not self.top_gecici if hasattr(self, 'top_gecici') else True:
                if self.carpisma_kontrol(self.top_x, self.top_y, mevcut_yaricap,
                                         engel['x'], engel['y'], engel['genislik'], engel['yukseklik']):
                    self.engel_carpisma_islemi(engel)
                    return  # Bir engele çarptıktan sonra çık

        # Hareketli engeller
        for engel in self.hareketli_engeller:
            if not self.top_gecici if hasattr(self, 'top_gecici') else True:
                if self.carpisma_kontrol(self.top_x, self.top_y, mevcut_yaricap,
                                         int(engel['x']), int(engel['y']), engel['genislik'], engel['yukseklik']):
                    self.engel_carpisma_islemi(engel)
                    return  # Bir engele çarptıktan sonra çık

    def engel_carpisma_islemi(self, engel):
        """Engel çarpışma işlemi - GELİŞTİRİLDİ"""
        # Çarpışma yönünü daha iyi belirle
        engel_merkez_x = engel['x'] + engel['genislik'] / 2
        engel_merkez_y = engel['y'] + engel['yukseklik'] / 2

        # Çarpışma vektörü
        dx = self.top_x - engel_merkez_x
        dy = self.top_y - engel_merkez_y

        # En yakın kenarı bul
        if abs(dx / engel['genislik']) > abs(dy / engel['yukseklik']):
            # Yatay çarpışma
            self.top_hiz_x *= -0.8
            if dx > 0:
                self.top_x = engel['x'] + engel['genislik'] + self.top_yaricap + 2
            else:
                self.top_x = engel['x'] - self.top_yaricap - 2
        else:
            # Dikey çarpışma
            self.top_hiz_y *= -0.8
            if dy > 0:
                self.top_y = engel['y'] + engel['yukseklik'] + self.top_yaricap + 2
            else:
                self.top_y = engel['y'] - self.top_yaricap - 2

        # Efektler
        self.carpma_sesi_cal()
        self.parcacik_ekle(self.top_x, self.top_y, [self.TURUNCU, self.KIRMIZI], 15, 4)
        self.combo = 0  # Engele çarpınca combo sıfırlanır

    def magnet_etkisi(self):
        """YENİ: Magnet power-up etkisi"""
        if not self.magnet_aktif:
            return

        magnet_menzil = 100
        for hedef in self.hedefler + self.ozel_hedefler:
            if hedef['vuruldu']:
                continue

            hedef_merkez_x = hedef['x'] + hedef['genislik'] / 2
            hedef_merkez_y = hedef['y'] + hedef['yukseklik'] / 2

            mesafe = math.sqrt((self.top_x - hedef_merkez_x) ** 2 + (self.top_y - hedef_merkez_y) ** 2)

            if mesafe < magnet_menzil:
                # Topu hedefe doğru çek
                aci = math.atan2(hedef_merkez_y - self.top_y, hedef_merkez_x - self.top_x)
                cekme_kuvveti = (magnet_menzil - mesafe) / magnet_menzil * 0.3

                self.top_hiz_x += math.cos(aci) * cekme_kuvveti
                self.top_hiz_y += math.sin(aci) * cekme_kuvveti

    def cekme_cizgisi_ciz(self):
        """Çekme çizgisi çizimi - daha belirgin hale getirildi"""
        if self.top_cekiliyor and not self.top_firlatildi:
            fare_x, fare_y = pygame.mouse.get_pos()

            # Ana çizgi
            pygame.draw.line(self.ekran, self.BEYAZ,
                             (self.top_x, self.top_y), (fare_x, fare_y), 3)

            # Kuvvet göstergesi
            cekme_yuzde = min(self.cekme_uzunlugu / self.max_cekme_uzunlugu, 1.0)
            renk = (
                int(255 * cekme_yuzde),
                int(255 * (1 - cekme_yuzde)),
                0
            )
            pygame.draw.line(self.ekran, renk,
                             (50, 50), (50 + 200 * cekme_yuzde, 50), 20)

    def topu_firlat(self):
        """Top fırlatma - GELİŞTİRİLDİ"""
        hiz_carpani = 1.5 if self.top_hizli else 1.0

        self.top_hiz_x = math.cos(self.cekme_aci) * self.cekme_uzunlugu * 0.25 * hiz_carpani
        self.top_hiz_y = math.sin(self.cekme_aci) * self.cekme_uzunlugu * 0.25 * hiz_carpani
        self.top_firlatildi = True
        self.top_cekiliyor = False

        # Çoklu top power-up'ı varsa
        if self.atis_sayisi > 1:
            for i in range(self.atis_sayisi - 1):
                aci_sapma = (i + 1) * 0.3 - 0.15
                yeni_top = {
                    'x': self.top_x,
                    'y': self.top_y,
                    'hiz_x': math.cos(self.cekme_aci + aci_sapma) * self.cekme_uzunlugu * 0.25 * hiz_carpani,
                    'hiz_y': math.sin(self.cekme_aci + aci_sapma) * self.cekme_uzunlugu * 0.25 * hiz_carpani,
                    'yaricap': self.top_yaricap,
                    'aktif': True
                }
                self.toplar.append(yeni_top)
            self.atis_sayisi = 1

    def topu_guncelle(self):
        """Top güncelleme - GELİŞTİRİLDİ"""
        zaman_carpani = 0.5 if self.zaman_yavaslama else 1.0

        if self.top_firlatildi:
            self.top_hiz_y += self.yercekimi * zaman_carpani
            self.top_hiz_x *= self.surtunme

            self.top_x += self.top_hiz_x * zaman_carpani
            self.top_y += self.top_hiz_y * zaman_carpani

            # Magnet etkisi
            self.magnet_etkisi()

            # Tavan çarpışması
            if self.top_y - self.top_yaricap <= self.tavan_y:
                self.top_y = self.tavan_y + self.top_yaricap
                self.top_hiz_y *= -0.8
                self.carpma_sesi_cal()

            # Zemin çarpışması
            if self.top_y + self.top_yaricap >= self.zemin_y:
                self.top_y = self.zemin_y - self.top_yaricap
                self.top_hiz_y *= -0.9
                self.top_hiz_x *= 0.95
                self.carpma_sesi_cal()

                if abs(self.top_hiz_y) < 0.5 and abs(self.top_hiz_x) < 0.5:
                    self.top_firlatildi = False
                    if not any(
                            hedef['vuruldu'] for hedef in self.hedefler + self.ozel_hedefler if not hedef['vuruldu']):
                        self.combo = 0

            # Duvar çarpışmaları
            if self.top_x - self.top_yaricap <= 0 or self.top_x + self.top_yaricap >= self.GENISLIK:
                self.top_hiz_x *= -0.95
                self.carpma_sesi_cal()
                if self.top_x - self.top_yaricap <= 0:
                    self.top_x = self.top_yaricap
                else:
                    self.top_x = self.GENISLIK - self.top_yaricap

            # Engel çarpışması
            self.engel_carpisma_kontrol()

            # Hedef kontrolü
            self.hedef_vuruldu_mu()

        # Çoklu topları güncelle
        self.coklu_toplari_guncelle()

    def coklu_toplari_guncelle(self):
        """YENİ: Çoklu topları güncelle"""
        zaman_carpani = 0.5 if self.zaman_yavaslama else 1.0

        for top in self.toplar[:]:
            if not top['aktif']:
                continue

            top['hiz_y'] += self.yercekimi * zaman_carpani
            top['hiz_x'] *= self.surtunme

            top['x'] += top['hiz_x'] * zaman_carpani
            top['y'] += top['hiz_y'] * zaman_carpani

            # Çarpışma kontrolleri
            if top['y'] - top['yaricap'] <= self.tavan_y:
                top['y'] = self.tavan_y + top['yaricap']
                top['hiz_y'] *= -0.8

            if top['y'] + top['yaricap'] >= self.zemin_y:
                top['y'] = self.zemin_y - top['yaricap']
                top['hiz_y'] *= -0.9
                top['hiz_x'] *= 0.95

                if abs(top['hiz_y']) < 0.5 and abs(top['hiz_x']) < 0.5:
                    top['aktif'] = False

            if top['x'] - top['yaricap'] <= 0 or top['x'] + top['yaricap'] >= self.GENISLIK:
                top['hiz_x'] *= -0.95
                if top['x'] - top['yaricap'] <= 0:
                    top['x'] = top['yaricap']
                else:
                    top['x'] = self.GENISLIK - top['yaricap']

            # Hedef çarpışması kontrol et
            self.coklu_top_hedef_kontrol(top)

        # Pasif topları kaldır
        self.toplar = [top for top in self.toplar if top['aktif']]

    def coklu_top_hedef_kontrol(self, top):
        """YENİ: Çoklu top hedef kontrolü"""
        # Normal hedefler
        for hedef in self.hedefler:
            if hedef['vuruldu']:
                continue

            if self.carpisma_kontrol(top['x'], top['y'], top['yaricap'],
                                     hedef['x'], hedef['y'], hedef['genislik'], hedef['yukseklik']):
                hedef['vuruldu'] = True
                hedef['parcalanma_suresi'] = 30
                self.hedef_parcalanma_efekti(hedef)
                self.skor += 100 + self.combo * 15
                self.combo += 1
                break

        # Özel hedefler
        for hedef in self.ozel_hedefler:
            if hedef['vuruldu']:
                continue

            if self.carpisma_kontrol(top['x'], top['y'], top['yaricap'],
                                     hedef['x'], hedef['y'], hedef['genislik'], hedef['yukseklik']):
                hedef['vuruldu'] = True
                self.hedef_parcalanma_efekti(hedef)
                self.skor += 300 + self.combo * 20
                self.combo += 1
                break

    def oyunu_kaydet(self):
        """Oyun durumunu kaydet"""
        kayit = {
            'level': self.mevcut_level,
            'skor': self.skor,
            'kalan_atis': self.kalan_atis,
            'ayarlar': self.ayarlar
        }

        try:
            with open(self.kayit_dosyasi, 'w') as f:
                json.dump(kayit, f)
            return True
        except:
            return False

    def oyunu_yukle(self):
        """Kayıtlı oyunu yükle"""
        try:
            with open(self.kayit_dosyasi, 'r') as f:
                kayit = json.load(f)

            self.mevcut_level = kayit['level']
            self.skor = kayit['skor']
            self.kalan_atis = kayit['kalan_atis']
            self.ayarlar = kayit['ayarlar']

            self.yeni_level_baslat()
            return True
        except:
            return False

    def olaylari_isle(self):
        for event in pygame.event.get():

            # Fare olaylarını kontrol et (EKLEME)
            if self.oyun_durumu == 'oyun':  # Sadece oyun ekranında fareyi kontrol et
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Sol fare butonu
                        fare_x, fare_y = event.pos
                        # Topun üzerine tıklanmış mı kontrol et
                        mesafe = math.sqrt((fare_x - self.top_x) ** 2 + (fare_y - self.top_y) ** 2)
                        if mesafe <= self.top_yaricap:
                            self.top_cekiliyor = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.top_cekiliyor:
                        self.topu_firlat()

            if event.type == pygame.QUIT:
                if self.oyun_durumu == 'oyun':
                    self.oyunu_kaydet()
                pygame.quit()
                sys.exit()




            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.oyun_durumu in ['ayarlar', 'nasil_oynanir']:
                        self.oyun_durumu = 'ana_menu'
                    elif self.oyun_durumu == 'oyun':
                        self.oyunu_kaydet()
                        self.oyun_durumu = 'ana_menu'

                if event.key == pygame.K_UP:
                    if self.oyun_durumu == 'ana_menu':
                        self.menu_secim = (self.menu_secim - 1) % 5
                    elif self.oyun_durumu == 'ayarlar':
                        self.menu_secim = (self.menu_secim - 1) % 4

                if event.key == pygame.K_DOWN:
                    if self.oyun_durumu == 'ana_menu':
                        self.menu_secim = (self.menu_secim + 1) % 5
                    elif self.oyun_durumu == 'ayarlar':
                        self.menu_secim = (self.menu_secim + 1) % 4

                if event.key == pygame.K_RETURN:
                    if self.oyun_durumu == 'ana_menu':
                        if self.menu_secim == 0:  # Yeni Oyun
                            self.oyunu_baslat()
                        elif self.menu_secim == 1:  # Devam Et
                            if self.oyunu_yukle():
                                self.oyun_durumu = 'oyun'
                        elif self.menu_secim == 2:  # Ayarlar
                            self.oyun_durumu = 'ayarlar'
                            self.menu_secim = 0
                        elif self.menu_secim == 3:  # Nasıl Oynanır
                            self.oyun_durumu = 'nasil_oynanir'
                        elif self.menu_secim == 4:  # Çıkış
                            pygame.quit()
                            sys.exit()

                    elif self.oyun_durumu == 'ayarlar':
                        if self.menu_secim == 3:  # Ana Menü
                            self.oyun_durumu = 'ana_menu'
                            self.menu_secim = 0

    def cekme_hesapla(self):
        """Çekme hesaplama - fare pozisyonunu kullanarak güncellendi"""
        if self.top_cekiliyor and not self.top_firlatildi:
            fare_x, fare_y = pygame.mouse.get_pos()
            dx = self.top_x - fare_x
            dy = self.top_y - fare_y
            self.cekme_uzunlugu = min(math.sqrt(dx * dx + dy * dy), self.max_cekme_uzunlugu)
            self.cekme_aci = math.atan2(dy, dx)

            # Çekme çizgisini çiz (gerçek zamanlı görsel feedback)
            self.cekme_cizgisi_ciz()

    def gradient_ciz(self, surface, renk1, renk2, rect):
        """Gradient çizme - aynı"""
        for i in range(rect.height):
            ratio = i / rect.height
            r = int(renk1[0] * (1 - ratio) + renk2[0] * ratio)
            g = int(renk1[1] * (1 - ratio) + renk2[1] * ratio)
            b = int(renk1[2] * (1 - ratio) + renk2[2] * ratio)
            pygame.draw.line(surface, (r, g, b),
                             (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))

    def power_up_ciz(self):
        """YENİ: Power-up çizimi - Geçici top kaldırıldı"""
        for power_up in self.power_ups:
            if power_up['alinmis']:
                continue

            # Animasyon
            power_up['animasyon'] += 0.1
            y_offset = math.sin(power_up['animasyon']) * 3

            x = power_up['x']
            y = power_up['y'] + y_offset

            # Power-up türüne göre renk ve şekil
            if power_up['tip'] == 'buyuk_top':
                pygame.draw.circle(self.ekran, self.TURUNCU, (int(x + 15), int(y + 15)), 15)
                pygame.draw.circle(self.ekran, self.BEYAZ, (int(x + 15), int(y + 15)), 15, 2)
                # Büyük top simgesi
                pygame.draw.circle(self.ekran, self.BEYAZ, (int(x + 15), int(y + 15)), 8)

            elif power_up['tip'] == 'hizli_top':
                pygame.draw.rect(self.ekran, self.SARI, (x, y, 30, 30))
                pygame.draw.rect(self.ekran, self.BEYAZ, (x, y, 30, 30), 2)
                # Hız çizgileri
                for i in range(3):
                    pygame.draw.line(self.ekran, self.BEYAZ,
                                     (x + 5 + i * 7, y + 10), (x + 5 + i * 7, y + 20), 2)

            elif power_up['tip'] == 'magnet':
                pygame.draw.rect(self.ekran, self.MOR, (x, y, 30, 30))
                pygame.draw.rect(self.ekran, self.BEYAZ, (x, y, 30, 30), 2)
                # Magnet simgesi
                pygame.draw.arc(self.ekran, self.BEYAZ, (x + 5, y + 5, 20, 20), 0, math.pi, 3)

            elif power_up['tip'] == 'coklu_top':
                pygame.draw.rect(self.ekran, self.YESIL, (x, y, 30, 30))
                pygame.draw.rect(self.ekran, self.BEYAZ, (x, y, 30, 30), 2)
                # Çoklu top simgesi
                pygame.draw.circle(self.ekran, self.BEYAZ, (int(x + 10), int(y + 15)), 4)
                pygame.draw.circle(self.ekran, self.BEYAZ, (int(x + 20), int(y + 15)), 4)

            elif power_up['tip'] == 'yavaslama':
                pygame.draw.rect(self.ekran, self.PEMBE, (x, y, 30, 30))
                pygame.draw.rect(self.ekran, self.BEYAZ, (x, y, 30, 30), 2)
                # Saat simgesi
                pygame.draw.circle(self.ekran, self.BEYAZ, (int(x + 15), int(y + 15)), 8, 2)
                pygame.draw.line(self.ekran, self.BEYAZ, (x + 15, y + 15), (x + 15, y + 8), 2)

    def hedef_ciz_sise(self, x, y, genislik, yukseklik, renk):
        """Şişe şeklinde hedef çiz"""
        # Şişe gövdesi
        pygame.draw.rect(self.ekran, renk, (x + 10, y + 15, genislik - 20, yukseklik - 15))
        # Şişe boynu
        pygame.draw.rect(self.ekran, renk, (x + 15, y + 5, genislik - 30, 15))
        # Şişe kapağı
        pygame.draw.rect(self.ekran, self.KOYU_KIRMIZI, (x + 12, y, genislik - 24, 8))
        # Parlama efekti
        pygame.draw.line(self.ekran, self.BEYAZ, (x + 15, y + 20), (x + 15, y + yukseklik - 5), 2)

    def hedef_ciz_balon(self, x, y, genislik, yukseklik, renk):
        """Balon şeklinde hedef çiz"""
        # Ana balon
        merkez_x = x + genislik // 2
        merkez_y = y + yukseklik // 2
        yaricap = min(genislik, yukseklik) // 2 - 2
        pygame.draw.circle(self.ekran, renk, (merkez_x, merkez_y), yaricap)

        # Balon parlama efekti
        pygame.draw.circle(self.ekran, self.BEYAZ, (merkez_x - 8, merkez_y - 8), 4)

        # Balon ipi
        pygame.draw.line(self.ekran, self.SIYAH, (merkez_x, merkez_y + yaricap),
                         (merkez_x, merkez_y + yaricap + 15), 2)

        # Balon düğümü
        pygame.draw.circle(self.ekran, self.SIYAH, (merkez_x, merkez_y + yaricap + 15), 2)

    def hedef_ciz_kalp(self, x, y, genislik, yukseklik, renk):
        """Kalp şeklinde hedef çiz"""
        merkez_x = x + genislik // 2
        merkez_y = y + yukseklik // 2

        # Kalp şekli için noktalar
        noktalar = []
        for i in range(20):
            t = i * 2 * math.pi / 20
            kalp_x = 16 * (math.sin(t) ** 3)
            kalp_y = -13 * math.cos(t) + 5 * math.cos(2 * t) + 2 * math.cos(3 * t) + math.cos(4 * t)
            noktalar.append((merkez_x + kalp_x, merkez_y + kalp_y))

        if len(noktalar) > 2:
            pygame.draw.polygon(self.ekran, renk, noktalar)
            pygame.draw.polygon(self.ekran, self.BEYAZ, noktalar, 2)

    def ayarlar_ciz(self):
        """Ayarlar menüsü"""
        # Arka plan
        self.gradient_ciz(self.ekran, self.KOYU_MAVI, self.ACIK_MAVI,
                          pygame.Rect(0, 0, self.GENISLIK, self.YUKSEKLIK))

        # Başlık
        baslik = self.buyuk_font.render("AYARLAR", True, self.SARI)
        baslik_rect = baslik.get_rect(center=(self.GENISLIK // 2, 50))
        self.ekran.blit(baslik, baslik_rect)

        # Ayarlar seçenekleri
        ayarlar = [
            f"Ses Seviyesi: {int(self.ayarlar['ses_seviyesi'] * 100)}%",
            f"Zorluk: {self.ayarlar['zorluk'].upper()}",
            f"Otomatik Geçiş: {'AÇIK' if self.ayarlar['otomatik_gecis'] else 'KAPALI'}",
            "ANA MENÜ"
        ]

        for i, ayar in enumerate(ayarlar):
            renk = self.BEYAZ if i == self.menu_secim else self.GRI
            yazi = self.font.render(ayar, True, renk)
            yazi_rect = yazi.get_rect(center=(self.GENISLIK // 2, 150 + i * 60))

            if i == self.menu_secim:
                pygame.draw.rect(self.ekran, self.SARI,
                                 (yazi_rect.x - 10, yazi_rect.y - 5,
                                  yazi_rect.width + 20, yazi_rect.height + 10), 3)

            self.ekran.blit(yazi, yazi_rect)

    def ciz(self):
        """Çizim fonksiyonu - Hedef tasarımları ve power-up süre göstergeleri geliştirildi"""
        # Gradient arka plan
        self.gradient_ciz(self.ekran, self.KOYU_MAVI, self.ACIK_MAVI,
                          pygame.Rect(0, 0, self.GENISLIK, self.YUKSEKLIK))

        # Tavan çizgisi
        pygame.draw.line(self.ekran, self.BEYAZ, (0, self.tavan_y), (self.GENISLIK, self.tavan_y), 3)

        # Zemin çiz
        pygame.draw.rect(self.ekran, self.SIYAH, (0, self.zemin_y, self.GENISLIK, self.YUKSEKLIK - self.zemin_y))

        # Hareketsiz engelleri çiz
        for engel in self.engeller:
            pygame.draw.rect(self.ekran, self.KIRMIZI,
                             (engel['x'], engel['y'], engel['genislik'], engel['yukseklik']))
            pygame.draw.rect(self.ekran, self.BEYAZ,
                             (engel['x'], engel['y'], engel['genislik'], engel['yukseklik']), 2)

        # Hareketli engelleri çiz
        for engel in self.hareketli_engeller:
            # Hareketli engeller için farklı renk
            pygame.draw.rect(self.ekran, self.KOYU_KIRMIZI,
                             (int(engel['x']), int(engel['y']), engel['genislik'], engel['yukseklik']))
            pygame.draw.rect(self.ekran, self.SARI,
                             (int(engel['x']), int(engel['y']), engel['genislik'], engel['yukseklik']), 2)

            # Hareket yönü göstergesi
            merkez_x = int(engel['x'] + engel['genislik'] / 2)
            merkez_y = int(engel['y'] + engel['yukseklik'] / 2)
            pygame.draw.circle(self.ekran, self.SARI, (merkez_x, merkez_y), 3)

        # Normal hedefleri çiz - YENİ TASARIMLAR
        for hedef in self.hedefler:
            if not hedef['vuruldu']:
                if hedef['tip'] == 'bonus':
                    renk = self.SARI
                    self.hedef_ciz_kalp(hedef['x'], hedef['y'], hedef['genislik'], hedef['yukseklik'], renk)
                elif hedef['tip'] == 'coklu_vurum':
                    # Vurulma durumuna göre renk değişimi
                    if hedef['mevcut_vurum'] > 0:
                        renk = self.TURUNCU
                    else:
                        renk = self.KIRMIZI
                    self.hedef_ciz_sise(hedef['x'], hedef['y'], hedef['genislik'], hedef['yukseklik'], renk)

                    # Çoklu vurum hedefinde sayı göster
                    kalan = hedef['vurum_sayisi'] - hedef['mevcut_vurum']
                    sayi_yazi = self.font.render(str(kalan), True, self.BEYAZ)
                    self.ekran.blit(sayi_yazi, (hedef['x'] + 20, hedef['y'] + 5))
                else:
                    renk = self.YESIL
                    self.hedef_ciz_balon(hedef['x'], hedef['y'], hedef['genislik'], hedef['yukseklik'], renk)

        # Özel hedefleri çiz
        for hedef in self.ozel_hedefler:
            if hedef['vuruldu']:
                continue

            if hedef['tip'] == 'hareketli':
                renk = self.MOR
                self.hedef_ciz_balon(int(hedef['x']), int(hedef['y']),
                                     int(hedef['genislik']), int(hedef['yukseklik']), renk)
            elif hedef['tip'] == 'buyuyen':
                renk = self.PEMBE
                self.hedef_ciz_kalp(int(hedef['x']), int(hedef['y']),
                                    int(hedef['genislik']), int(hedef['yukseklik']), renk)
            elif hedef['tip'] == 'kaybolan':
                renk = self.ACIK_YESIL
                # Kaybolan hedef için alpha değeri
                surface = pygame.Surface((hedef['genislik'], hedef['yukseklik']))
                surface.set_alpha(hedef['gorunurluk'])
                surface.fill(renk)
                self.ekran.blit(surface, (int(hedef['x']), int(hedef['y'])))
                # Çerçeve çiz
                pygame.draw.rect(self.ekran, self.BEYAZ,
                                 (int(hedef['x']), int(hedef['y']),
                                  int(hedef['genislik']), int(hedef['yukseklik'])), 2)

        # Power-up'ları çiz
        self.power_up_ciz()

        # Özel efektleri çiz
        for efekt in self.ozel_efektler:
            if efekt['tip'] == 'patlama':
                surface = pygame.Surface((int(efekt['boyut'] * 20), int(efekt['boyut'] * 20)))
                surface.set_alpha(efekt['alpha'])
                surface.fill(efekt['renk'])
                self.ekran.blit(surface, (efekt['x'] - efekt['boyut'] * 10, efekt['y'] - efekt['boyut'] * 10))

        # Parçacıkları çiz
        for parcacik in self.hedef_parcaciklar:
            pygame.draw.circle(self.ekran, parcacik[3], (int(parcacik[0][0]), int(parcacik[0][1])), parcacik[2])

        for parcacik in self.parcaciklar:
            pygame.draw.circle(self.ekran, parcacik[3], (int(parcacik[0][0]), int(parcacik[0][1])), parcacik[2])

        # Ana topu çiz - GEÇİCİ TOP KALDIRILDI
        mevcut_yaricap = int(self.top_yaricap * 1.5) if self.top_buyuk else self.top_yaricap
        top_rengi = self.SARI if self.top_hizli else self.MAVI

        pygame.draw.circle(self.ekran, top_rengi, (int(self.top_x), int(self.top_y)), mevcut_yaricap)
        pygame.draw.circle(self.ekran, self.BEYAZ, (int(self.top_x), int(self.top_y)), mevcut_yaricap, 2)

        # Çoklu topları çiz
        for top in self.toplar:
            if top['aktif']:
                pygame.draw.circle(self.ekran, self.ACIK_MAVI, (int(top['x']), int(top['y'])), top['yaricap'])
                pygame.draw.circle(self.ekran, self.BEYAZ, (int(top['x']), int(top['y'])), top['yaricap'], 1)

        # Magnet etkisi göster
        if self.magnet_aktif:
            pygame.draw.circle(self.ekran, (255, 0, 255, 50), (int(self.top_x), int(self.top_y)), 100, 2)

        # Çekme çizgisi
        self.cekme_cizgisi_ciz()

        # HUD - Geliştirilmiş süre göstergeleri
        skor_yazi = self.font.render(f'Skor: {self.skor}', True, self.BEYAZ)
        self.ekran.blit(skor_yazi, (10, 10))

        level_yazi = self.font.render(f'Level: {self.mevcut_level}/{self.max_level}', True, self.BEYAZ)
        self.ekran.blit(level_yazi, (200, 10))

        if self.combo > 1:
            combo_yazi = self.font.render(f'Combo x{self.combo}!', True, self.SARI)
            self.ekran.blit(combo_yazi, (400, 10))

        # Power-up durumu göster - GELİŞTİRİLMİŞ SÜRE GÖSTERGESİ
        y_pos = 40
        if self.top_buyuk:
            kalan_saniye = (self.top_buyuk_sure // 60) + 1
            power_yazi = self.font.render(f'Büyük Top: {kalan_saniye}s', True, self.TURUNCU)
            self.ekran.blit(power_yazi, (10, y_pos))

            # Süre çubuğu
            bar_width = 100
            bar_height = 8
            doluluk = self.top_buyuk_sure / 600.0  # Maksimum süre 600
            pygame.draw.rect(self.ekran, self.GRI, (150, y_pos + 8, bar_width, bar_height))
            pygame.draw.rect(self.ekran, self.TURUNCU, (150, y_pos + 8, bar_width * doluluk, bar_height))
            y_pos += 30

        if self.top_hizli:
            kalan_saniye = (self.top_hizli_sure // 60) + 1
            power_yazi = self.font.render(f'Hızlı Top: {kalan_saniye}s', True, self.SARI)
            self.ekran.blit(power_yazi, (10, y_pos))

            # Süre çubuğu
            bar_width = 100
            bar_height = 8
            doluluk = self.top_hizli_sure / 480.0  # Maksimum süre 480
            pygame.draw.rect(self.ekran, self.GRI, (150, y_pos + 8, bar_width, bar_height))
            pygame.draw.rect(self.ekran, self.SARI, (150, y_pos + 8, bar_width * doluluk, bar_height))
            y_pos += 30

        if self.magnet_aktif:
            kalan_saniye = (self.magnet_sure // 60) + 1
            power_yazi = self.font.render(f'Magnet: {kalan_saniye}s', True, self.MOR)
            self.ekran.blit(power_yazi, (10, y_pos))

            # Süre çubuğu
            bar_width = 100
            bar_height = 8
            doluluk = self.magnet_sure / 720.0  # Maksimum süre 720
            pygame.draw.rect(self.ekran, self.GRI, (150, y_pos + 8, bar_width, bar_height))
            pygame.draw.rect(self.ekran, self.MOR, (150, y_pos + 8, bar_width * doluluk, bar_height))
            y_pos += 30

        if self.zaman_yavaslama:
            kalan_saniye = (self.zaman_yavaslama_sure // 60) + 1
            power_yazi = self.font.render(f'Yavaşlama: {kalan_saniye}s', True, self.PEMBE)
            self.ekran.blit(power_yazi, (10, y_pos))

            # Süre çubuğu
            bar_width = 100
            bar_height = 8
            doluluk = self.zaman_yavaslama_sure / 600.0  # Maksimum süre 600
            pygame.draw.rect(self.ekran, self.GRI, (150, y_pos + 8, bar_width, bar_height))
            pygame.draw.rect(self.ekran, self.PEMBE, (150, y_pos + 8, bar_width * doluluk, bar_height))

        # Level tamamlandı mesajı
        if self.level_tamamlandi:
            overlay = pygame.Surface((self.GENISLIK, self.YUKSEKLIK))
            overlay.set_alpha(128)
            overlay.fill(self.SIYAH)
            self.ekran.blit(overlay, (0, 0))

            if self.mevcut_level < self.max_level:
                tamamlandi_yazi = pygame.font.SysFont('Arial', 36).render(f'LEVEL {self.mevcut_level} TAMAMLANDI!',
                                                                          True, self.SARI)
                tamamlandi_rect = tamamlandi_yazi.get_rect(center=(self.GENISLIK // 2, self.YUKSEKLIK // 2))
                self.ekran.blit(tamamlandi_yazi, tamamlandi_rect)
            else:
                kazanma_yazi = pygame.font.SysFont('Arial', 48).render('TEBRİKLER! OYUNU KAZANDIN!', True, self.SARI)
                kazanma_rect = kazanma_yazi.get_rect(center=(self.GENISLIK // 2, self.YUKSEKLIK // 2))
                self.ekran.blit(kazanma_yazi, kazanma_rect)

        if self.oyun_bitti:
            oyun_bitti_yazi = self.font.render('Oyun Bitti! R tuşuna basarak yeniden başla', True, self.BEYAZ)
            self.ekran.blit(oyun_bitti_yazi, (self.GENISLIK // 2 - 200, self.YUKSEKLIK // 2))

        # Level geçiş kontrolü
        if self.level_tamamlandi:
            self.level_gecis_suresi -= 1
            if self.level_gecis_suresi <= 0:
                if self.mevcut_level < self.max_level:
                    self.mevcut_level += 1
                    self.yeni_level_baslat()
                else:
                    self.oyun_bitti = True

        pygame.display.flip()

    def calistir(self):
        while True:
            self.clock.tick(self.FPS)
            self.olaylari_isle()

            # Ekranı temizle
            self.ekran.fill(self.SIYAH)  # Veya gradient_ciz() kullanın

            # Durum kontrolü
            if self.oyun_durumu == 'ana_menu':
                self.menu_ciz()
            elif self.oyun_durumu == 'nasil_oynanir':
                self.nasil_oynanir_ciz()
            elif self.oyun_durumu == 'ayarlar':
                self.ayarlar_ciz()
            elif self.oyun_durumu == 'oyun':
                self.oyun_mantigi()  # Tüm oyun güncellemeleri için ayrı fonksiyon
                self.ciz()
            elif self.oyun_durumu == 'game_over':
                self.game_over_ciz()

            pygame.display.flip()

    def oyun_mantigi(self):
        """Oyun güncelleme mantığını gruplandırır"""
        self.cekme_hesapla()
        self.topu_guncelle()
        self.parcaciklari_guncelle()
        self.power_up_guncelle()
        self.ozel_hedefleri_guncelle()
        self.hareketli_engelleri_guncelle()

if __name__ == "__main__":
    oyun = SuperZiplayanTopOyunu()
    oyun.calistir()
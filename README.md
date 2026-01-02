# Güvenli Collatz Şifreleme (SCC) Algoritması

Bu proje, modifiye edilmiş bir **Collatz Sanısı** (3n+1 problemi) tabanlı, kriptografik olarak güvenli bir sözde rastgele sayı üreteci (CSPRNG) uygular. Kriptografik uygulamalar veya temiz rastgele dizi üretimi için uygun, istatistiksel olarak yüksek kaliteli ve dengeli bit dizileri (eşit sayıda 0 ve 1) üretmek üzere tasarlanmıştır.

## Özellikler

1.  **Gerçek Rastgelelik**: Başlatma ve yeniden tohumlama (re-seeding) için Python'un `secrets` modülünü kullanır.
2.  **İstatistiksel Kalite**: Reddetme Örneklemesi (Rejection Sampling) yöntemi kullanarak tam olarak %50 0 ve %50 1 (0/1 eşitliği) oranını garanti eder.
3.  **Kriptografik Güvenlik**:
    *   **Afin Dönüşüm**: $An + B$ (Burada A ve B, Ana Anahtardan türetilen büyük tek sayılardır).
    *   **Doğrusal Olmayanlık (Non-Linearity)**: Mevcut durumdan ($n$) ve Ana Anahtardan HMAC-SHA256 ile türetilen dinamik bir $K$ anahtarı ile XOR maskelemesi.
    *   **Ana Anahtar (Master Key)**: 256-bit entropi.

---

## 1. Algoritma Mantığı ve Açıklaması

Algoritma, modifiye edilmiş bir Collatz fonksiyonu kullanarak dahili bir tamsayı durumunu (state) evriltir. Standart Collatz ($3n+1$) tamamen deterministik ve doğrusaldır. Bunu güvenli hale getirmek için:
1.  Sabit çarpanları (3, 1), Ana Anahtardan türetilen gizli büyük $A$ ve $B$ tamsayıları ile değiştiriyoruz.
2.  Sonucu, yine Ana Anahtar ve mevcut durumdan ($n$) türetilen dinamik bir $k$ değeri ile XOR işlemine tabi tutarak doğrusallığı bozuyoruz.
3.  Durumun paritesine (tek/çift) göre bit çıktısı veriyoruz (Çift $\rightarrow$ 0, Tek $\rightarrow$ 1).
4.  **0/1 Eşitliğini** sağlamak için 0 ve 1 sayılarını sayıyoruz. Eğer algoritma, hedef sayısına ($Uzunluk/2$) ulaşmış bir bit üretirse, bu biti atıyor ve uygun bir bit bulunana kadar durumu (state) ilerletmeye devam ediyoruz.

### Modifiye Collatz Adım Fonksiyonu
$$
f(n) = 
\begin{cases} 
n / 2 & \text{eğer } n \equiv 0 \pmod 2 \\
((A \cdot n + B) \oplus K(n)) & \text{eğer } n \equiv 1 \pmod 2 
\end{cases}
$$

---

## 2. Sözde Kod (Pseudocode)

```text
ALGORİTMA GuvenliCollatzUretici:
    GİRDİ: uzunluk (çift sayı olmalı), AnaAnahtar
    ÇIKTI: DengeliBitDizisi

    BAŞLAT durum = Rastgele(256 bit)
    TÜRET A, B <- AnaAnahtar kullanılarak
    AYARLA hedef_sifirlar = uzunluk / 2
    AYARLA hedef_birler = uzunluk / 2
    AYARLA sifirlar = 0, birler = 0
    AYARLA cikti = ""

    DÖNGÜ uzunluk(cikti) < uzunluk OLDUĞU SÜRECE:
        EĞER durum % 2 == 0 İSE:
            aday_bit = '0'  # Çift Sayı -> 0
        DEĞİLSE:
            aday_bit = '1'  # Tek Sayı -> 1

        # Denge Kontrolü
        EĞER aday_bit == '0' İSE:
            EĞER sifirlar < hedef_sifirlar İSE:
                EKLE '0' -> cikti
                sifirlar = sifirlar + 1
            DEĞİLSE:
                ADIM_AT(durum)
                DEVAM_ET
        DEĞİLSE (aday_bit == '1'):
            EĞER birler < hedef_birler İSE:
                EKLE '1' -> cikti
                birler = birler + 1
            DEĞİLSE:
                ADIM_AT(durum)
                DEVAM_ET

        ADIM_AT(durum)

    DÖNDÜR cikti

FONKSİYON ADIM_AT(durum):
    EĞER durum ÇİFT İSE:
        durum = durum / 2
    DEĞİLSE:
        k = HMAC_SHA256(AnaAnahtar, durum)
        durum = ((A * durum + B) XOR k)
    
    EĞER durum <= 1 İSE:
        durum = Rastgele(256 bit) # Çökme Önleyici (Anti-collapse)
```

---

## 3. Akış Şeması

```mermaid
graph TD
    A[Başlat] --> B[Durumu ve Anahtarları Hazırla]
    B --> C{Uzunluğa Ulaşıldı Mı?}
    C -- Evet --> Z[Bit Dizisini Döndür]
    C -- Hayır --> D[Durum Paritesini Kontrol Et]
    
    D -- Çift --> E[Aday Bit = 0]
    D -- Tek --> F[Aday Bit = 1]
    
    E --> G{Sıfır Sayısı < Hedef?}
    F --> H{Bir Sayısı < Hedef?}
    
    G -- Evet --> I['0' Ekle, Sıfırları Artır]
    G -- Hayır --> J[Biti Atla/Yoksay]
    
    H -- Evet --> K['1' Ekle, Birleri Artır]
    H -- Hayır --> J
    
    I --> L[Durumu Güncelle (Adım At)]
    K --> L
    J --> L
    
    L --> C
    
    subgraph "Güvenli Adım (Secure Step)"
    L1{Durum Çift Mi?}
    L1 -- Evet --> L2[Durum = Durum / 2]
    L1 -- Hayır --> L3[Dinamik K Hesapla]
    L3 --> L4[Durum = (A*Durum + B) XOR K]
    end
```

---

## 4. İstatistiksel Test Sonuçları

Algoritma, rastgeleliği ve kaliteyi doğrulamak için yerleşik istatistiksel testler içerir.
Canlı sonuçları görmek için `collatz_crypto.py` dosyasını çalıştırın.

### Uygulanan Testler
1.  **0/1 Denge Kontrolü (Balance Check)**: 0 ve 1 sayılarının tam olarak eşit olduğunu doğrular.
2.  **Ki-Kare Testi (Chi-Square $\chi^2$)**:
    *   **Frekans Testi**: Sembol dağılımının düzgün (uniform) olup olmadığını kontrol eder. Mükemmel dengeli diziler için ideal değer 0.0'dır.
    *   **Blok Testi (2-bit)**: 00, 01, 10, 11 bloklarının dağılımını kontrol eder.
3.  **Runs Testi (Wald-Wolfowitz / Mislin)**:
    *   0 ve 1'lerin *sıralamasının* rastgele olup olmadığını, ardışık serileri (runs) sayarak kontrol eder.
    *   Bir Z-Skoru hesaplar. $|Z| < 1.96$ olması, %95 güven aralığında rastgeleliği gösterir.

### Örnek Çıktı
```text
Kontrol Edilen Bit Dizisi Uzunluğu: 128
----------------------------------------
[1] 0/1 Denge Kontrolü: 0s=64, 1s=64 -> BAŞARILI (PASS)
[2] Ki-Kare (Frekans): 0.0000 (İdeal: 0.0)
    Ki-Kare (2-bit): 2.1500 (< 7.81 Başarılı)
[3] Runs Testi: Seriler=68, Beklenen=65.00
    Z-Skoru: 0.5280
    Sonuç: BAŞARILI (Rastgele Seriler / Random Runs)
```

## Kullanım

Demoyu ve test sonuçlarını görmek için python betiğini doğrudan çalıştırın:

```bash
python collatz_crypto.py
```

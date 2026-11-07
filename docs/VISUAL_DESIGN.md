# VISUAL_DESIGN.md — Görsel Dil ve Görselleştirme Kataloğu

> Hedef: açıldığında etkileyici ama her pikseli bilgi taşıyan bir bilimsel arayüz.
> Doğruluk estetikten önce gelir: yanıltıcı bir görsel, güzel olsa bile başarısızdır.

## 1. Bilimsel görselleştirme kuralları
1. **Her görsel bir soruyu yanıtlar;** başlığı o sorudur.
2. **Eksenler her zaman etiketli;** log ölçekler açıkça belirtilir.
3. **Kesikli olan kesikli gösterilir.** n bir tam sayı dizisidir (2, 4, 8, …). Farklı n'ler arasına **yüzey örülmez**; her n ayrı bir şerit/eğridir.
   (n'ler arası ara değerleme, var olmayan çözümler gösterir.)
4. **FEM ile analitik ayırt edilebilir:** renk + çizgi stili (FEM: düğümlü kesikli; analitik: düz). Renk tek bilgi kanalı değildir.
5. **3D yalnızca üçüncü eksen gerçek bir değişkense** (n, baz indisi). Süs için 3D yok. Her 3D görselin tek tıkla 2D görünümü vardır.
6. **Analitik çözüm yoksa** kıyas ve hata görselleri gösterilmez; yerlerine açıklama mesajı çıkar.

## 2. Tasarım belirteçleri (`web/src/styles/tokens.css`)
- Koyu tema varsayılan (3D şeritler koyu zeminde daha okunur); açık tema da desteklenir (PDF görselleri açık temayla üretilir).
- Koyu: zemin `#0B0F17`, yüzey `#121826`, çizgi `#243044`, metin `#E6EAF2`. Açık: zemin `#FAFAF7`, yüzey `#FFFFFF`, çizgi `#E3E1DA`, metin `#1B1F27`.
- Anlamsal renkler (Okabe–Ito, renk körü güvenli): FEM `#56B4E9`, analitik `#E69F00`, hata `#D55E00`, baz `#009E73`, vurgu `#CC79A7`.
- n dizisi için sıralı palet: **viridis** (küçük n koyu mor → büyük n sarı). |hata| için **inferno** (log ölçek). Gökkuşağı (jet) yasak.
- Yazı: arayüz için sistem sans-serif; belge gövdesi serif (ör. Source Serif 4, self-host); sayılar `tabular-nums`.
- Boşluk ölçeği 4 px; köşe yarıçapı 10 px; gölgeler çok hafif.
- Hareket: geçişler 200–400 ms; `prefers-reduced-motion` desteklenir.

## 3. Görselleştirme kataloğu

| ID | Ad | Tür | İçerik | Yanıtladığı soru |
|---|---|---|---|---|
| **V1** | Yakınsama şeritleri | 3D | Her n için `u_h(x)` bir şerit: x ekseni, n ekseni (log₂ ölçekli, kesikli konumlar), u ekseni. En arkada analitik çözüm parlak turuncu referans şeridi. Düğüm değerleri nokta (n ≤ 32). | n arttıkça çözüm analitiğe nasıl yaklaşıyor? |
| **V2** | Hata şeritleri | 3D | Her n için `log₁₀|u − u_h|(x)` şeridi, inferno renk. Düğümlerde hata çukurları görünür (süperyakınsama). | Hata nerede yoğun, n ile nasıl sönüyor? |
| **V3** | Baz inşası | 3D | x ekseni, baz indisi i ekseni, `Uᵢ φᵢ(x)` şeritleri; ön düzlemde toplam `u_h`. Kaydırıcı: kaç baz toplansın. | Çözüm baz fonksiyonlarından nasıl kuruluyor? |
| **V4** | Karşılaştırma | 2D | Seçili n için u_h ve u; alt panelde işaretli hata. n seçici. | Tek bir ağda ne kadar iyi? |
| **V5** | Yakınsama grafiği | 2D | log-log: h'ye karşı L², H¹, max düğüm hatası; teorik eğim üçgenleri; ölçülen oranlar etiketli. | Yöntem teorik mertebede mi yakınsıyor? |
| **V6** | Matris yapısı | 2D | Seçili n için K'nın ısı haritası (dofs ≤ 33), ıraksak renk, sıfırlar boş; P1 üçlü-köşegen, P2 blok yapısı. | Matris neden seyrek ve bantlı? |

### 3.1 Plotly 3D ayarları (başlangıç; M6.1 incelemesiyle kalibre edilir)
- Şeritler: her n için ince bir `surface` (x × [n − δ, n + δ]) veya kalın `scatter3d` çizgisi; şerit genişliği sabit, n konumu log₂ n.
- `lighting`: ambient 0.4, diffuse 0.8, specular 0.2, roughness 0.6, fresnel 0.2.
- Eksen arka planı şeffaf; ızgara `#243044`; eksen başlıkları Unicode (`uₕ(x)`, `log₂ n`) çünkü Plotly 3D LaTeX desteklemez.
- n ekseni etiketleri gerçek değerler: 2, 4, 8, … (konum log₂ n).
- Kamera ön ayarları: `iso`, `önden` (x–u: tüm n'ler üst üste), `yandan` (n–u). Tuşlar 1–3.
- Hover: x, n, u_h, u, hata (4 anlamlı basamak).
- PNG dışa aktarım: 1600×1000, ölçek 2, açık tema.

## 4. Sekmeler
1. **3D Laboratuvar:** üstte büyük V1; altında V2 ve V3 yan yana; kamera ön ayarları.
2. **Yakınsama:** V5 + hata/oran tablosu (kopyalanabilir) + V4.
3. **Matris:** V6 + Thomas adımları tablosu (P1).
4. **Çözüm Belgesi:** uzun okuma; solda içindekiler; not kutuları kenarda; "LaTeX'i kopyala" ve ".tex indir".

## 5. Erişilebilirlik (asgari)
Metin kontrastı ≥ 4.5:1; tüm denetimler klavyeyle kullanılabilir; her grafiğin altında "veri tablosu olarak göster".

## 6. Kabul kriterleri (M6 kapısı)
Her görsel için: saf `buildTraces` fonksiyonu + vitest; B2, B5 ve M4 için ekran görüntüsü; konsolda hata yok; analitik yokken doğru mesaj.

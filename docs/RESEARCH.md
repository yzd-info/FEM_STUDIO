# RESEARCH.md — Referans Repo İncelemesi (M6.1, en fazla 2 saat)

> Amaç: Görselleştirme ve bilimsel anlatımda dünya standardı açık kaynak projelerin **kaynak kodunu okuyup**
> somut teknikleri (parametre değerleri, düzen kuralları, zamanlama eğrileri) çıkarmak ve bizim görsellerimize uygulamak.
> Bu inceleme ürün kodu üretmez; çıktısı tek bir not dosyasıdır: `docs/RESEARCH_NOTES.md`.

## 1. İncelenecek repolar
| # | Repo | Ne arıyoruz | Hedef bileşen |
|---|---|---|---|
| R1 | `plotly/plotly.js` | 3D `surface`/`scatter3d` ışıklandırma parametreleri, kamera, eksen stili; şerit çiziminin en temiz yolu | V1–V3 |
| R2 | `3b1b/manim` | Renk paleti seçimleri; "bir şeyin adım adım inşa edilmesi" kurgusu; zamanlama/easing fonksiyonları | V3 kaydırıcısı, geçişler |
| R3 | `distillpub/template` | Uzun bilimsel metin + kenar notu + şekil düzeni; tipografi ölçüleri | Çözüm Belgesi sekmesi |

Not: scikit-fem (kâhin) M2.7'de bağımlılık olarak kullanılır; kodunun incelenmesi gerekmez.

## 2. Yöntem
1. `git clone --depth 1 https://github.com/<repo> research/<ad>` (`research/` git'e girmez).
2. İlgili dizinleri oku; her bulguyu `dosya yolu` ile kaydet.
3. Bulguyu bizim bir bileşenimize eşle: "V1'de şunu şu değerle yapacağız".
4. Repo erişilemezse (silinmiş/taşınmış) kullanıcıya bildir; yerine öneri sun, kendi başına değiştirme.

## 3. `RESEARCH_NOTES.md` biçimi
```markdown
# Referans İnceleme Notları
| Repo | Commit | Lisans |
## R1 plotly.js
| Bulgu | Kaynak dosya | Bizde nerede | Uygulanacak değer/kural |
## R2 manim
...
## R3 distill template
...
## Kararlar
(VISUAL_DESIGN.md §3.1'de değişecek parametreler — kullanıcıya gösterilir)
```

## 4. Lisans kuralları
| Lisans | Kod uyarlama |
|---|---|
| MIT, BSD, Apache-2.0 | Serbest; telif ve lisans `THIRD_PARTY_NOTICES.md`'ye; commit'te `Third-party:` satırı |
| GPL / AGPL / lisanssız / ticari olmayan | Kod kopyalanmaz; yalnızca fikir/desen alınır ve kendi kodumuz yazılır |

Lisans her repo için klonlandıktan sonra `LICENSE` dosyasından okunur ve notlara yazılır (ezberden yazılmaz).

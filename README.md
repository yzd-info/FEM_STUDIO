# FEM1D Studio

1D lineer ikinci mertebe sınır değer problemlerini P1/P2 sonlu elemanlarla tarayıcıda çözen, n'e göre yakınsamayı 3D gösteren,
analitik çözümle kıyaslayan ve tüm çözümü adım adım LaTeX ders notu olarak üreten bilimsel bir araç.

$$-\bigl(p(x)\,u'\bigr)' + q(x)\,u' + r(x)\,u = f(x),\qquad x\in(a,b)$$

## Durum
Planlama tamamlandı. Uygulama `pipeline.md` ile 7 günde, 8 modülde (M0–M7) yapılır. Güncel durum: `docs/PROGRESS.md`.

## Başlatma (VS Code + Claude Code)
1. Bu klasörü VS Code'da aç.
2. Terminalde Claude Code'u başlat.
3. Şu mesajı gönder:

```
CLAUDE.md, pipeline.md ve docs/LEARNING.md dosyalarını oku.
Sonra bana docs/LEARNING.md §2'deki FEM yol haritasını kısaca anlat ve M0.1'den başla.
Her modül sonunda bilimsel özeti yaz ve onayımı bekle.
```

## Belgeler
| Dosya | İçerik |
|---|---|
| `CLAUDE.md` | Claude Code çalışma ve bilimsel doğruluk kuralları |
| `pipeline.md` | 7 günlük adım adım plan + gelecek modüller |
| `docs/LEARNING.md` | Öğretim kuralları, FEM yol haritası, özet şablonu, terim sözlüğü, kaynaklar |
| `docs/MATH_SPEC.md` | Tüm formüller (tek doğruluk kaynağı) |
| `docs/BENCHMARKS.md` | 14 referans problem, beklenen hata değerleri ve oranlar |
| `docs/ARCHITECTURE.md` | Modüller ve veri sözleşmesi |
| `docs/LATEX_STYLE.md` | Ders notu standardı (13 adım) |
| `docs/VISUAL_DESIGN.md` | Görsel dil, 6 görsel |
| `docs/TESTING.md` · `docs/GIT_WORKFLOW.md` · `docs/RESEARCH.md` · `docs/DECISIONS.md` | Test, git, referans inceleme, kararlar |

## Gereksinimler (M0.1'de kontrol edilir)
git, GitHub CLI (`gh`, oturum açık), `uv`, Node.js LTS, Python (Pyodide sürümüyle eşleşen), isteğe bağlı TeX Live.
Windows'ta ayrıca `make` gerekir (`winget install ezwinports.make`); Claude Code M0.1'de kontrol edip sorar.

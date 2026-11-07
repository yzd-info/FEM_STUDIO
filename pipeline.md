# pipeline.md — FEM1D Studio Uygulama Planı (7 gün)

> Claude Code'un izleyeceği tek yürütme planı. Sıra bağlayıcıdır.
> Her adımın kimliği (`M2.3`), çıktısı, testi ve commit mesajı vardır. Kurallar: `CLAUDE.md`.

## İçindekiler
1. Hedef · 2. Dondurulmuş kapsam · 3. Teknoloji · 4. Mimari · 5. Depo yapısı · 6. Adım Protokolü ·
7. Modül kapıları · 8. Modüller (M0–M7) · 9. Kalite eşikleri · 10. Riskler ve B planı · 11. **Gelecek modüller (evrim yol haritası)** · 12. Ekler

---

## 1. Hedef
Kullanıcı tarayıcıda bir denklem ve sınır koşulları girer. Sistem:
1. Problemi kanonik forma çevirir ve kapsam içinde olup olmadığını denetler.
2. Seçilen eleman (P1 lineer / P2 kuadratik) ve her `n` için FEM çözümünü hesaplar.
3. Analitik çözümü SymPy ile bulur (veya MMS ile üretir) ve yerine koyarak doğrular.
4. Hata normlarını ve yakınsama oranlarını hesaplar; teorik oranla kıyaslar.
5. Sonuçları 3D ve 2D gösterir.
6. Tüm çözümü **elle yazılmış bir ders notu gibi** adım adım LaTeX belgesi olarak üretir (ekranda KaTeX, indirilebilir `.tex`).

**Başarı ölçütü:** Hocaya gösterildiğinde (a) her sayı doğru ve kanıtlı, (b) yakınsama oranları teoriyle uyumlu,
(c) belge bir FEM dersindeki el çözümüyle birebir aynı mantıkla ilerliyor, (d) görseller bir bakışta "n arttıkça ne oluyor" sorusunu yanıtlıyor.

---

## 2. Dondurulmuş kapsam

### İçeride
| Konu | Ayrıntı |
|---|---|
| Denklem | `−(p(x) u′)′ + q(x) u′ + r(x) u = f(x)`, `x ∈ [a, b]`, `p(x) > 0` |
| Girdi modları | (1) Serbest denklem metni, ör. `-u'' = 1`, `-((1+x)*u')' = 1`; (2) MMS: tam çözüm `u` verilir (ör. `x^4`), `f` ve BC üretilir |
| Sınır koşulları | Her uçta `α u′ + β u = γ` → Dirichlet / Neumann / Robin |
| Elemanlar | P1 (lineer), P2 (kuadratik); düzgün ağ |
| n dizisi | Kullanıcı seçer; varsayılan 2, 4, 8, 16, 32, 64 |
| Analitik çözüm | SymPy `dsolve` + yerine koyarak doğrulama; MMS; kullanıcı tanımlı tam çözüm (doğrulanarak) |
| Hata | L², H¹ yarı-normu, maksimum düğüm hatası; ardışık yakınsama oranları |
| Tanılama | Kapsam kapısı (reddetme + neden), Péclet uyarısı, makine hassasiyeti bayrağı, kareleme bildirimi |
| Görseller | V1–V3 (3D), V4–V6 (2D); bkz. `docs/VISUAL_DESIGN.md` |
| Belge | 13 adımlık Türkçe türetme; ekranda KaTeX; `.tex` indirme; CI'da `pdflatex` ile derlenir |

### Dışarıda (bu 7 günde yapılmaz → §11'de gelecek modül olarak planlı)
Zamana bağlı problemler, özdeğer problemleri, lineer olmayan denklemler, 4. mertebe (kiriş), P3+ elemanlar, düzgün olmayan/adaptif ağ,
SUPG, başlangıç değer problemleri, İngilizce arayüz, çoklu tarayıcı testi, görsel regresyon testi, GitHub Pages yayını.

> Bu sınırlar keyfi değil. Her dış konu farklı bir matematiksel formülasyon gerektirir ve aceleyle eklenirse doğruluk riski doğar.
> Mimari, her birinin sonradan aynı çekirdek üzerine eklenebileceği şekilde kuruludur (§11).

---

## 3. Teknoloji (sabit — gerekçeler `docs/DECISIONS.md`)
| Katman | Seçim |
|---|---|
| Hesap çekirdeği | Python paketi `fem1d` (NumPy + SymPy) |
| Tarayıcıda çalıştırma | Pyodide, Web Worker içinde |
| Ön yüz | Vite + TypeScript (framework yok) |
| Grafik | Plotly.js (3D + 2D) |
| Matematik gösterimi | KaTeX |
| Test | pytest, hypothesis, scikit-fem (bağımsız kâhin, yalnızca geliştirmede); vitest; Playwright (yalnızca Chromium) |
| Kalite | ruff (lint + format), mypy, `tsc --strict` |
| CI | GitHub Actions: `python`, `web`, `latex` işleri |
| Paket yönetimi | `uv` (Python), `npm` |

**Sürüm kuralı:** Bağımlılıklar kilitlenir (`uv.lock`, `package-lock.json`). Yerel Python minör sürümü, seçilen Pyodide sürümünün içerdiği Python ile aynı olmalıdır (M0.1).

---

## 4. Mimari (özet — ayrıntı `docs/ARCHITECTURE.md`)
```
Tarayıcı (statik HTML)
├─ UI (TypeScript): giriş paneli · görseller (Plotly) · belge (KaTeX) · .tex indirme
└─ Web Worker: Pyodide → fem1d.solve(request) → SolveResult (JSON)
```
**Temel ilke:** Tüm matematik Python'da, tüm sunum TypeScript'te. TS hiçbir FEM hesabı yapmaz.
Türetme belgesi de hesap yapmaz, yalnızca hesaplanmış sonuçları biçimlendirir. Böylece belge, grafik ve testler aynı sayıları kullanır.

---

## 5. Depo yapısı (hedef)
```
fem1d-studio/
├── CLAUDE.md  pipeline.md  README.md  Makefile  THIRD_PARTY_NOTICES.md
├── .github/workflows/ci.yml
├── docs/  (bu belgeler) + learning/M0.md … M7.md (modül özetleri) + VALIDATION.md (M7)
├── shared/latex_macros.json
├── core/
│   ├── pyproject.toml
│   ├── src/fem1d/
│   │   ├── api.py            # solve(request) -> result (tek giriş noktası)
│   │   ├── parsing.py        # metin → SymPy → kanonik (p, q, r, f) + kapsam kapısı
│   │   ├── bc.py             # sınır koşulu metni → (α, β, γ)
│   │   ├── quadrature.py  mesh.py  elements.py
│   │   ├── element_matrices.py   # sayısal + tam sembolik yol
│   │   ├── assembly.py  boundary.py  solver.py
│   │   ├── analytic.py       # dsolve, doğrulama, MMS
│   │   ├── errors.py  convergence.py  sampling.py
│   │   ├── derivation/       # model.py, format.py, steps.py, latex_document.py
│   │   └── schema.py         # sonuç şeması doğrulaması
│   └── tests/ unit/ integration/ oracle/ fixtures/ snapshots/
├── web/
│   ├── index.html  package.json  vite.config.ts  tsconfig.json
│   ├── public/               # derlenmiş fem1d wheel (git'e girmez)
│   ├── src/ main.ts  worker/  ui/  viz/  doc/  styles/  types.ts
│   └── tests/ unit/  e2e/  fixtures/
└── scripts/ build_wheel.sh  export_fixtures.py
```

---

## 6. Adım Protokolü (HER ADIMDA ZORUNLU)
```
1. HAZIRLIK    PROGRESS.md'de adımı 🔄 yap. İlgili docs/ bölümünü oku.
2. TEST ÖNCE   Başarısız testi yaz, kırmızı olduğunu GÖR (core'da zorunlu; web'de saf fonksiyonlar için zorunlu).
3. UYGULA      En küçük yeterli değişiklik.
4. KONTROL     make check → yeşil. İlgiliyse make e2e / make tex.
5. GÖZDEN GEÇİR git diff: kapsam dışı değişiklik, hata ayıklama artığı, sabitlenmiş sayı var mı?
6. KAYDET      PROGRESS.md: adım ✅ + 1 satır not (aynı commit'e dahil).
7. COMMIT      Conventional Commits; gövdede `Step: M2.3` ve `Tests: ...` (docs/GIT_WORKFLOW.md).
8. PUSH        git push
9. CI DOĞRULA  gh run watch --exit-status → yeşil. Kırmızıysa: düzelt → yeni commit → push (amend/force yok).
10. RAPOR      Kullanıcıya 1–2 satır: ne yapıldı, hangi test kanıtlıyor, sıradaki adım.
```
**Adım ölçüsü:** Bir adım = bir mantıksal değişiklik = bir commit. 300 satırı aşan üretim kodu → alt adımlara böl (`M2.3a`, `M2.3b`) ve PROGRESS'e yaz.

---

## 7. Modül kapıları (🚦)
Her modülün sonunda:
1. `make check` ve CI yeşil.
2. `docs/learning/Mx.md` → **Modül Sonu Bilimsel Özet** (`docs/LEARNING.md` §3 şablonu). Özetteki her sayı o an çalıştırılan komutun çıktısıdır.
3. Commit + push + CI (`docs(learning): add module Mx summary`).
4. Kullanıcıya özeti sohbette de sun: kısa versiyon + dosya yolu + 3 kontrol sorusu.
5. Git etiketi: `mx-done` (ör. `m2-done`).
6. **DUR.** Kullanıcı "devam" demeden sonraki modüle başlama. Kullanıcı soru sorarsa önce yanıtla.

İlk kapı (G0) ayrıca M0.2'den sonradır: GitHub repo adı ve görünürlüğü için onay.

---

## 8. Modüller

| Gün | Modül | Öğrenilen FEM kavramı |
|---|---|---|
| 1 | M0 Kurulum · M1 Referans eleman | Kareleme, ağ, şekil fonksiyonları |
| 2 | M2 Ayrıklaştırma ve çözüm | Eleman matrisleri, montaj, sınır koşulları, lineer sistem |
| 3 | M3 Problem girişi ve analitik çözüm | Kanonik form, eliptiklik, ODE'nin kapalı çözümü, MMS |
| 4 | M4 Hata ve yakınsama · M5 başlangıcı | Normlar, a priori kestirim, yakınsama oranı |
| 5 | M5 Türetme belgesi | Çözümün baştan sona matematiksel anlatımı |
| 6 | M6 Web arayüzü ve görseller | Sonuçların görsel yorumu |
| 7 | M7 Doğrulama raporu ve sunum | Doğrulama (verification) ve bilimsel raporlama |

---

### M0 — Kurulum ve iskelet (Gün 1, sabah)
**Ders konusu (modül başında 5–10 cümle):** Projenin büyük resmi; FEM'in 8 aşaması (`docs/LEARNING.md` §2) ve hangi modülün hangisine karşılık geldiği.

- **M0.1 — Ön kontroller.** `git --version`, `gh auth status`, `uv --version`, `node --version`, `python --version`.
  Güncel kararlı Pyodide sürümünü ve içerdiği Python sürümünü belirle (Pyodide belgelerinden/sürüm notlarından), PROGRESS "Ortam" tablosuna yaz.
  Gerekirse `uv python install <sürüm>`. Eksik araç varsa **kurmadan önce sor.**
  **Windows:** `make --version` kontrol et. Yoksa kullanıcıya sor: `winget install ezwinports.make` önerilir. Shell komutları Git Bash ile çalıştırılır;
  yardımcı scriptler `.sh` değil Python (`scripts/*.py`) yazılır ki Windows'ta da çalışsın. · Commit yok.
- **M0.2 — Depo başlatma.** `git init -b main`, `.gitignore` (Python, Node, `web/public/*.whl`, `research/`, `*.pdf`, `.venv`), README taslağı (başlatma komutları).
  · `chore: initialize repository with planning docs`
- **🚦 G0 — Kullanıcıya sor:** repo adı (öneri: `fem1d-studio`), public/private.
- **M0.3 — GitHub.** `gh repo create <ad> --<görünürlük> --source . --remote origin --push`. · Commit yok.
- **M0.4 — Python iskeleti.** `core/pyproject.toml` (src layout), ruff, mypy, pytest, hypothesis; `fem1d/__init__.py` (`__version__`); duman testi.
  · Test: `test_version` · `build(core): scaffold fem1d package`
- **M0.5 — Web iskeleti.** Vite + TS strict, vitest, Playwright (Chromium); boş sayfa; duman testleri.
  · `build(web): scaffold vite typescript app`
- **M0.6 — Makefile + CI.** §12.1 hedefleri; `.github/workflows/ci.yml` (`python`, `web` işleri; `latex` işi M5.9'da eklenir). Push, CI yeşil.
  · `ci: add python and web jobs`
- **🚦 M0 kapısı** → `docs/learning/M0.md`

---

### M1 — Referans eleman (Gün 1, öğleden sonra)
**Ders konusu:** Neden her elemanı [−1, 1] referans aralığına taşırız; Gauss kareleme neden yeter; şapka fonksiyonu.
Referans: `docs/MATH_SPEC.md` §4.

- **M1.1 — Gauss–Legendre kareleme.** m noktalı kural, [−1,1] → [x₀,x₁] dönüşümü.
  · Test: m noktalı kural 2m−1 dereceye kadar polinomları tam integre eder (hypothesis, rastgele polinom); 2m dereceli tek terimde tam olmaz.
  · `feat(core): add Gauss-Legendre quadrature`
- **M1.2 — Ağ.** Düzgün ağ; P1 (n+1 düğüm) ve P2 (2n+1 düğüm, orta düğümler) bağlantı tablosu.
  · Test: düğüm sayıları, uç noktalar, eleman → global indis eşlemesi (P2: eleman k → [2k, 2k+1, 2k+2]).
  · `feat(core): add uniform 1D mesh with P1 and P2 connectivity`
- **M1.3 — Şekil fonksiyonları.** P1 ve P2, türevleriyle; sayısal (NumPy) ve sembolik (SymPy).
  · Test: Σ Nᵢ = 1, Σ Nᵢ′ = 0, Nᵢ(ξⱼ) = δᵢⱼ, sembolik ↔ sayısal eşitlik.
  · `feat(core): add P1 and P2 reference shape functions`
- **🚦 M1 kapısı** → `docs/learning/M1.md` (elle alıştırma: P2 şekil fonksiyonlarının düğümlerdeki değerlerini tablola).

---

### M2 — Ayrıklaştırma ve çözüm (Gün 2)
**Ders konusu:** Zayıf form → Galerkin → `KU = F`; eleman matrisinin anlamı; montaj; Dirichlet'in eliminasyonu, Neumann/Robin'in "doğal" oluşu.
Referans: `docs/MATH_SPEC.md` §2, §3, §5.

- **M2.1 — Elle hesaplanmış fikstürler.** `BENCHMARKS.md` §4'teki B1 (n=2, n=4) ve B3 (n=2) sistemleri `core/tests/fixtures/*.json`'a, kesir olarak.
  · `test(fixtures): add hand-computed reference systems`
- **M2.2 — Eleman matrisleri (sayısal yol).** K, C, M, F; değişken katsayılar karelemeyle (`MATH_SPEC` §5.2 nokta sayısı kuralı).
  · Test: sabit katsayıda `MATH_SPEC` §5.1 tablosu (P1 ve P2); satır toplamı ve toplam integral özellikleri.
  · `feat(core): compute element matrices by quadrature`
- **M2.3 — Eleman matrisleri (tam sembolik yol).** Katsayılar ve f için SymPy `integrate` kapalı form verirse kesirli/tam sonuç.
  · Test: sembolik ↔ sayısal (göreli 1e-12); B3 için `K^(1)_{11} = 5/2` gibi kesirler.
  · `feat(core): compute exact symbolic element matrices`
- **M2.4 — Global montaj + montaj kaydı.** Her (eleman, yerel i, yerel j) → (global I, J, değer) kaydı tutulur (belge M5'te kullanır).
  · Test: B1 n=2,4 fikstürleriyle **kesir düzeyinde** eşitlik; q = 0 iken simetri.
  · `feat(core): assemble global system with assembly log`
- **M2.5 — Sınır koşulları.** Dirichlet → eliminasyon (lifting); Neumann/Robin → `MATH_SPEC` §2.2–2.3 işaretleriyle. İki uç saf Neumann ve r ≡ 0 → açıklamalı hata.
  · Test: B6, B7, B10 (sol Robin); indirgenmiş matrisin simetrik pozitif tanımlı olması (q = 0, r ≥ 0).
  · `feat(core): apply Dirichlet, Neumann and Robin conditions`
- **M2.6 — Çözücü.** `numpy.linalg.solve` + P1 için Thomas algoritması (ara değerler kaydedilir, belge gösterir).
  · Test: iki çözücü aynı sonuç (1e-12); B1 düğüm değerleri tam.
  · `feat(core): add linear solvers including Thomas algorithm`
- **M2.7 — Bağımsız kâhin.** scikit-fem (yalnızca dev bağımlılığı) ile B1–B10'u çöz, düğüm değerlerini karşılaştır.
  · Test: göreli fark < 1e-10. · `test(oracle): cross-check nodal values against scikit-fem`
- **M2.8 — Yama testi ve süperyakınsama.** (a) Tam çözüm P_k içindeyse FEM tam; (b) sabit p, q = r = 0 iken eleman uç düğümleri tam (P1 ve P2).
  · Test: B1, B6, B7, M2, M3, M4 (`BENCHMARKS.md` §3). · `test(core): add patch and nodal superconvergence tests`
- **🚦 M2 kapısı** → `docs/learning/M2.md` (elle alıştırma: B1 n=2'yi baştan sona elle çöz, U₁ = 1/8 bul).

---

### M3 — Problem girişi ve analitik çözüm (Gün 3)
**Ders konusu:** Her lineer 2. mertebe ODE neden `−(pu′)′ + qu′ + ru = f` yazılabilir; eliptiklik (p > 0) neden şart;
sabit katsayılı ODE'nin karakteristik denklemle çözümü; MMS'nin bir doğrulama tekniği olarak mantığı. Referans: `MATH_SPEC` §1, §9.

- **M3.1 — Ayrıştırıcı.** `u''`, `u'`, `u`, `diff(u,x,k)`, `(expr*u')'` → SymPy. Beyaz liste fonksiyonlar; kısıtlı ad alanı (`eval` yok).
  · Test: ≥ 30 geçerli/geçersiz girdi; Türkçe hata mesajları. · `feat(parser): parse ODE text into sympy expressions`
- **M3.2 — Kanonikleştirme.** `a₂u″ + a₁u′ + a₀u = g` → (p, q, r, f) (`MATH_SPEC` §1.1); dönüşüm adımları kaydedilir (belge adım 1).
  · Test: hypothesis ile rastgele polinom katsayılar → kanonik → geri açılım = orijinal; `BENCHMARKS.md` §2 tablosu.
  · `feat(parser): convert to canonical divergence form`
- **M3.3 — Kapsam kapısı.** Lineerlik, mertebe = 2, `p(x)` sıfır olmuyor ve işaret değiştirmiyor (SymPy kök arama + 200 nokta örnekleme), BVP olması (her uçta bir koşul).
  Reddetme mesajı **neden** ve **ne yapılabilir** içerir. Uyarılar: `PECLET`, `NON_COERCIVE` (r < 0).
  · Test: `BENCHMARKS.md` §5 reddedilecek girdiler tablosu. · `feat(parser): add scope gate with explanatory rejections`
- **M3.4 — Sınır koşulu ayrıştırıcı.** `u(0)=0`, `u'(1)=2`, `u'(1)+3*u(1)=1`, `-u'(0)+2*u(0)=1` → (α, β, γ); uç noktası alan sınırıyla eşleşmeli.
  · `feat(parser): parse boundary condition expressions`
- **M3.5 — Analitik çözüm.** `dsolve` + BC ile sabitler; sabit katsayıda karakteristik kökler, homojen ve özel çözüm ayrıca kaydedilir (belge adım 11). Zaman aşımı 10 s.
  · Test: B1–B10 tam çözümleri bulunur (bulunamayan varsa test bunu açıkça bekler ve PROGRESS'e not düşülür).
  · `feat(analytic): solve boundary value problems symbolically`
- **M3.6 — Doğrulama.** Çözüm denkleme ve BC'lere yerine konur, `simplify == 0`; olmazsa 50 noktada sayısal kontrol (< 1e-10). Doğrulanmayan çözüm **kullanılmaz**.
  · `feat(analytic): verify solutions by substitution`
- **M3.7 — MMS ve kullanıcı tanımlı tam çözüm.** MMS: verilen u ve (p, q, r) → f ve BC değerleri. Kullanıcı tam çözümü de M3.6 ile doğrulanır.
  · Test: M2, M3, M4, S1. · `feat(analytic): support manufactured and user-provided exact solutions`
- **🚦 M3 kapısı** → `docs/learning/M3.md` (elle alıştırma: `u'' − u = −x` için karakteristik denklemi çöz, B4'ün tam çözümünü elde et).

---

### M4 — Hata, yakınsama ve API (Gün 4, sabah)
**Ders konusu:** L² ve H¹ normları ne ölçer; a priori kestirim `‖e‖ ≤ C hᵏ⁺¹`; log-log grafikte eğim neden oranı verir; düzgünlük varsayımı. Referans: `MATH_SPEC` §6–§7.

- **M4.1 — Hata normları.** Eleman başına 10 noktalı Gauss; L², H¹ yarı-norm, maksimum düğüm hatası, göreli hatalar.
  · Test: bilinen fark fonksiyonları için analitik değerler; `BENCHMARKS.md` §3 referans tablosu (göreli %1).
  · `feat(analysis): compute L2, H1 and nodal errors`
- **M4.2 — Yakınsama.** Ardışık oranlar; "asimptotik bölgede" bayrağı; hata < 1e-12 ise `MACHINE_PRECISION` (oran hesaplanmaz).
  · Test: `BENCHMARKS.md` §3 oran aralıkları (B2, B3, B4, B10, M3, M4, S1). · `feat(analysis): estimate convergence rates`
- **M4.3 — Örnekleme.** Görseller için ortak x ızgarası; P2'de eleman içi eğrilik; baz fonksiyonu değerleri.
  · `feat(core): sample fields for visualization`
- **M4.4 — `api.solve()` ve şema.** Tek giriş noktası; çıktı JSON şemasıyla doğrulanır (`ARCHITECTURE.md` §3). `scripts/export_fixtures.py` → `web/tests/fixtures/`.
  · Test: her benchmark sonucu şemaya uyar. · `feat(api): expose solve() returning schema-valid result`
- **🚦 M4 kapısı** → `docs/learning/M4.md` (elle alıştırma: B2 tablosundaki iki hatadan oranı hesapla).

---

### M5 — Türetme belgesi (Gün 4 öğleden sonra – Gün 5)
**Önce `docs/LATEX_STYLE.md`'yi baştan sona oku.**
**Ders konusu:** Bir FEM çözümü nasıl yazılır; her adımın gerekçesi.

- **M5.1 — Belge modeli ve ortak makrolar.** `shared/latex_macros.json` (`LATEX_STYLE.md` §5); `Step`, `Paragraph`, `Equation`, `Table`, `MatrixBlock`, `Note`, `Result` veri sınıfları + JSON.
  · `feat(derivation): add document model`
- **M5.2 — Biçimlendirme.** Kesir/ondalık seçimi, anlamlı basamak, matris kısaltma, işaret temizliği (`+ -` asla).
  · Test: ≥ 25 vaka. · `feat(derivation): add numeric and matrix formatting`
- **M5.3 — Adım 1–2:** problem ve kanonik form; zayıf form. · `feat(derivation): generate problem and weak form steps`
- **M5.4 — Adım 3–4:** ağ; baz fonksiyonları. · `feat(derivation): generate mesh and basis steps`
- **M5.5 — Adım 5–7:** Galerkin sistemi; eleman matrisleri (genel + sayısal). · `feat(derivation): generate element matrix steps`
- **M5.6 — Adım 8–9:** montaj; sınır koşulları. · `feat(derivation): generate assembly and boundary steps`
- **M5.7 — Adım 10–11:** sistemin çözümü (Thomas tablosu); analitik çözüm. · `feat(derivation): generate solution steps`
- **M5.8 — Adım 12–13:** karşılaştırma ve hata; yakınsama ve sonuç. · `feat(derivation): generate error and convergence steps`
  · Her adım için test: (1) B1 ve B4 için snapshot, (2) belgedeki her sayı `SolveResult` ile aynı, (3) yasak ifadeler yok (`LATEX_STYLE` §7).
- **M5.9 — `.tex` belgesi + çift motor kontrolü.** Bağımsız `.tex` (önsöz + ortak makrolar); `export_fixtures.py` B1 (n=2), B4 (n=4), M4 (P2, n=2) `.tex`'lerini üretir;
  CI `latex` işi `latexmk -pdf` ile derler, PDF'leri artefakt yapar; vitest tüm denklemleri KaTeX `throwOnError: true` ile render eder.
  · `feat(latex): assemble standalone document and verify in KaTeX and pdflatex`
- **🚦 M5 kapısı** → `docs/learning/M5.md` + üç PDF'i kullanıcıya göster. Kullanıcı "ders notu gibi" hissini onaylamalı.

---

### M6 — Web arayüzü ve görseller (Gün 6)
- **M6.1 — Kısa referans incelemesi (en fazla 2 saat).** `docs/RESEARCH.md`'deki 3 repo; çıktı tek dosya `docs/RESEARCH_NOTES.md`. Ürün kodu yok.
  · `docs(research): add reference notes for plotting and layout`
- **M6.2 — Pyodide köprüsü.** `make wheel`; worker Pyodide + numpy + sympy + fem1d yükler; ilerleme olayları; `solve` RPC'si; 30 s zaman aşımı → worker yeniden başlar.
  **Zaman kutusu 3 saat.** Aşılırsa DUR ve §10 B planını kullanıcıya öner.
  · Test: e2e — sayfa açılır, B1 çözülür, düğüm değerleri fikstürle eşleşir. · `feat(web): run fem1d in a Pyodide web worker`
- **M6.3 — Giriş paneli.** Denklem metni + canlı KaTeX önizleme (kanonik form), BC alanları, P1/P2, n seçimi, MMS modu, hazır problemler (B1–B10, M2–M4, S1), reddetme/uyarı mesajları.
  · `feat(web): add input panel with live preview and presets`
- **M6.4 — 3D görseller V1–V3** (`VISUAL_DESIGN.md` §3). Her biri saf `buildTraces(result)` + vitest. · `feat(viz): add 3D convergence, error and basis views`
- **M6.5 — 2D görseller V4–V6.** · `feat(viz): add comparison, convergence and matrix views`
- **M6.6 — Belge sekmesi.** Türetme modeli → KaTeX; içindekiler; "LaTeX'i kopyala"; `.tex` indir. · `feat(doc): render derivation and export tex`
- **🚦 M6 kapısı** → `docs/learning/M6.md` + ekran görüntüleri (B2, B5, M4).

---

### M7 — Doğrulama raporu ve sunum (Gün 7)
- **M7.1 — Doğrulama raporu.** `scripts/validation_report.py` → `docs/VALIDATION.md`: tüm benchmark'lar için ölçülen oranlar ve teorik oranlar, kâhin farkları, düğüm tamlığı testleri. **Tamamen otomatik üretilir.**
  · `docs: generate validation report`
- **M7.2 — Uçtan uca senaryolar.** Playwright: §12.3'teki 5 sunum senaryosu baştan sona. · `test(e2e): add demo scenarios`
- **M7.3 — README ve sunum rehberi.** Kurulum, çalıştırma, `docs/DEMO.md` (hocaya 10 dakikalık sunum akışı, olası sorular ve yanıtları).
  · `docs: add README and demo guide`
- **M7.4 — Son kontrol.** Temiz klonda `make setup && make check && make e2e`; etiket `v1.0.0`.
- **🚦 M7 kapısı** → `docs/learning/M7.md`: projenin tamamının bilimsel özeti (1 sayfa) + "hocanın sorabileceği 10 soru ve yanıtları".

---

## 9. Kalite eşikleri
| Ölçüt | Eşik |
|---|---|
| Core satır kapsaması | ≥ 90 % |
| mypy, tsc | sıfır hata |
| ruff | sıfır uyarı |
| Kâhin farkı (scikit-fem, düğüm değerleri) | < 1e-10 göreli |
| Referans hata tablosu (`BENCHMARKS.md` §3) | göreli fark < %1 |
| Yakınsama oranları | `BENCHMARKS.md` §3 aralıkları |
| KaTeX render hatası | 0 |
| pdflatex | 0 hata |
| Tarayıcıda n = 2…64 taraması (dsolve hariç) | < 2 s |

---

## 10. Riskler ve B planı
| Risk | Azaltma |
|---|---|
| Pyodide entegrasyonu uzar | M6.2'de 3 saatlik zaman kutusu. **B planı (kullanıcı onayıyla):** `python -m fem1d.report` komutu aynı `SolveResult`'u ve aynı TS görsellerini içeren tek bir statik HTML + `.tex` üretir. Matematik ve testler hiç değişmez; yalnızca etkileşimli giriş kaybolur. |
| `dsolve` takılır/bulamaz | 10 s zaman aşımı; "analitik çözüm bulunamadı" mesajı; MMS önerisi. Kıyas yapılmaz. |
| KaTeX ↔ pdflatex uyumsuzluğu | Ortak makro seti + iki motorda CI testi. |
| Konveksiyon baskın problemde salınım | Bu yöntemin gerçek davranışıdır. `PECLET` uyarısı + belgede açıklama notu (B5). |
| Kapsam kayması | §2 dondurulmuş; yeni istek → §11'e eklenir. |

---

## 11. Gelecek modüller (evrim yol haritası)
v1.0 tamamlandıktan sonra sistem aşağıdaki modüllerle 1D FEM'in tamamını kapsayacak şekilde büyür.
Her modül aynı çekirdeği (kareleme, ağ, elemanlar, montaj, sınır koşulları, hata, türetme motoru, görseller) yeniden kullanır
ve **aynı pipeline disipliniyle** (test önce, adım protokolü, modül sonu bilimsel özet) eklenir.

| Sıra | Modül | Matematik | Yeniden kullanılan | Yeni | Tahmini süre |
|---|---|---|---|---|---|
| E1 | Yüksek dereceli elemanlar (P3, P4) | Lagrange P_k, p-yakınsama `O(h^{k+1})` | Tüm çekirdek | `elements.py` genelleme | 0.5 gün |
| E2 | Düzgün olmayan ağ | Derecelendirilmiş ağ ile tekil çözümde optimal oranın geri kazanılması (S1) | Tümü | `mesh.py` | 0.5 gün |
| E3 | Özdeğer problemleri | `K φ = λ M φ` (titreşen tel, Sturm–Liouville) | K, M montajı | genelleştirilmiş özdeğer çözücü, mod görselleri | 1 gün |
| E4 | Zamana bağlı problemler | `M U̇ + K U = F`, θ-yöntemi (Euler, Crank–Nicolson); ısı ve dalga denklemi | Montaj, BC | zaman ilerletme, `u(x, t)` 3D yüzeyi (gerçek 3D) | 1.5 gün |
| E5 | Konveksiyon baskın problemler | SUPG / yukarı akış (upwind) stabilizasyonu; Galerkin ile kıyas | Tümü | stabilizasyon terimi | 1 gün |
| E6 | Lineer olmayan problemler | Newton–Raphson, Jacobian montajı; iterasyon görselleştirmesi | Montaj, BC | Newton döngüsü, yakınsama izleme | 1.5 gün |
| E7 | 4. mertebe problemler | Euler–Bernoulli kirişi, Hermite (C¹) elemanlar | Kareleme, montaj | Hermite şekil fonksiyonları, 4 BC tipi | 1.5 gün |
| E8 | A posteriori hata ve adaptif ağ | Artık tabanlı kestirici, işaretle-incelt | Tümü + E2 | kestirici, adaptif döngü, ağ evrimi animasyonu | 2 gün |
| E9 | İngilizce arayüz ve belge | i18n sözlüğü | Belge modeli | metin kataloğu | 0.5 gün |

**Kural:** Bir E-modülüne başlamadan önce kullanıcı onayıyla `pipeline.md`'ye o modülün adımları (M-modülleriyle aynı biçimde) eklenir
ve `MATH_SPEC.md`'ye matematiği yazılır. Spesifikasyonu yazılmamış bir modül kodlanmaz.

---

## 12. Ekler

### 12.1 Makefile hedefleri
```makefile
setup:   ## uv sync (core) + npm ci (web) + playwright install chromium
lint:    ## ruff check + ruff format --check
type:    ## mypy core/src + tsc --noEmit
test:    ## pytest (core, slow hariç) + vitest
check: lint type test   ## commit öncesi zorunlu
e2e:     ## wheel + playwright test
tex:     ## export_fixtures --tex + latexmk (TeX yoksa atla ve bildir)
wheel:   ## core wheel → web/public
dev:     ## wheel + vite
```

### 12.2 Commit biçimi
```
feat(core): add P1 and P2 reference shape functions

Implements Lagrange shape functions and derivatives on [-1, 1],
numerically (numpy) and symbolically (sympy).

Step: M1.3
Tests: test_partition_of_unity, test_kronecker_delta, test_symbolic_matches_numeric
```

### 12.3 Sunum senaryoları (M7.2'de e2e olarak test edilir)
1. **B1, P1, n = 2 → 64:** Elle çözülebilen problem; belge U₁ = 1/8'i gösterir; düğümler tam.
2. **M4 (`u = x⁴`, MMS), P1 ve P2:** Oranlar 2 ve 3; P2'nin üstünlüğü; düğüm tamlığı.
3. **M2 (`u = x²`), P2:** Makine hassasiyeti bayrağı: "tam çözüm eleman uzayında".
4. **B5 (konveksiyon baskın), n = 8 ve 64:** Pe = 1.25'te salınım, Pe < 1'de düzelme; uyarının anlamı.
5. **S1 (`u = x^0.75`):** P1 ve P2 aynı düşük oranı verir (L² 1.25, H¹ 0.25); düzgünlük varsayımı.

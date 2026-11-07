# LATEX_STYLE.md — "Elle Yazılmış Ders Notu" Standardı

> Hedef: iyi bir hocanın tahtada çözdüğü, öğrencinin temize çektiği bir çözüm.
> Her adım **neden** yapıldığını söyler, **ne** yapıldığını gösterir, **sonucu** kutular. Her sayı gerçek hesaplamadan gelir.

## 1. Üslup
- Birinci çoğul şahıs, anlatım dili: "Denklemi bir test fonksiyonu $v$ ile çarpıp aralık boyunca integre edelim."
- Her adım 1–2 cümlelik **amaç**la başlar: "Bu adımda türevlerden birini test fonksiyonuna aktararak $u$'dan istenen düzgünlüğü azaltacağız."
- Her dönüşümün yanında gerekçe: `\quad\text{(kısmi integrasyon)}`, `\quad\text{(}v(0)=0\text{ olduğundan)}`.
- Ara adım atlanmaz. Uzun aritmetik tablo halinde verilir.
- Adım başına en fazla bir `\boxed{}` (o adımın sonucu).
- Sezgi ve uyarılar **not kutusunda**: "Not", "Dikkat", "Neden?". Ekranda kenar kutusu, PDF'de `tcolorbox`.
- Yasak ifadeler (testle taranır): "açıktır", "kolayca görülür", "aşikârdır", "trivial", "bariz".

## 2. Gösterim
| Nesne | Yazım |
|---|---|
| Türev | `u'`, `u''` |
| İntegral | `\int_{a}^{b} \cdots \dd x` (`\dd` = `\,\mathrm{d}`) |
| Vektör/matris | `\vect{U}`, `\vect{K}`, `\vect{F}`; eleman: `\Kel{e}`, `\Fel{e}` |
| Şekil / baz fonksiyonu | `N_i(\xi)` / `\varphi_i(x)` |
| Normlar | `\LtwoNorm{e}`, `\HoneSemi{e}` |
| Sayılar | Tam kesir varsa kesir (`\tfrac{1}{8}`); yoksa 6 anlamlı basamak; küçükler `1.23\times10^{-4}` |
| Ondalık ayırıcı | Nokta (belge başında bir kez not edilir) |
| İşaret temizliği | `+ -3` → `- 3`; `1x` → `x`; `0\cdot(\ldots)` terimleri yazılmaz; `-(-a)` → `+a` |

## 3. Belgenin 13 adımı
| # | Başlık | İçerik |
|---|---|---|
| 1 | Problemin tanımı | Kullanıcı girdisi → kanonik form (gerekirse −1 ile çarpma, çarpım kuralı); p, q, r, f tablosu; BC tipleri ve (α, β, γ). Kanonik form kutulu. |
| 2 | Zayıf form | `v` ile çarp, integre et, kısmi integrasyon **açık açık**; her uç için sınır teriminin ne olduğu (Dirichlet: v = 0; Neumann/Robin: yerine koy). `B(u,v) = ℓ(v)` kutulu. |
| 3 | Ağ | Düğüm tablosu (i, xᵢ), h; ağ şekli. |
| 4 | Baz fonksiyonları | Referans eleman, Nᵢ(ξ), x(ξ), Jacobian, türev dönüşümü; şapka (P1) / parabol (P2) şekli. |
| 5 | Galerkin sistemi | `u_h = Σ Uⱼ φⱼ` → `Σⱼ B(φⱼ, φᵢ) Uⱼ = ℓ(φᵢ)` → `K U = F` kutulu. "Neden çoğu girdi sıfır?" notu. |
| 6 | Eleman matrisleri (genel) | `K^(e)_ij` integralinin referans elemana taşınması; sembolik sonuç. |
| 7 | Eleman matrisleri (sayısal) | Her eleman için gerçek değerler. n ≤ 4: her eleman ayrı; büyükse ilk eleman + tablo. Kareleme kullanıldıysa nokta sayısı belirtilir. |
| 8 | Montaj | Bağlantı tablosu; katkıların gösterimi, ör. `K_{11} = K^{(1)}_{22} + K^{(2)}_{11}`; global matris. |
| 9 | Sınır koşulları | Dirichlet eliminasyonu (satır/sütun çıkarma, sağ tarafa taşıma); Neumann/Robin katkıları; indirgenmiş sistem kutulu. |
| 10 | Sistemin çözümü | P1 ve dofs ≤ 9: Thomas algoritması tablosu (c′ᵢ, d′ᵢ, geri yerine koyma). Aksi halde sonuç vektörü + koşul sayısı. `U` kutulu. |
| 11 | Analitik çözüm | Sabit katsayı: karakteristik denklem, homojen + özel çözüm, sabitlerin BC'den bulunması. Değişken katsayı: SymPy sonucu + yerine koyarak doğrulama satırı. MMS: "çözüm seçildi, f türetildi" açıklaması. Analitik yoksa bu adım "bulunamadı" der ve 12–13 kıyas içermez. |
| 12 | Karşılaştırma ve hata | Düğüm tablosu: xᵢ, Uᵢ, u(xᵢ), |eᵢ|; normlar; düğüm tamlığı varsa açıklama notu (`MATH_SPEC` §6.2). |
| 13 | Yakınsama ve sonuç | Tüm n için hata ve oran tablosu; teorik oranla kıyas; `MACHINE_PRECISION`, `PECLET`, tekil çözüm vb. uyarıların yorumu; 3–5 cümlelik sonuç paragrafı. |

Model: `Step = { id, title, intro, blocks: [Paragraph | Equation | Table | MatrixBlock | Note | Result] }`.
`Equation` → `{ latex, label?, justification? }`; çok satırlı türetmeler `aligned` ile.

## 4. Matris gösterimi
- Boyut ≤ 9: tam `pmatrix`; sıfırlar `\color{gray}{0}`.
- Boyut > 9: ilk 3 satır/sütun, `\cdots`, `\vdots`, `\ddots`, son satır/sütun + "tam matris Matris sekmesinde".
- Montajda katkılar eleman rengine göre (`\elA`, `\elB`, `\elC` makroları; renk körü güvenli: Okabe–Ito mavi, turuncu, yeşil). Renk tek bilgi kanalı değildir; üst simge `^{(e)}` de yazılır.

## 5. Ortak makrolar (`shared/latex_macros.json`)
Tek kaynak; KaTeX'e `macros` seçeneği olarak, `.tex`'e `fem1dmacros.sty` olarak üretilir. Yalnızca KaTeX'in desteklediği komutlar.
```json
{
  "\\dd": "\\,\\mathrm{d}",
  "\\vect": "\\mathbf{#1}",
  "\\Kel": "\\mathbf{K}^{(#1)}",
  "\\Fel": "\\mathbf{F}^{(#1)}",
  "\\LtwoNorm": "\\left\\|#1\\right\\|_{L^2(a,b)}",
  "\\HoneSemi": "\\left|#1\\right|_{H^1(a,b)}",
  "\\elA": "\\color{#0072B2}",
  "\\elB": "\\color{#E69F00}",
  "\\elC": "\\color{#009E73}"
}
```
Yasak: belge içinde `\newcommand`/`\def`; `align` (yerine `equation` + `aligned`); KaTeX'in desteklemediği paketler. M5.9 testi yakalar.

## 6. PDF (pdflatex)
- `article`, A4, 11pt; `geometry` (2.5 cm), `amsmath, amssymb, mathtools, booktabs, xcolor, tcolorbox, hyperref, babel[turkish], microtype`, `fem1dmacros`.
- Latin Modern yazı tipi (ders notu görünümü).
- Üstte başlık bloğu: problem, tarih, "FEM1D Studio vX ile üretildi".
- Denklemler bölüm bazlı numaralı `(2.3)`, `\eqref` ile atıf.
- `\usepackage[turkish]{babel}` ile `=` ve `:` karakterlerinin aktif karakter sorunu M5.9'da test edilir (gerekirse `\shorthandoff{=}`).
- Derleme: `latexmk -pdf -interaction=nonstopmode -halt-on-error`.

## 7. Kabul kriterleri (M5 kapısı)
1. B1 (P1, n = 2), B4 (P1, n = 4), M4 (P2, n = 2) belgeleri hatasız derlenir.
2. Belgedeki her sayı `SolveResult` ile aynıdır (test).
3. Yasak ifade yoktur (test).
4. B1 belgesi `U₁ = 1/8` sonucunu kesir olarak, eleman matrislerinden başlayarak elle takip edilebilir biçimde gösterir.
5. Kullanıcı belgeyi okuyup "ders notu gibi" olduğunu onaylar.

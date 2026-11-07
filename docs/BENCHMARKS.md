# BENCHMARKS.md — Referans Problemler ve Beklenen Sonuçlar

> Testlerin, hazır problemlerin ve sunum senaryolarının kaynağı.
> Tüm tam çözümler denkleme ve sınır koşullarına yerine konarak doğrulanmıştır.
> §3'teki tüm sayılar bu belge hazırlanırken **bağımsız bir referans FEM koduyla** (12 noktalı Gauss) hesaplanmıştır.
> Proje kodu bu sayıları yeniden üretmelidir (göreli fark < %1); üretemiyorsa önce kod, sonra bu belge sorgulanır (kullanıcıya sorulur).

Gösterim: kanonik form `−(pu′)′ + qu′ + ru = f`, BC `αu′ + βu = γ`, tüm alanlar `[0, 1]`.

## 1. Problemler

| ID | Ad | p | q | r | f | Sol BC | Sağ BC | Tam çözüm | Ne öğretir / test eder |
|---|---|---|---|---|---|---|---|---|---|
| B1 | Gerilmiş tel | 1 | 0 | 0 | 1 | u=0 | u=0 | x(1−x)/2 | El hesabı; P1 düğümde tam, P2 her yerde tam |
| B2 | Sinüs | 1 | 0 | 0 | π² sin πx | u=0 | u=0 | sin πx | **Ana yakınsama örneği** |
| B3 | Değişken iletkenlik | 1+x | 0 | 0 | 1 | u=0 | u=0 | ln(1+x)/ln 2 − x | Değişken p; tam sembolik integral; düğüm tamlığı yok |
| B4 | Difüzyon–reaksiyon | 1 | 0 | 1 | x | u=0 | u=0 | x − sinh x / sinh 1 | **Belge vitrin örneği**; M matrisi; karakteristik denklem |
| B5 | Konveksiyon baskın | 0.05 | 1 | 0 | 0 | u=0 | u=1 | (e^{x/ε}−1)/(e^{1/ε}−1), ε=0.05 | Sınır tabakası; Péclet; salınım |
| B6 | Neumann | 1 | 0 | 0 | 2 | u=0 | u′=0 | 2x − x² | Doğal BC |
| B7 | Robin | 1 | 0 | 0 | 1 | u=0 | u′+u=1 | −x²/2 + 5x/4 | Robin'in K ve F'ye katkısı |
| B8 | Helmholtz | 1 | 0 | −100 | 0 | u=0 | u=1 | sin 10x / sin 10 | r<0; asimptotik öncesi bölge |
| B9 | Üstel katsayı | eˣ | 0 | 0 | eˣ(1+2x) | u=0 | u=0 | x(1−x) | Polinom olmayan katsayı → sayısal kareleme |
| B10 | Tam karışık | 1 | 1 | 2 | 2eˣ | −u′+2u=1 | u=e | eˣ | Sol Robin işareti; q ve r birlikte; sıfırdan farklı Dirichlet |
| M2 | MMS x² | 1 | 0 | 0 | −2 | u=0 | u=1 | x² | P2'de tam temsil |
| M3 | MMS x³ | 1 | 0 | 0 | −6x | u=0 | u=1 | x³ | P2'de oran 3, düğümde tam |
| M4 | MMS x⁴ | 1 | 0 | 0 | −12x² | u=0 | u=1 | x⁴ | P1/P2 oran kıyası |
| S1 | Tekil çözüm | 1 | 0 | 0 | (3/16) x^{−5/4} | u=0 | u=1 | x^{3/4} | **Düzgünlük varsayımı**; P2 kazandırmaz |

(S1 için f = −u″ = −(3/4)(−1/4) x^{−5/4} = (3/16) x^{−5/4}. f, x = 0'da sonsuzdur ama yük integrali sonludur.)

## 2. Serbest metin girdileri (ayrıştırıcı testleri)
| ID | Kullanıcının yazacağı | Beklenen (p, q, r, f) |
|---|---|---|
| B1 | `-u'' = 1` | (1, 0, 0, 1) |
| B3 | `-((1+x)*u')' = 1` | (1+x, 0, 0, 1) |
| B3′ | `-(1+x)*u'' - u' = 1` | (1+x, 0, 0, 1) — açılmış hali, aynı problem |
| B4 | `u'' - u = -x` | (1, 0, 1, x) — −1 ile çarpma adımı gösterilir |
| B5 | `-0.05*u'' + u' = 0` | (0.05, 1, 0, 0) |
| B8 | `u'' + 100*u = 0` | (1, 0, −100, 0) |
| B9 | `-diff(exp(x)*diff(u,x),x) = exp(x)*(1+2*x)` | (eˣ, 0, 0, eˣ(1+2x)) |
| B10 | `-u'' + u' + 2*u = 2*exp(x)` | (1, 1, 2, 2eˣ) |
| M4 | `y'' = 12*x^2` | (1, 0, 0, −12x²) — `y` → `u`, −1 ile çarpma |

## 3. Beklenen sayısal sonuçlar

### 3.1 Referans hata değerleri (bağımsız koddan; test toleransı göreli %1)
| ID | P1 n=8 L² | P1 n=8 H¹ | P1 n=64 L² | P1 n=64 H¹ | P2 n=8 L² | P2 n=8 H¹ | P2 n=64 L² | P2 n=64 H¹ |
|---|---|---|---|---|---|---|---|---|
| B2 | 9.921e-03 | 2.512e-01 | 1.555e-04 | 3.148e-02 | 2.457e-04 | 1.274e-02 | 4.809e-07 | 1.995e-04 |
| B3 | 1.175e-03 | 2.805e-02 | 1.843e-05 | 3.514e-03 | 1.418e-05 | 7.346e-04 | 2.786e-08 | 1.155e-05 |
| B4 | 7.363e-04 | 1.954e-02 | 1.153e-05 | 2.448e-03 | 1.133e-05 | 5.874e-04 | 2.214e-08 | 9.183e-06 |
| B10 | 1.885e-03 | 6.447e-02 | 2.945e-05 | 8.062e-03 | 2.004e-05 | 1.040e-03 | 3.921e-08 | 1.626e-05 |
| M3 | 4.932e-03 | 1.248e-01 | 7.720e-05 | 1.562e-02 | 6.739e-05 | 3.494e-03 | 1.316e-07 | 5.459e-05 |
| M4 | 7.616e-03 | 1.928e-01 | 1.196e-04 | 2.420e-02 | 1.553e-04 | 8.054e-03 | 3.040e-07 | 1.261e-04 |
| B1 | 1.426e-03 | 3.608e-02 | 2.229e-05 | 4.511e-03 | < 1e-12 | < 1e-12 | < 1e-12 | < 1e-12 |
| B7 | 1.426e-03 | 3.608e-02 | 2.229e-05 | 4.511e-03 | < 1e-12 | < 1e-12 | < 1e-12 | < 1e-12 |

### 3.2 Yakınsama oranı aralıkları (n = 8…64 ardışık oranlar, aksi belirtilmedikçe)
| ID | P1 L² | P1 H¹ | P2 L² | P2 H¹ | Not |
|---|---|---|---|---|---|
| B2, B3, B4, B10, M3, M4 | [1.95, 2.05] | [0.95, 1.05] | [2.9, 3.1] | [1.9, 2.1] | Teorik oranlar |
| B5 | n=32…256: [1.95, 2.05] | [0.95, 1.05] | n=32…256: [2.9, 3.1] | [1.9, 2.1] | Küçük n'de asimptotik değil |
| B8 | n=64…256: [1.95, 2.05] | [0.95, 1.1] | n=32…256: [2.95, 3.15] | [1.9, 2.1] | P1 n=8→16 oranı ≈ 6 (asimptotik öncesi) |
| B9 | [1.95, 2.05] | [0.95, 1.05] | MACHINE_PRECISION | — | u ∈ P2 |
| S1 | n=16…256: [1.15, 1.35] | [0.2, 0.3] | n=16…128: [1.1, 1.35] | [0.2, 0.3] | **P2 oran kazandırmaz** |
| B1, B6, B7, M2 | [1.95, 2.05] | [0.95, 1.05] | MACHINE_PRECISION | — | Tam temsil |

### 3.3 Düğüm tamlığı (eleman uç düğümleri, eşik 1e-12)
| Tam olmalı | Tam olmamalı |
|---|---|
| B1, B2, B6, B7, M2, M3, M4 (P1 ve P2) | B3 (değişken p), B4 (r ≠ 0), B9, B10 |
| S1 **yalnızca** yük vektörü tam sembolik hesaplanırsa | S1 sayısal karelemeyle (kareleme hatası; `MATH_SPEC` §5.2) |

### 3.4 B5 salınımı (P1)
| n | Pe | min U | Monoton mu |
|---|---|---|---|
| 8 | 1.25 | ≈ −0.111 | Hayır (salınım) |
| 16 | 0.625 | 0 | Evet |
| 64 | 0.156 | 0 | Evet |

## 4. Elle hesaplanmış fikstürler (M2.1)

### B1, P1, n = 2 (h = 1/2)
`K^e = 2·[[1, −1], [−1, 1]]`, `F^e = [1/4, 1/4]`.
```
K = [[ 2, -2,  0],      F = [1/4, 1/2, 1/4]
     [-2,  4, -2],
     [ 0, -2,  2]]
```
Dirichlet eliminasyonu sonrası: `4 U₁ = 1/2` → **`U₁ = 1/8`** = u(1/2) ✓.

### B1, P1, n = 4 (h = 1/4)
İndirgenmiş: `4·tridiag(−1, 2, −1) U = (1/4)·[1, 1, 1]` → **`U = [3/32, 1/8, 3/32]`** ✓.

### B3, P1, n = 2 (tam sembolik)
`K^(1)_{22} = ∫₀^{1/2} (1+x)·4 dx = 5/2`, `K^(2)_{11} = ∫_{1/2}^{1} (1+x)·4 dx = 7/2`.
İndirgenmiş: `(5/2 + 7/2) U₁ = 1/2` → **`U₁ = 1/12`**. Tam: u(1/2) = ln(3/2)/ln 2 − 1/2 ≈ 0.08496. Fark ≈ 1.6e-3 (beklenen; §3.3).

Fikstür biçimi (kesirler metin olarak, `fractions.Fraction` ile karşılaştırılır):
```json
{ "id": "B1_P1_n2", "element": "P1", "n": 2,
  "K": [["2","-2","0"],["-2","4","-2"],["0","-2","2"]],
  "F": ["1/4","1/2","1/4"],
  "U": ["0","1/8","0"] }
```

## 5. Reddedilecek girdiler (M3.3)
| Girdi | Beklenen hata kodu |
|---|---|
| `-u'' + u^2 = 1` | `NONLINEAR` |
| `-u'' + sin(u) = 0` | `NONLINEAR` |
| `u*u' = 1` | `NONLINEAR` |
| `u' = x^2` | `ORDER` (mertebe 1) |
| `u'''' = 1` | `ORDER` (mertebe 4) |
| `-(x*u')' = 1` alan [0, 1] | `NOT_ELLIPTIC` (p(0) = 0) |
| `-((x-0.5)*u')' = 1` | `NOT_ELLIPTIC` (işaret değiştirir) |
| `-u'' = 1`, BC `u(0)=0, u'(0)=1` | `NOT_BVP` |
| `-u'' = 1`, BC `u'(0)=0, u'(1)=0` | `SINGULAR` |
| `-u'' = k` (k tanımsız) | `UNKNOWN_SYMBOL` |

# MATH_SPEC.md — Matematiksel Spesifikasyon

> Core'daki her formülün tek doğruluk kaynağı. Kod bu belgeyle çelişirse **kod yanlıştır**.
> Bu belgedeki eleman matrisleri tam kesirli hesapla, sınır koşulu işaretleri ve beklenen oranlar bağımsız bir FEM koduyla doğrulanmıştır
> (`BENCHMARKS.md` §3). Değişiklik yalnızca kullanıcı onayıyla.

## 1. Kanonik problem
$$
-\bigl(p(x)\,u'(x)\bigr)' + q(x)\,u'(x) + r(x)\,u(x) = f(x), \qquad x\in(a,b)
$$
| Katsayı | Fiziksel anlam (örnek: çubukta ısı) | Şart |
|---|---|---|
| p | difüzyon / iletkenlik / eksenel rijitlik EA | `p(x) > 0` tüm `[a,b]`'de (**eliptiklik**) |
| q | konveksiyon (akışla taşınım) | — |
| r | reaksiyon / yaylı zemin / ısı kaybı | `r − q′/2 ≥ 0` koersifliği garanti eder; değilse `NON_COERCIVE` uyarısı |
| f | kaynak / yayılı yük | — |

### 1.1 Genel girdiden kanonik forma
Girdi `a₂(x)u″ + a₁(x)u′ + a₀(x)u = g(x)` biçimine indirgenir. `−(pu′)′ + qu′ + ru = −p u″ + (q − p′) u′ + r u` olduğundan:

| Kanonik | Değer |
|---|---|
| p | −a₂ |
| q | a₁ − a₂′ |
| r | a₀ |
| f | g |

`a₂ > 0` ise denklem önce −1 ile çarpılır (`p > 0` olsun diye). Bu dönüşüm belge adım 1'de açıkça gösterilir.
Örnek: `u″ − u = −x` → −1 ile çarp → `−u″ + u = x` → (p, q, r, f) = (1, 0, 1, x).

### 1.2 Kapsam kapısı (M3.3) — reddetme koşulları
| Koşul | Neden | Mesajda önerilen |
|---|---|---|
| `u`'da lineer olmayan terim (`u²`, `sin u`, `u u′`) | Galerkin sistemi lineer olmaz | "Lineer olmayan problemler gelecek modül E6" |
| Mertebe ≠ 2 | Farklı eleman/BC yapısı | 1. mertebe: başlangıç değer problemi; 4. mertebe: E7 |
| `p(x)` aralıkta sıfır olur veya işaret değiştirir | Eliptiklik bozulur; standart hata kestirimleri geçersiz | Aralığı daraltmak |
| Bir uçta iki koşul, diğerinde hiç (`u(0)`, `u′(0)`) | Başlangıç değer problemi, sınır değer problemi değil | Her uca bir koşul |
| İki uç saf Neumann ve `r ≡ 0`, `q ≡ 0` | Çözüm tek değil (sabit kadar belirsiz) | Bir uca Dirichlet veya Robin |
| Bilinmeyen sembol | Tanımsız | İzin verilen adlar listesi |

## 2. Sınır koşulları
Her uçta genel biçim `α u′(x₀) + β u(x₀) = γ`, `(α, β) ≠ (0, 0)`.

| Tip | Koşul | Örnek yazım |
|---|---|---|
| Dirichlet (esas) | α = 0 | `u(0) = 1` |
| Neumann (doğal) | β = 0 | `u'(1) = 2` |
| Robin (karışık) | α ≠ 0, β ≠ 0 | `u'(1) + 3*u(1) = 1` |

### 2.1 Zayıf formdaki sınır terimi
Kısmi integrasyon:
$$
\int_a^b -(pu')'v\,\mathrm{d}x = \int_a^b p\,u'v'\,\mathrm{d}x \;-\; p(b)u'(b)v(b) \;+\; p(a)u'(a)v(a).
$$

### 2.2 Sağ uç (x = b), α_b ≠ 0
`u′(b) = (γ_b − β_b u(b)) / α_b` yerine konur:
- Bilineer forma: `+ p(b) (β_b/α_b) u(b)v(b)` → `K[N,N] += p(b) β_b/α_b`
- Yük vektörüne: `+ p(b) (γ_b/α_b) v(b)` → `F[N] += p(b) γ_b/α_b`

### 2.3 Sol uç (x = a), α_a ≠ 0
`u′(a) = (γ_a − β_a u(a)) / α_a`:
- `K[0,0] += − p(a) β_a/α_a`
- `F[0]   += − p(a) γ_a/α_a`

> Sol uçta dışa dönük normal −1 olduğu için işaretler terstir. Örnek (B10): `−u′(0) + 2u(0) = 1` → α = −1, β = 2, γ = 1
> → `K[0,0] += +2`, `F[0] += +1`. Pozitif katkı koersifliği korur.

### 2.4 Dirichlet: eliminasyon (lifting)
Bilinen düğümler D, serbest düğümler S: `K_SS U_S = F_S − K_SD U_D`. Belgede hem tam sistem hem indirgenmiş sistem gösterilir.
Satır değiştirme yöntemi **kullanılmaz** (simetriyi bozar, pedagojik olarak yanıltıcıdır).

## 3. Zayıf form ve Galerkin
`V = { v ∈ H¹(a,b) : Dirichlet uçlarında v = 0 }`. `u = u_D + w`, `w ∈ V` bulun öyle ki her `v ∈ V` için `B(u, v) = ℓ(v)`:
$$
B(u,v) = \int_a^b \bigl(p\,u'v' + q\,u'v + r\,uv\bigr)\mathrm{d}x + (\text{Robin } K \text{ katkıları}),\qquad
\ell(v) = \int_a^b f v\,\mathrm{d}x + (\text{Neumann/Robin } F \text{ katkıları}).
$$
Galerkin: `u_h = Σ_j U_j φ_j`, test fonksiyonları `v = φ_i` → `Σ_j B(φ_j, φ_i) U_j = ℓ(φ_i)` → **`K U = F`**, `K_ij = B(φ_j, φ_i)`.
`q ≠ 0` ise `K` simetrik değildir (konveksiyon terimi simetrik değildir); bu hata değildir.

## 4. Ayrıklaştırma
- Düzgün ağ: `x_k = a + k h`, `h = (b − a)/n`, `k = 0…n`. Eleman `e_k = [x_{k−1}, x_k]`.
- Referans eleman `ξ ∈ [−1, 1]`: `x(ξ) = (x_{k−1} + x_k)/2 + (h/2) ξ`, Jacobian `J = h/2`, `dN/dx = (2/h) dN/dξ`.

### 4.1 P1 (lineer)
`N₁ = (1 − ξ)/2`, `N₂ = (1 + ξ)/2`. Global serbestlik derecesi: `n + 1`. Global baz `φ_i` = düğüm i'de 1, komşularda 0 olan şapka fonksiyonu.

### 4.2 P2 (kuadratik), yerel sıra: sol, orta, sağ
`N₁ = ξ(ξ − 1)/2`, `N₂ = 1 − ξ²`, `N₃ = ξ(ξ + 1)/2`. Global serbestlik derecesi: `2n + 1`. Eleman k (1'den başlayarak) → global `[2k−2, 2k−1, 2k]`.

## 5. Eleman matrisleri
`K_ij = ∫ p N_j′ N_i′ dx`, `C_ij = ∫ q N_j′ N_i dx`, `M_ij = ∫ r N_j N_i dx`, `F_i = ∫ f N_i dx`; eleman sistem matrisi `A^e = K^e + C^e + M^e`.
(Belgede ve kodda `K` hem difüzyon parçası hem global sistem için kullanılır; belgede global sistem `\mathbf{A}` değil `\mathbf{K}` olarak anılır ve bu bir kez açıkça not edilir.)

### 5.1 Sabit katsayılar (tam kesirli hesapla doğrulandı)
**P1:**
$$
K^e=\frac{p}{h}\begin{pmatrix}1&-1\\-1&1\end{pmatrix},\;
C^e=\frac{q}{2}\begin{pmatrix}-1&1\\-1&1\end{pmatrix},\;
M^e=\frac{rh}{6}\begin{pmatrix}2&1\\1&2\end{pmatrix},\;
F^e=\frac{fh}{2}\begin{pmatrix}1\\1\end{pmatrix}
$$
**P2:**
$$
K^e=\frac{p}{3h}\begin{pmatrix}7&-8&1\\-8&16&-8\\1&-8&7\end{pmatrix},\;
C^e=\frac{q}{6}\begin{pmatrix}-3&4&-1\\-4&0&4\\1&-4&3\end{pmatrix},\;
M^e=\frac{rh}{30}\begin{pmatrix}4&2&-1\\2&16&2\\-1&2&4\end{pmatrix},\;
F^e=\frac{fh}{6}\begin{pmatrix}1\\4\\1\end{pmatrix}
$$
Kontrol özellikleri (test edilir): `K^e` ve `C^e` satır toplamları 0; `M^e` girdilerinin toplamı `rh`; `F^e` toplamı `fh`; `K^e` ve `M^e` simetrik.

### 5.2 Hesap yolları
1. **Tam sembolik:** SymPy `integrate` 2 s içinde `Integral` içermeyen kapalı form verirse kullanılır (polinom, rasyonel, `ln`, kesirli kuvvet `x^(3/4)` dahil). Belge bunu kullanır; sonuç kesir veya tam ifadedir.
2. **Sayısal (Gauss–Legendre):** Polinom integrand, derece d → `m = ⌈(d + 1)/2⌉` nokta **tam** sonuç verir.
   Derece: K için `deg p + 2(k−1)`, C için `deg q + 2k − 1`, M için `deg r + 2k`, F için `deg f + k` (k = eleman derecesi).
   Polinom olmayan katsayı/kaynak: P1 için m = 8, P2 için m = 10 ve `QUADRATURE_APPROX` bildirimi ("integraller sayısal yaklaşık").

> **Önemli:** Kareleme hatası FEM hatasından ayrıdır. Tekil kaynakta (S1, `f ~ x^{−5/4}`) sayısal kareleme düğüm tamlığını bozar.
> Doğrulandı: n = 64'te düğüm hatası 12 noktada 4.7e-5, 40 noktada 8.1e-6, 200 noktada 7.3e-7. Bu yüzden S1'de yük vektörü tam sembolik yolla hesaplanır.

## 6. Hata normları
$$
\|e\|_{L^2}=\Bigl(\int_a^b (u-u_h)^2\Bigr)^{1/2},\quad
|e|_{H^1}=\Bigl(\int_a^b (u'-u_h')^2\Bigr)^{1/2},\quad
\|e\|_{\infty,\mathrm{düğüm}}=\max_{\text{uç düğümler}}|u(x_i)-U_i|
$$
Eleman başına 10 noktalı Gauss. Göreli hatalar (`‖e‖/‖u‖`, `‖u‖ > 0` ise) de raporlanır.

### 6.1 A priori kestirimler (çözüm yeterince düzgünse, `u ∈ H^{k+1}`)
| Eleman | L² | H¹ yarı-norm | Dayanak |
|---|---|---|---|
| P1 (k=1) | O(h²) | O(h) | Céa lemması + interpolasyon; L² için Aubin–Nitsche dualite argümanı |
| P2 (k=2) | O(h³) | O(h²) | aynı |

### 6.2 Düğüm süperyakınsaması (1D'ye özgü)
`p` sabit ve `q = r = 0` ise, integraller tam hesaplandığında **eleman uç düğümlerindeki** FEM değerleri her `f` için tam çözüme eşittir
(P1 ve P2 için; P2 orta düğümleri hariç). Neden: Green fonksiyonu `G(x_i, ·)` parçalı lineerdir ve FEM uzayının içindedir.
`p` değişkense (B3) veya `q, r ≠ 0` ise (B4, B10) düğüm tamlığı yoktur. Test edilir ve belgede bir not kutusuyla açıklanır.

### 6.3 Tam temsil
Tam çözüm FEM uzayının içindeyse (P1 için lineer, P2 için kuadratik çözüm) hata makine hassasiyetindedir (~1e-14).
Bu durumda oran hesaplanmaz, `MACHINE_PRECISION` bayrağı ve "tam çözüm eleman uzayında" notu gösterilir (B1-P2, B6-P2, B7-P2, B9-P2, M2-P2).

### 6.4 Tekil çözümler — düzgünlük varsayımı
`u = x^α` (`1/2 < α < 1`) gibi `u ∉ H²` çözümlerde düzgün ağda oranlar eleman derecesinden bağımsız olarak düşer:
L² ≈ α + 1/2, H¹ ≈ α − 1/2. S1 (α = 3/4): **L² ≈ 1.25, H¹ ≈ 0.25, hem P1 hem P2 için** (doğrulandı).
Bu, yöntemin hatası değil, kestirimin varsayımının sağlanmamasıdır. Çare: derecelendirilmiş ağ (E2).

## 7. Yakınsama oranı
Ardışık: `ρ_k = ln(e_k / e_{k+1}) / ln(h_k / h_{k+1})`.
"Asimptotik bölgede" bayrağı: son iki ardışık oran teorik orandan en fazla 0.1 sapıyorsa.
Hata < 1e-12 ise oran hesaplanmaz (`MACHINE_PRECISION`).

## 8. Tanılama
| Kod | Koşul | Anlam |
|---|---|---|
| `PECLET` | `Pe = max |q| h / (2p) > 1` (her n için ayrı) | Standart Galerkin'de düğüm salınımı beklenir (B5, n = 8: Pe = 1.25, min U ≈ −0.111) |
| `NON_COERCIVE` | `min (r − q′/2) < 0` | Kararlılık garanti değil; Helmholtz tipi (B8): `k h > 1` iken çözünürlük yetersiz, asimptotik bölge geç başlar |
| `MACHINE_PRECISION` | hata < 1e-12 | Tam temsil (§6.3) |
| `QUADRATURE_APPROX` | sayısal kareleme yolu kullanıldı | §5.2 |
| `ILL_CONDITIONED` | `cond(K) > 1e10` (n ≤ 1024) | Yuvarlama hatası etkili olabilir |
| `NO_EXACT_SOLUTION` | dsolve bulamadı / zaman aşımı | Kıyas yapılmaz; MMS önerilir |

## 9. Girdi dilbilgisi
- Bağımsız değişken `x`, bilinmeyen `u` (`y` de kabul edilir ve `u`'ya çevrilir).
- Türev: `u'`, `u''`, `diff(u, x)`, `diff(u, x, 2)`, `(ifade*u')'` (çarpım kuralıyla açılır).
- Fonksiyonlar: `sin cos tan exp log sqrt sinh cosh tanh`; sabitler `pi`, `E`; kuvvet `^` veya `**`.
- Tam bir `=`; yoksa `= 0`.
- Alan `[a, b]` ayrı girilir; varsayılan `[0, 1]`.

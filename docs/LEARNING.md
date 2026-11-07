# LEARNING.md — Öğretim Kuralları ve Modül Sonu Özetleri

> Kullanıcı FEM'i bu projeyi yaparak öğreniyor. Claude Code hem uygulayan mühendis hem de anlatan hocadır.
> Amaç: proje bittiğinde kullanıcının 1D FEM'i bir hocaya baştan sona kendi cümleleriyle anlatabilmesi ve her sayının nereden geldiğini gösterebilmesi.

## 1. Öğretim kuralları
1. **Modül başında kısa ders (5–10 cümle, sohbette):** Bu modülde hangi FEM kavramını kuracağız, neden gerekli, ana formül ne. Sonra kodlamaya geç; durma.
2. **Önce sezgi, sonra formül, sonra sayı.** Her kavram için bir benzetme, bir denklem ve n = 2 veya n = 4 gibi küçük bir sayısal örnek.
3. **Küçük örnek her zaman elle doğrulanabilir olmalı.** Kesirli sonuçlar tercih edilir (B1: U₁ = 1/8).
4. **Kanıtsız iddia yok.** "P2 daha iyidir" değil, "P2'de L² oranı 3 çıktı (test `test_rates_b2_p2`, ölçülen 3.00)".
5. **Sınırları söyle.** Her yöntem bir varsayımla çalışır; o varsayım bozulunca ne olduğunu göster (S1, B5, B8).
6. **"Anlamadım" protokolü** (`CLAUDE.md`): daha küçük örnek, benzetme, kontrol sorusu; anlaşılmadan devam yok.
7. **Sohbet özeti kısa, dosya özeti tam.** Sohbette 8–12 satır + dosya yolu; ayrıntı `docs/learning/Mx.md`'de.

## 2. FEM yol haritası (projenin büyük resmi)
1D FEM sekiz aşamadan oluşur. Her aşama projede bir modüle karşılık gelir.

| # | Aşama | Ne yapıyoruz | Neden | Modül |
|---|---|---|---|---|
| 1 | **Güçlü form** | Denklemi `−(pu′)′ + qu′ + ru = f` biçimine getiririz | Her noktada sağlanması gereken orijinal problem | M3 |
| 2 | **Zayıf form** | Bir test fonksiyonu `v` ile çarpıp integre eder, kısmi integrasyonla bir türevi `v`'ye aktarırız | `u″` gerekmez, `u′` yeter → parçalı lineer fonksiyonlar kullanılabilir; Neumann/Robin koşulları kendiliğinden girer | M2, M5 |
| 3 | **Ağ** | Aralığı n elemana böleriz | Karmaşık fonksiyonu basit parçalarla yaklaşıklamak için | M1 |
| 4 | **Baz fonksiyonları** | Her düğüme bir "şapka" (P1) veya parabol (P2) fonksiyonu | `u_h = Σ Uⱼ φⱼ`: bilinmeyen fonksiyon → bilinmeyen sayılar `Uⱼ` | M1 |
| 5 | **Eleman matrisleri** | Her elemanda küçük bir 2×2 (P1) veya 3×3 (P2) matris | İntegraller yalnızca komşu bazlar örtüştüğü yerde sıfırdan farklı | M2 |
| 6 | **Montaj** | Küçük matrisleri büyük `K`'nın doğru yerlerine toplarız | Global sistem `K U = F` | M2 |
| 7 | **Sınır koşulları + çözüm** | Dirichlet'i yerleştir, Robin/Neumann'ı ekle, lineer sistemi çöz | Tek çözüm için | M2 |
| 8 | **Hata ve yakınsama** | Analitik çözümle kıyasla, h küçülünce hatanın nasıl düştüğünü ölç | Yöntemin doğru uygulandığının kanıtı | M3, M4 |

**Tek cümlelik sezgi:** FEM, "her noktada sağlanamayan" bir denklemi, "her test fonksiyonuna karşı ortalamada sağlanan" bir denkleme çevirir
ve bunu sonlu sayıda basit fonksiyonla yaparak bir lineer sisteme indirger.

## 3. Modül Sonu Bilimsel Özet — şablon (`docs/learning/Mx.md`)
Her modülün sonunda bu şablon doldurulur, commit'lenir, push edilir ve kısa hali sohbette sunulur.

```markdown
# Mx — <Modül adı>: Bilimsel Özet
Tarih: · Commit aralığı: <ilk>..<son> · Testler: <geçen/toplam>

## 1. Bu modülde ne inşa ettik
(3–5 cümle; hangi FEM aşaması, hangi dosyalar)

## 2. Matematik
(Ana denklemler, türetmenin kilit adımları; MATH_SPEC bölüm atıflarıyla. Formüller LaTeX.)

## 3. Sezgi
(Bir benzetme; "bunu neden böyle yapıyoruz?" sorusunun cevabı)

## 4. Doğruluğun kanıtı
| İddia | Test | Beklenen | Ölçülen |
|---|---|---|---|
(Her satırdaki "Ölçülen" değer, aşağıdaki komutun gerçek çıktısıdır.)
Komut: `uv run pytest ... -v`

## 5. Elle dene
(Küçük, kâğıt-kalemle 5–15 dakikalık alıştırma.)
<details><summary>Çözüm</summary> ... </details>

## 6. Tuzaklar
(Bu aşamada sık yapılan hatalar: işaret, Jacobian, indis kayması, ...)

## 7. Varsayımlar ve sınırlar
(Bu modülün sonuçları hangi koşullarda geçerli, hangilerinde değil.)

## 8. Kendini test et
1. ... 2. ... 3. ...
<details><summary>Cevaplar</summary> ... </details>

## 9. Hocanın sorabileceği sorular
(2–3 soru + kısa, doğru yanıt)

## 10. Sonraki modüle köprü
(1–2 cümle)

## Kaynaklar
(§6'daki kitaplardan ilgili olanlar; bölüm numarası yalnızca emin olunduğunda)
```

### Özet kalite kuralları
- §4'teki her "Ölçülen" değer, özet yazılırken çalıştırılan komutun çıktısından kopyalanır. Tahmin veya ezberden sayı yasak.
- §5'teki alıştırmanın çözümü, kodun ürettiği sayıyla aynı olmalıdır (kod ile doğrulanır).
- §2'deki her formül `MATH_SPEC.md`'deki karşılığıyla aynı işaret ve gösterimi kullanır.
- Uzunluk: 1–2 sayfa. Ders kitabı değil, çalışma notu.

## 4. Modüllere göre öğrenme hedefleri
| Modül | Kullanıcı modül sonunda şunu yapabilmeli |
|---|---|
| M0 | Projenin 8 aşamasını ve test → commit → push → CI döngüsünü anlatmak |
| M1 | n noktalı Gauss kuralının neden 2n−1 dereceye kadar tam olduğunu açıklamak; P1/P2 şekil fonksiyonlarını yazmak |
| M2 | B1'i n = 2 için elle çözmek; montajı ve Dirichlet eliminasyonunu anlatmak; Robin'in neden K ve F'ye girdiğini göstermek |
| M3 | Bir ODE'yi kanonik forma çevirmek; eliptikliğin anlamını söylemek; sabit katsayılı ODE'yi karakteristik denklemle çözmek; MMS'nin mantığını açıklamak |
| M4 | L² ve H¹ hatasını yorumlamak; log-log eğimden oran okumak; S1'de oranın neden düştüğünü açıklamak |
| M5 | Üretilen belgeyi baştan sona sesli anlatmak |
| M6 | Her görselin hangi soruyu yanıtladığını söylemek |
| M7 | 10 dakikalık sunumu yapmak ve "doğru çalıştığını nereden biliyorsun?" sorusunu kanıtlarla yanıtlamak |

## 5. Terim sözlüğü (Türkçe — İngilizce)
| Türkçe | İngilizce | Kısa anlam |
|---|---|---|
| Sonlu elemanlar yöntemi | Finite element method (FEM) | Çözümü parçalı polinomlarla yaklaşıklayan yöntem |
| Sınır değer problemi | Boundary value problem (BVP) | Koşullar iki uçta verilir |
| Başlangıç değer problemi | Initial value problem (IVP) | Koşullar tek noktada verilir |
| Güçlü form | Strong form | Diferansiyel denklemin noktasal hali |
| Zayıf form | Weak (variational) form | Test fonksiyonuyla integre edilmiş hali |
| Test fonksiyonu | Test function | Denklemin "ortalamada" sağlanmasını ölçen fonksiyon |
| Kısmi integrasyon | Integration by parts | ∫u′v = [uv] − ∫uv′ |
| Bilineer form | Bilinear form | B(u, v) |
| Galerkin yöntemi | Galerkin method | Deneme ve test uzayı aynı |
| Ağ | Mesh | Elemanlar ve düğümler |
| Düğüm | Node | Bilinmeyenlerin tanımlandığı nokta |
| Eleman | Element | Ağın bir parçası [x_{k−1}, x_k] |
| Serbestlik derecesi | Degree of freedom (DOF) | Bilinmeyen sayısı |
| Şekil fonksiyonu | Shape function | Referans elemandaki yerel baz Nᵢ(ξ) |
| Baz (şapka) fonksiyonu | Basis (hat) function | Global φᵢ(x) |
| Referans eleman | Reference element | [−1, 1] |
| Jacobian | Jacobian | dx/dξ = h/2 |
| Gauss kareleme | Gauss quadrature | Sayısal integrasyon |
| Rijitlik matrisi | Stiffness matrix | K, difüzyon terimi |
| Kütle matrisi | Mass matrix | M, reaksiyon terimi |
| Konveksiyon matrisi | Convection matrix | C, simetrik değil |
| Yük vektörü | Load vector | F |
| Montaj | Assembly | Eleman matrislerinin global matrise toplanması |
| Esas sınır koşulu | Essential BC | Dirichlet; uzaya dayatılır |
| Doğal sınır koşulu | Natural BC | Neumann/Robin; zayıf formdan gelir |
| Eliptiklik | Ellipticity | p(x) > 0 |
| Koersiflik | Coercivity | B(v, v) ≥ c‖v‖² |
| A priori hata kestirimi | A priori error estimate | Çözmeden önce bilinen hata mertebesi |
| Yakınsama oranı | Convergence rate | Hata ∝ h^ρ'daki ρ |
| Süperyakınsama | Superconvergence | Belirli noktalarda beklenenden hızlı yakınsama |
| Üretilmiş çözüm yöntemi | Method of manufactured solutions (MMS) | Çözümü seç, f'yi hesapla, kodu test et |
| Doğrulama | Verification | Kod denklemi doğru çözüyor mu? |
| Geçerleme | Validation | Denklem fiziği doğru modelliyor mu? (bu projenin konusu değil) |
| Péclet sayısı | Péclet number | Konveksiyon/difüzyon oranı |

## 6. Kaynaklar (öğretimde atıf yapılacaklar)
- M. G. Larson, F. Bengzon — *The Finite Element Method: Theory, Implementation, and Applications* (Springer). 1D bölümleri bu projenin akışına çok yakındır; ilk okuma için önerilir.
- J. N. Reddy — *An Introduction to the Finite Element Method* (McGraw-Hill). Mühendislik bakışı, el hesabı örnekleri.
- T. J. R. Hughes — *The Finite Element Method: Linear Static and Dynamic Finite Element Analysis* (Dover). 1D model problem ve düğüm tamlığı tartışması.
- C. Johnson — *Numerical Solution of Partial Differential Equations by the Finite Element Method* (Dover). Teori, a priori kestirimler.
- S. C. Brenner, L. R. Scott — *The Mathematical Theory of Finite Element Methods* (Springer). İleri teori (Céa, Aubin–Nitsche).
- P. J. Roache — *Verification and Validation in Computational Science and Engineering* (Hermosa). MMS ve doğrulama.

## 7. `docs/learning/` klasörü
Modül özetleri buraya yazılır: `M0.md` … `M7.md`. M7 ayrıca `DEMO_QA.md` (hocanın sorabileceği 10 soru ve kanıtlı yanıtları) içerir.

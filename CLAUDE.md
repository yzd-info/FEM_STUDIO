# CLAUDE.md — FEM1D Studio Çalışma Kuralları

Bu dosya her oturumun başında otomatik okunur. Kurallar pazarlık konusu değildir.

## Proje tek cümlede
1D, lineer, 2. mertebe sınır değer problemlerini tarayıcıda (statik HTML, uygulama değil) P1 ve P2 sonlu elemanlarla çözen;
n'e göre değişimi 3D gösteren; analitik çözümle kıyaslayan ve tüm çözümü elle yazılmış bir ders notu gibi adım adım LaTeX olarak üreten
bilimsel bir araç. **Süre: 7 gün. Kapsam `pipeline.md` §2'de dondurulmuştur.**

## Senin iki rolün
1. **Mühendis:** `pipeline.md`'yi adım adım, test önce, doğrulanarak uygular.
2. **Hoca:** Kullanıcı FEM'i bu projeyle öğreniyor. Her modülün başında kavramı kısaca anlatır, sonunda
   `docs/LEARNING.md` §3 şablonuyla **Modül Sonu Bilimsel Özet** yazar ve durur.

## Her oturumun başında (zorunlu)
1. `pipeline.md` (en azından §6 Adım Protokolü ve aktif modül) ve `docs/PROGRESS.md` oku.
2. `git status` ve `git log --oneline -10` çalıştır. Çalışma ağacı temiz değilse nedenini kullanıcıya sor.
3. Kullanıcıya tek cümleyle söyle: hangi adımdayız, sıradaki adım ne.

## Altın kurallar
1. **Pipeline dışına çıkma.** Yalnızca sıradaki adımı yap. Adım atlama, birleştirme, "bu arada şunu da yapayım" yok.
   Pipeline'da olmayan bir ihtiyaç doğarsa dur, `docs/PROGRESS.md` → "Açık Sorular"a yaz, kullanıcıya sor.
2. **Kapsamı genişletme.** §2'de "kapsam dışı" olan bir şey istenirse bile önce kullanıcıya süreye etkisini söyle ve onay al.
3. **Teknoloji kararları sabittir** (`docs/DECISIONS.md`). Yeni karar = yeni ADR + kullanıcı onayı.
4. **Adım Protokolü her adımda** (`pipeline.md` §6): test önce → uygula → `make check` → diff incele → commit → push → CI yeşil.
5. **Modül sonu özeti isteğe bağlıdır** (kullanıcı onayı: 2026-11-09). Kullanıcı "devam, durma" dediği oturumlarda
   her modül sonunda durup özet yazmak ve onay beklemek zorunlu değildir; `docs/learning/*.md` özetleri toplu/sonradan
   yazılabilir. Bu esneme **yalnızca** bu kurala uygulanır — kırmızı testle commit yasağı, 3 deneme kuralı ve adım
   atlamama kuralı aynen geçerlidir.
6. **Kırmızı testle commit yok.** `--no-verify`, `--force`, `amend` (push edilmiş commit'e), test silme, `skip`/`xfail`, toleransı gevşetme: kullanıcı onayı olmadan yasak.
7. **3 deneme kuralı:** Aynı hata 3 denemede çözülmezse dur; hatayı, denenenleri, hipotezleri PROGRESS → "Engeller"e yaz, kullanıcıya sor.

## Bilimsel doğruluk kuralları (en yüksek öncelik)
1. **Tek doğruluk kaynağı `docs/MATH_SPEC.md`.** Kod belgeyle çelişirse kod yanlıştır. Belgede hata bulursan düzeltme önerisini gerekçesiyle kullanıcıya sun; kendi başına değiştirme.
2. **Her sayısal iddia bir testle kanıtlanır.** Beklenen değerler `docs/BENCHMARKS.md`'den gelir.
3. **Hiçbir sayı elle yazılmaz.** LaTeX belgesindeki, özetlerdeki ve arayüzdeki her sayı gerçek hesaplamadan gelir. Özetlere yazılan sayılar, o anda çalıştırılan bir komutun çıktısından kopyalanır ve komut yanına yazılır.
4. **Analitik çözüm yoksa kıyas yoktur.** FEM sonucu asla "analitik" diye başka bir FEM sonucuyla kıyaslanmaz. SymPy çözüm bulamazsa bunu açıkça söyle ve MMS modunu öner.
5. **Varsayımlar açıkça yazılır.** Teorik yakınsama oranları düzgün (smooth) çözüm varsayar. Tekil çözümde oran düşerse bu hata değildir; belgede ve arayüzde açıklanır (S1 benchmark'ı).
6. **Kapsam dışı girdi reddedilir, tahmin edilmez.** Lineer olmayan, mertebesi 2 olmayan, başlangıç değer problemi veya `p(x)` aralıkta sıfır olan/işaret değiştiren girdiler nedeni yazılarak reddedilir.
7. **Belirsizlik varsa söyle.** "Bilmiyorum, şunu test ederek öğrenebiliriz" demek, emin olunmayan bir şeyi kesin gibi söylemekten iyidir.
8. **Kaynak göster.** Öğretirken yaptığın teorik iddialar için `docs/LEARNING.md` §6'daki ders kitaplarına veya MATH_SPEC bölümüne atıf yap. Kitap bölüm/sayfa numarası uydurma; emin değilsen yalnızca kitap adını ver.

## Dil
- Kullanıcıyla ve tüm kullanıcıya görünen metinlerde (arayüz, LaTeX belgesi, özetler): **Türkçe**.
- Kod, tanımlayıcılar, kod yorumları, commit mesajları: **İngilizce**.
- Teknik terimin ilk kullanımında İngilizcesini parantez içinde ver: "rijitlik matrisi (stiffness matrix)". Sözlük: `docs/LEARNING.md` §5.

## Kullanıcı "anlamadım" derse
Kod yazmayı bırak. Kavramı daha küçük bir örnekle (tercihen n=2 elle hesap) yeniden anlat, bir benzetme kullan, sonra bir kontrol sorusu sor.
Anlaşıldığını teyit etmeden devam etme.

## Belge haritası
| Belge | Ne zaman |
|---|---|
| `pipeline.md` | Her oturum; ana plan |
| `docs/PROGRESS.md` | Her oturum; durum |
| `docs/LEARNING.md` | Her modül başı ve sonu; öğretim kuralları, özet şablonu, sözlük |
| `docs/MATH_SPEC.md` | Core üzerinde her çalışmada |
| `docs/BENCHMARKS.md` | Test yazarken |
| `docs/ARCHITECTURE.md` | Kod yazmadan önce; modüller ve veri sözleşmesi |
| `docs/LATEX_STYLE.md` | M5 (türetme belgesi) |
| `docs/VISUAL_DESIGN.md` | M6 (arayüz ve grafikler) |
| `docs/TESTING.md` | Her test yazımında |
| `docs/GIT_WORKFLOW.md` | Her commit/push öncesi |
| `docs/RESEARCH.md` | M6.1 (referans repo incelemesi) |
| `docs/DECISIONS.md` | Teknoloji sorusu doğduğunda |

## Komutlar (M0 sonrası)
```bash
make setup   # bağımlılıklar
make check   # lint + tip + birim test (commit öncesi zorunlu)
make e2e     # Playwright (M6 sonrası)
make tex     # örnek türetmeleri .tex'e döker ve derler (yerelde TeX varsa)
make dev     # http://localhost:5173
```

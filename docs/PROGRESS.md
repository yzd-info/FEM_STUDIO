# PROGRESS.md — Durum

> Claude Code her adımın başında (🔄) ve sonunda (✅) günceller. Güncelleme adımın commit'ine dahildir.

## Aktif
- **Modül:** M3 — ODE ayrıştırıcı ve analitik çözüm
- **Adım:** M3.2 — Kanonikleştirme
- **Gün:** 2 / 7

## Ortam (M0.1'de doldurulur)
| Araç | Sürüm | Not |
|---|---|---|
| git | 2.55.0.windows.3 | OK |
| gh (auth) | 2.103.3 | giriş yapıldı: yzd-info (M0.3) |
| uv | 0.13.7 | kuruldu (winget) |
| node | v24.19.0 | LTS (Node 24, Maintenance LTS — EOL 2028-04-30) |
| python (yerel) | 3.14.7 | Pyodide'in Python minör sürümüyle (3.14) eşleşiyor |
| Pyodide (hedef) | 314.0.7 (2026-09-14) | içerdiği Python: 3.14.2 — [değişiklik günlüğü](https://pyodide.org/en/stable/project/changelog.html) |
| TeX (yerel, isteğe bağlı) | — | kurulu değil; yoksa LaTeX derlemesi yalnızca CI'da yapılır (engel değil) |
| make | 4.4.1 (ezwinports) | M0.1'de atlanmış, M0.6'da fark edilip kuruldu (`winget install ezwinports.make`) |

## Adımlar
Durumlar: ⏳ bekliyor · 🔄 devam · ✅ bitti · ⛔ engelli · 🚦 kullanıcı onayı bekleniyor

| Adım | Durum | Not | Tarih |
|---|---|---|---|
| M0.1 | ✅ | git/node/python mevcut; Pyodide 314.0.7 (Python 3.14.2) seçildi, yerel Python 3.14.7 minör sürümde eşleşiyor; gh ve uv winget ile kuruldu | 2026-11-04 |
| M0.2 | ✅ | `git init -b main`; `.gitignore` eklendi; README taslağı zaten mevcuttu | 2026-11-07 |
| G0 | ✅ | Kullanıcı onayı: repo adı `FEM_STUDIO`, görünürlük public | 2026-11-07 |
| M0.3 | ✅ | `gh auth login` (yzd-info) tamamlandı; `gh repo create FEM_STUDIO --public --source . --remote origin --push` → https://github.com/yzd-info/FEM_STUDIO | 2026-11-07 |
| M0.4 | ✅ | `core/pyproject.toml` (src layout, ruff+mypy+pytest+hypothesis+scikit-fem); `fem1d/__init__.py` (`__version__="0.1.0"`); `test_version_is_semver_string` kırmızı→yeşil; `uv run ruff check`/`ruff format --check`/`mypy` temiz | 2026-11-07 |
| M0.5 | ✅ | Vite+TS strict scaffold (`npm create vite -- --template vanilla-ts`), boş sayfa ("FEM1D Studio"); vitest (jsdom) + Playwright (Chromium) kuruldu; `smoke.test.ts` ve `smoke.spec.ts` kırmızı→yeşil; `tsc --noEmit` temiz | 2026-11-07 |
| M0.6 | ✅ | `Makefile` (§12.1 hedefleri) + `.github/workflows/ci.yml` (python, web işleri); yerelde `make check` ve `make e2e` yeşil; CI ilk push'ta doğrulanacak | 2026-11-07 |
| M1.1 | ✅ | `fem1d/quadrature.py` (`gauss_legendre`, `integrate`); hypothesis testi m-point kuralın 2m−1 dereceye kadar tam, 2m derecede tam olmadığını doğruluyor; `make check` yeşil, CI yeşil | 2026-11-07 |
| M1.2 | ✅ | `fem1d/mesh.py` (`build_mesh`); tekdüze ağ, P1 (n+1 düğüm) ve P2 (2n+1 düğüm) bağlantı tablosu; eleman k → P1 `[k,k+1]`, P2 `[2k,2k+1,2k+2]`; `make check` yeşil, CI yeşil | 2026-11-07 |
| M1.3 | ✅ | `fem1d/elements.py`; P1/P2 referans şekil fonksiyonları (sayısal+sembolik) ve türevleri; Σ Nᵢ=1, Σ Nᵢ′=0, Nᵢ(ξⱼ)=δᵢⱼ, sembolik↔sayısal eşitlik; `make check` yeşil, CI yeşil | 2026-11-07 |
| M2.1 | ✅ | `core/tests/fixtures/{B1_P1_n2,B1_P1_n4,B3_P1_n2}.json`; elle hesaplanmış K,F,U (kesir); `test_fixtures.py` ile iç tutarlılık (KU=F iç düğümlerde) doğrulandı; `make check` yeşil, CI yeşil | 2026-11-07 |
| M2.2 | ✅ | `fem1d/element_matrices.py`: Gauss-Legendre kuadratürüyle K,C,M,F (P1/P2); §5.2 derece kuralıyla nokta sayısı, bilinmeyen derece için sabit nokta + `quadrature_approx=True`; hypothesis testleri §5.1 kapalı formlarla eşleşiyor; `make check` yeşil, CI yeşil | 2026-11-08 |
| M2.3 | ✅ | `fem1d/element_matrices.py`: `element_matrices_symbolic` (SymPy `integrate`, §5.2.1), K/M simetrisinden yararlanılarak hesaplanıyor; `exact=False` sonuçta `Integral` kalırsa (ör. tanımsız `g(x)`); B3 kapalı-form fixture'ı, sabit katsayıda sayısal kuadratürle eşleşme (hypothesis, `rtol=atol=1e-12`) ve tanımsız integrand testleriyle doğrulandı; `uv run pytest -m "not slow"` → 927 passed (675.29s); `make check` tam yeşil (ruff/mypy/tsc/pytest/vitest) | 2026-11-09 |
| M2.4–M2.6, M4.1–M4.3 | ✅ | **Not (sıra sapması):** bu adımların kodu (`assembly.py`, `boundary.py`, `solver.py`, `analysis.py` + testleri + `tests/bench.py`/`conftest.py`/`tests/integration/`) M2.3'ten önce, pipeline sırası dışında yazılmış halde bulundu. Kullanıcı onayı (2026-11-09): M2.3 önce bitirilip koddan geriye doğru sıra düzeltilsin, bu dosyalar olduğu gibi tutulup doğrulansın. `uv run pytest -m "not slow"` çalıştırıldı → 927 passed, 0 failed (bu dosyaları kapsayan testler dahil); ayrı commit'lerle kayda geçirildi (M2.4: `b12e51b`, M2.5: `6a98375`, M2.6: `2b0c38b`, M4.1-M4.3: `d7ea15b`) | 2026-11-09 |
| M2.7 | ✅ | `core/tests/oracle/test_scikit_fem_oracle.py`: scikit-fem ile tamamen bağımsız bir montaj (kendi `BilinearForm`/`LinearForm`, kendi kareleme) ve çözüm (`condense`+`solve`); yalnızca Robin/Neumann köşe terimi cebiri `boundary.py` ile aynı formülü (temel cebir, ayrıklaştırmanın kendisi değil) kullanıyor. B1–B10, P1/P2, n=6: göreli fark en fazla ~4.9e-15 (eşik 1e-10, `docs/TESTING.md` §1); 20/20 passed. `make check` tam yeşil: ruff/mypy/tsc temiz, `uv run pytest -m "not slow"` → 947 passed (725.44s), vitest 1 passed | 2026-11-09 |
| M2.8 | ✅ | Yeni kod gerekmedi: pipeline'ın istediği kapsam (B1, B6, B7, M2, M3, M4) M2.6 toplu commit'inde (`2b0c38b`) zaten vardı — `test_p1_rates_and_p2_exactness_for_polynomial_solutions_of_degree_le_2` (a: P_k içindeki tam çözüm → FEM tam; B1,B6,B7,M2) ve `test_nodal_superconvergence_when_p_constant_and_q_r_zero` (b: sabit p, q=r=0 → uç düğümler tam; B1,B2,B6,B7,M2,M3,M4) `core/tests/integration/test_fem_end_to_end.py`'de doğrulanmış halde | 2026-11-09 |
| M3.1 | ✅ | `fem1d/parsing.py`: `parse_equation` — `'`/`diff(u,x,k)`/`(ifade*u')'` (çarpım kuralıyla, `Derivative.doit()`) → SymPy; beyaz liste ad alanı (`parse_expr(..., global_dict={})`, `eval` yok), ek olarak izin verilen karakter kümesi ve Python anahtar kelime reddi (`__import__`, `and`, `if`... güvenlik için). Test: `core/tests/unit/test_parsing.py`, `BENCHMARKS.md` §2'nin tamamı (B1,B3,B3′,B4,B5,B8,B9,B10,M4) + 20 geçersiz girdi (enjeksiyon denemeleri dahil) = 46 test. `make check` tam yeşil: ruff/mypy/tsc temiz, `uv run pytest -m "not slow"` → 993 passed (774.58s), vitest 1 passed | 2026-11-09 |

## Modül kapıları
| Modül | Özet dosyası | Etiket | Kullanıcı onayı |
|---|---|---|---|
| G0 (repo) | — | — | ⏳ |
| M0 | docs/learning/M0.md | m0-done | ✅ (2026-11-07) |
| M1 | docs/learning/M1.md | m1-done | ✅ (2026-11-08) |
| M2 | docs/learning/M2.md (henüz yazılmadı — kural 5 esnemesiyle sonradan/toplu yazılacak, 2026-11-09) | m2-done | ⏳ (kullanıcı 2026-11-09: durmadan devam et) |
| M3 | docs/learning/M3.md | m3-done | ⏳ |
| M4 | docs/learning/M4.md | m4-done | ⏳ |
| M5 | docs/learning/M5.md | m5-done | ⏳ |
| M6 | docs/learning/M6.md | m6-done | ⏳ |
| M7 | docs/learning/M7.md | v1.0.0 | ⏳ |

## Açık Sorular
- (yok)

## Engeller
<!-- 3 deneme kuralı: hata, denenenler, hipotezler -->
- (yok)

## Takvim sapması
<!-- Bir modül planlanan günü aşarsa buraya yaz ve kullanıcıya bildir -->
- (yok)

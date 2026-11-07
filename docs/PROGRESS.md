# PROGRESS.md — Durum

> Claude Code her adımın başında (🔄) ve sonunda (✅) günceller. Güncelleme adımın commit'ine dahildir.

## Aktif
- **Modül:** M1 — Referans eleman
- **Adım:** M1.2 — Ağ (uniform mesh, P1/P2 connectivity)
- **Gün:** 1 / 7

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

## Modül kapıları
| Modül | Özet dosyası | Etiket | Kullanıcı onayı |
|---|---|---|---|
| G0 (repo) | — | — | ⏳ |
| M0 | docs/learning/M0.md | m0-done | ✅ (2026-11-07) |
| M1 | docs/learning/M1.md | m1-done | ⏳ |
| M2 | docs/learning/M2.md | m2-done | ⏳ |
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

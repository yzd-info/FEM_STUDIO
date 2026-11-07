# TESTING.md — Test Stratejisi

> Bu projede test, matematiksel doğruluğun kanıtıdır. Testi gevşetmek kanıtı yok etmektir.

## 1. Core test türleri
| Tür | Klasör | Araç | Kanıtladığı |
|---|---|---|---|
| Birim | `tests/unit/` | pytest | Her fonksiyon `MATH_SPEC` ile uyumlu |
| Özellik | `tests/unit/` | hypothesis | Kareleme tamlığı; kanonik dönüşümün geri açılımı; birimin ayrışımı |
| Fikstür | `tests/unit/test_fixtures.py` | `fractions.Fraction` | B1 (n=2,4), B3 (n=2) sistemleri **kesir düzeyinde** |
| Kâhin | `tests/oracle/` | scikit-fem | Bağımsız bir kütüphaneyle aynı düğüm değerleri (< 1e-10) |
| Yakınsama | `tests/integration/` | pytest | `BENCHMARKS.md` §3 değerleri ve oran aralıkları |
| Düğüm tamlığı | `tests/integration/` | pytest | `BENCHMARKS.md` §3.3 (hem "tam olmalı" hem "tam olmamalı") |
| Reddetme | `tests/unit/test_scope_gate.py` | pytest | `BENCHMARKS.md` §5 |
| Snapshot | `tests/snapshots/` | syrupy | Türetme adımlarının LaTeX çıktısı (B1, B4) |
| Şema | `tests/integration/` | jsonschema | Her benchmark sonucu şemaya uyar |
| Katman | `tests/test_layers.py` | ast | `derivation` hesap modüllerini çağırmaz |

## 2. Kurallar
- **TDD (core):** Test önce yazılır ve kırmızı görülür. Commit gövdesinde `Tests:` satırı.
- **Toleranslar sabittir:** kayan nokta `rtol=1e-12, atol=1e-14`; kâhin `rtol=1e-10`; referans hata tablosu göreli %1; oranlar `BENCHMARKS.md` aralıkları.
  Tolerans değiştirmek = kullanıcı onayı.
- **"Tam olmamalı" testleri de yazılır.** Örneğin B3'te düğüm hatasının 1e-12'den büyük olduğu test edilir; yoksa yanlış bir "tamlık" fark edilmez.
- Snapshot güncellemesi ayrı commit: `test(snapshots): update ...` + gövdede neden.
- hypothesis CI'da `derandomize=True`, `max_examples=200`.
- Yavaş testler (`dsolve`, n ≥ 512) `@pytest.mark.slow`: `make check` hariç tutar, CI koşar.

## 3. Web testleri
| Tür | Araç | Kapsam |
|---|---|---|
| Birim | vitest | `viz/*` `buildTraces` (gerçek core fikstürleriyle), `doc/` biçimlendirme |
| KaTeX | vitest | Tüm benchmark türetmelerindeki her denklem `throwOnError: true` ile render edilir |
| e2e | Playwright (Chromium) | Yükle → çöz → sekmeler → belge → `.tex` indir; `pipeline.md` §12.3 senaryoları; reddetme mesajları |

Fikstür akışı: `scripts/export_fixtures.py` → `web/tests/fixtures/*.json`. Core değişince yeniden üretilir; CI `git diff --exit-code` ile güncelliği kontrol eder.

## 4. LaTeX derleme testi
CI `latex` işi: TeX Live içeren bir GitHub Action (sürüm M0.6/M5.9'da güncel kararlı olarak doğrulanır) ile örnek `.tex`'ler derlenir; log'da `Error` / `Undefined` olmamalı; PDF'ler artefakt.

## 5. Her adım için "bitti" kontrol listesi
- [ ] Yeni davranış için test var ve önce kırmızı görüldü
- [ ] `make check` yeşil
- [ ] İlgiliyse `make e2e` / `make tex` yeşil
- [ ] CI yeşil (`gh run watch --exit-status`)
- [ ] PROGRESS.md güncel

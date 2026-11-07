# ARCHITECTURE.md — Mimari ve Veri Sözleşmesi

## 1. İlkeler
1. **Tek matematik kaynağı:** Tüm hesap `core/` (Python `fem1d`) içinde. Web tarafı yalnızca gösterir.
2. **Saf fonksiyonlar:** `solve(request) → result` deterministik; global durum yok.
3. **Belge hesap yapmaz:** `derivation/` yalnızca `SolveContext` içindeki hazır sonuçları biçimlendirir. Böylece belge, grafik ve testler aynı sayıyı gösterir.
4. **Sözleşme önce:** Python ↔ TS arasındaki tek sınır `SolveRequest` / `SolveResult` JSON'udur.

## 2. Core modülleri ve bağımlılık yönü (döngü yasak)
```
api
 ├─ parsing, bc ─────────────► sympy
 ├─ analytic ────────────────► parsing
 ├─ mesh ─ elements ─ quadrature
 ├─ element_matrices ────────► elements, quadrature
 ├─ assembly ────────────────► element_matrices, mesh
 ├─ boundary ────────────────► assembly
 ├─ solver
 ├─ errors, convergence ─────► elements, quadrature
 ├─ sampling ────────────────► elements
 └─ derivation ──────────────► (yalnızca SolveContext okur)
```
Basit bir test (`tests/test_layers.py`, `ast` ile import taraması) `derivation`'ın `assembly`, `solver` vb. modülleri çağırmadığını doğrular.

`SolveContext` (iç veri sınıfı): kanonik problem, dönüşüm adımları, ağ, eleman matrisleri (sembolik + sayısal), montaj kaydı,
BC öncesi/sonrası sistemler, Thomas ara değerleri, U, analitik çözüm ve türetme adımları, hatalar, oranlar, uyarılar.

## 3. Veri sözleşmesi

### SolveRequest
```jsonc
{
  "schemaVersion": "1.0",
  "mode": "equation" | "mms",
  "equation": "-((1+x)*u')' = 1",        // mode = equation
  "manufactured": { "u": "x^4", "p": "1", "q": "0", "r": "0" },   // mode = mms
  "exactSolution": null,                  // isteğe bağlı kullanıcı tam çözümü (doğrulanır)
  "domain": [0, 1],
  "bc": { "left": "u(0)=0", "right": "u(1)=1" },   // mms modunda BC tipi + değer otomatik
  "element": "P1" | "P2",
  "nValues": [2, 4, 8, 16, 32, 64],
  "derivationN": 2                        // belgede ayrıntılı gösterilecek ağ (≤ 8 önerilir)
}
```

### SolveResult
```jsonc
{
  "schemaVersion": "1.0",
  "status": "ok" | "rejected",
  "rejection": null | { "code": "NONLINEAR", "message": "...", "suggestion": "..." },
  "problem": {
    "canonical": { "p": "...", "q": "...", "r": "...", "f": "..." },        // SymPy srepr değil, okunur metin
    "latex": { "input": "...", "canonical": "...", "bcs": ["...", "..."] },
    "bcTypes": ["dirichlet", "robin"]
  },
  "exact": { "source": "sympy" | "mms" | "user" | "none", "latex": "...", "verified": true },
  "runs": [{
    "n": 8, "h": 0.125, "dofs": 9,
    "nodes": [...], "U": [...],
    "sample": { "x": [...], "uh": [...], "duh": [...], "u": [...], "err": [...] },
    "errors": { "L2": 0.0, "H1": 0.0, "maxNodal": 0.0, "L2rel": 0.0 },
    "matrix": [[...]] | null,                // yalnızca dofs ≤ 33
    "conditionNumber": 0.0
  }],
  "convergence": {
    "L2":       { "rates": [...], "theory": 2, "asymptotic": true, "machinePrecision": false },
    "H1":       { ... },
    "maxNodal": { ... }
  },
  "basis": { "n": 4, "x": [...], "phi": [[...]], "U": [...] },   // V3 için (n = derivationN)
  "derivation": { "steps": [ /* LATEX_STYLE §3 modeli */ ] },
  "latexDocument": "\\documentclass...",
  "warnings": [{ "code": "PECLET", "message": "...", "data": { "n": 8, "Pe": 1.25 } }]
}
```
- `analytic` yoksa (`exact.source = "none"`) `errors`, `convergence`, `sample.u`, `sample.err` alanları `null` olur ve arayüz kıyas göstermez.
- Şema: `core/src/fem1d/result.schema.json`; `schema.py` testlerde doğrular. TS tipleri `web/src/types.ts` elle tutulur;
  vitest, `web/tests/fixtures/*.json` (gerçek core çıktısı) üzerinden tiplerle uyumu kontrol eder.
- Boyut: örnekleme eleman başına P1 için 2, P2 için 9 nokta; koşu başına en fazla 2048 nokta.

## 4. Worker protokolü (`web/src/worker/`)
| Yön | Mesaj | İçerik |
|---|---|---|
| UI → W | `init` | — |
| W → UI | `progress` | `{ stage: "pyodide" \| "packages" \| "fem1d", pct }` |
| W → UI | `ready` | `{ version }` |
| UI → W | `preview` | `{ id, equation, bc }` → kanonik LaTeX veya reddetme (yazarken, 300 ms gecikmeli) |
| UI → W | `solve` | `{ id, request }` → `result` veya `error` |

Zaman aşımı: `preview` 3 s, `solve` 30 s. Aşımda worker sonlandırılır ve yeniden başlatılır; kullanıcıya anlaşılır mesaj gösterilir.

## 5. Web modülleri
| Klasör | Sorumluluk | Test |
|---|---|---|
| `worker/` | Pyodide yaşam döngüsü, RPC | e2e |
| `ui/` | Giriş paneli, hazır problemler, uyarılar, sekmeler | e2e |
| `viz/` | Her görsel: saf `buildTraces(result) → { data, layout }` + ince bileşen | vitest (saf kısım) |
| `doc/` | Türetme modeli → DOM (KaTeX), içindekiler, `.tex` indirme | vitest + e2e |
| `styles/` | Tasarım belirteçleri | — |

## 6. Sayfa düzeni
```
┌────────────────────────────────────────────────────────────────────┐
│ FEM1D Studio                                        tema · paylaş   │
├────────────────┬───────────────────────────────────────────────────┤
│ Giriş paneli   │  [3D Laboratuvar] [Yakınsama] [Matris] [Çözüm Belgesi] │
│ denklem + KaTeX│                                                   │
│ BC, P1/P2, n   │                                                   │
│ hazır problem  │                                                   │
│ [ Çöz ]        │                                                   │
└────────────────┴───────────────────────────────────────────────────┘
```
Not: Pyodide `file://` üzerinden çalışmaz; sayfa her zaman bir HTTP sunucusundan açılır (`make dev` veya `npx vite preview`).

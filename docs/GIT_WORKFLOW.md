# GIT_WORKFLOW.md — Git Akışı

## 1. Dal
Tek geliştirici, 7 gün: doğrudan `main` üzerinde çalışılır. Her adım küçük bir commit'tir ve push sonrası CI ile doğrulanır.
Modül sonunda etiket: `m0-done`, `m1-done`, …; teslimde `v1.0.0`.

## 2. Commit
- **Conventional Commits:** `feat`, `fix`, `test`, `docs`, `build`, `ci`, `refactor`, `chore`.
- Kapsamlar: `core`, `parser`, `analytic`, `analysis`, `derivation`, `latex`, `api`, `web`, `viz`, `doc`, `e2e`, `learning`, `research`, `fixtures`, `oracle`.
- Konu ≤ 72 karakter, İngilizce, emir kipi, nokta yok.
- Gövde zorunlu satırları:
  ```
  Step: M2.4
  Tests: test_assembly_b1_n2_exact, test_assembly_symmetry
  ```
  İsteğe bağlı: `Refs: docs/MATH_SPEC.md §2.3`, `Third-party: <repo> (<lisans>)`.
- PROGRESS.md güncellemesi aynı commit'e dahildir. Adımın commit'i `git log --grep "Step: M2.4"` ile bulunur.

## 3. Her adımın sonu
```bash
make check                               # kırmızıysa commit yok
git add -A && git diff --cached --stat   # kapsamı gözden geçir
git commit                               # Step: ve Tests: satırlarıyla
git push
gh run watch --exit-status "$(gh run list --branch main --limit 1 --json databaseId -q '.[0].databaseId')"
```
CI kırmızıysa düzeltme **yeni bir commit**tir (`fix(...)`). amend ve force-push yok.

## 4. Yasaklar (kullanıcı onayı olmadan)
`--no-verify`; `git push --force`; push edilmiş geçmişi değiştirmek; testleri silmek/`skip`/`xfail`; toleransı gevşetmek; kaynak dosyayı `.gitignore` ile gizlemek.

## 5. Git'e girmeyenler
`.venv/`, `node_modules/`, `dist/`, `web/public/*.whl`, `research/`, `*.pdf` (CI artefaktı olarak saklanır), `.env`.

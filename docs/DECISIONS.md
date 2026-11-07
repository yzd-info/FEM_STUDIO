# DECISIONS.md — Teknoloji Kararları (ADR)

Bu kararlar kabul edilmiştir. Değişiklik veya yeni karar: aşağıdaki şablonla "Önerildi" olarak yaz, kullanıcı onayıyla "Kabul edildi" yap.

```markdown
## ADR-NNN: <başlık>
- Durum: Önerildi · Tarih: · Adım:
- Bağlam:
- Seçenekler (en az 2, artı/eksi):
- Karar:
- Sonuçlar:
```

---

## ADR-001: Statik HTML + tarayıcıda Python (Pyodide)
- Durum: **Kabul edildi**
- Bağlam: Kullanıcı isteği: "HTML üzerinden çalışsın, uygulama değil". Sunucu yok. Matematik güvenilir ve test edilebilir olmalı.
- Seçenekler: (a) FEM'i TypeScript'te yazmak — SymPy eşdeğeri yok (dsolve, LaTeX yazıcısı, tam integral); (b) Python core + Pyodide; (c) Python sunucusu.
- Karar: (b). Aynı Python kodu hem pytest ile test edilir hem tarayıcıda çalışır.
- Sonuçlar: İlk açılış birkaç saniye sürer (yükleme ekranı). Yerel Python, Pyodide'in Python sürümüyle eşleşmeli. B planı: `pipeline.md` §10.

## ADR-002: Plotly.js
- Durum: **Kabul edildi**
- Gerekçe: 3D ve 2D bilimsel grafik, hover, kamera, PNG dışa aktarım hazır. Three.js tam kontrol verir ama 7 güne sığmaz.

## ADR-003: KaTeX + ortak makro seti
- Durum: **Kabul edildi**
- Gerekçe: Hızlı ve senkron. Kısıtlı komut seti, KaTeX ve pdflatex'in ikisinde de çalışan ortak bir alt küme kullanmaya zorlar.

## ADR-004: Dirichlet için eliminasyon (lifting)
- Durum: **Kabul edildi**
- Gerekçe: Simetriyi korur; ders kitaplarındaki el çözümüyle aynıdır. Satır değiştirme yöntemi kullanılmaz.

## ADR-005: Türkçe arayüz ve belge
- Durum: **Kabul edildi** · İngilizce: gelecek modül E9.

## ADR-006: scikit-fem bağımsız kâhin
- Durum: **Kabul edildi**
- Gerekçe: Kendi kodumuzu kendi kodumuzla test etmek döngüseldir. Yaygın kullanılan bağımsız bir FEM kütüphanesiyle düğüm değerlerinin aynı çıkması güçlü bir doğrulamadır. Yalnızca geliştirme bağımlılığıdır; tarayıcıya girmez.

## ADR-007: Kapsam dondurma (v1.0)
- Durum: **Kabul edildi** (kullanıcı: "çekirdekten başlayalım, A")
- Karar: `pipeline.md` §2. Diğer 1D FEM konuları §11'de gelecek modüller olarak planlıdır.

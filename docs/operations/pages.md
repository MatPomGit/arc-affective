# Dokumentacja MkDocs i publikowanie na GitHub Pages

## Architektura dokumentacji

- **Pliki źródłowe:** `docs/*.md` oraz `papers/P*.md`.
- **Główna konfiguracja:** `mkdocs.yml`, motyw Material for MkDocs.
- **Generator:** `scripts/sync_mkdocs.py` włącza istniejące protokoły `papers/` do witryny, przenosząc względne linki. Nie modyfikuje oryginałów.
- **Katalog przejściowy:** `docs/papers/` jest generowany i ignorowany przez Git.
- **Wynik:** `site/` jest generowany, ignorowany przez Git, a publikowany jako artefakt Pages.
- **Automatyzacja:** `.github/workflows/docs.yml`: test kompilacji na PR i wdrożenie po zmianach `main`.

!!! important "Status publikacji"
    Adres docelowy to `https://matpomgit.github.io/arc-affective/`, ale działa dopiero po wybraniu **GitHub Actions** jako źródła w ustawieniach Pages i po udanym wdrożeniu. Sam PR lub uruchomienie MkDocs nie dowodzi, że strona jest dostępna publicznie.

## Instalacja lokalna

Wymagane Python 3.11+ (zalecany 3.12) i Git:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-docs.txt
python scripts/sync_mkdocs.py
python -m unittest discover -s tests -p "test_docs.py" -v
mkdocs build --strict
mkdocs serve
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-docs.txt
python scripts/sync_mkdocs.py
python -m unittest discover -s tests -p test_docs.py -v
mkdocs build --strict
mkdocs serve
```

Podgląd lokalny: `http://127.0.0.1:8000/`.

## Pierwsze uruchomienie GitHub Pages

1. Otwórz [ustawienia Pages repozytorium](https://github.com/MatPomGit/arc-affective/settings/pages).
2. W sekcji **Build and deployment** ustaw **Source → GitHub Actions**.
3. Na zakładce [Actions](https://github.com/MatPomGit/arc-affective/actions) uruchom workflow **Docs / MkDocs → Run workflow** na `main` lub opublikuj zmianę dokumentacji.
4. Sprawdź wynik zadania `deploy` i adres `https://matpomgit.github.io/arc-affective/`.
5. W razie potrzeby ustaw ochronę środowiska `github-pages`, ograniczając wdrożenia do `main`.

Źródła: [GitHub Pages z własnym workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site); [MkDocs — deployment](https://www.mkdocs.org/user-guide/deploying-your-docs/).

## Polityka bezkosztowa i bezpieczeństwo

Repozytorium jest publiczne, a **standardowe runnery GitHub-hosted są bezpłatne w repozytoriach publicznych**. Workflow nie korzysta z płatnych modeli, specjalnych runnerów ani sekretów. Praca na PR ma wyłącznie uprawnienia odczytu; publikacja na `main` uzyskuje `pages: write` i `id-token: write`.

Nie przenoś tej konfiguracji bez audytu do prywatnego repozytorium ani na płatny większy runner. Nie publikuj nagrań biometrycznych, danych uczestników ani nieautoryzowanych zbiorów.

**Utrzymanie zależności:** `mkdocs-material==9.8.0` jest wersją bezpieczeństwa, a projekt znajduje się w trybie utrzymania. Zweryfikuj wsparcie i ewentualną migrację przed końcem wsparcia upstream w 2027 r.

## Edycja treści

1. Zmieniaj protokoły **wyłącznie** w `papers/Pxx-*.md`, nigdy ręcznie w `docs/papers/`.
2. Zmieniaj pozostałe dokumenty bezpośrednio w `docs/`.
3. Aktualizując nawigację, edytuj `mkdocs.yml`; przy zmianach nazw plików aktualizuj `scripts/sync_mkdocs.py`.
4. Przed PR uruchom generator, testy i `mkdocs build --strict`. Nie commituj `site/` ani `docs/papers/`.

Workflow Pages uruchamia się na `main` oraz kontroluje kompilację zmian w PR. Nie uruchamia eksperymentów, sensorów ani obliczeń badawczych.

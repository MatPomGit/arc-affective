# Polityka publicznej strony ARC Affective

Dokumentacja `docs/` służy wewnętrznej pracy naukowej i technicznej. **Publiczna witryna korzysta wyłącznie z osobnego `pages/`** oraz `mkdocs.public.yml`. Główne `mkdocs.yml` zachowuje dotychczasowy, niepublikowany build dokumentacji na potrzeby kontroli poprawności.

`config/pages-policy.json` wskazuje dokładnie zatwierdzone pliki publiczne. Kontrola `scripts/validate_public_pages.py` odrzuca niezatwierdzone pliki, symlinki, ścieżki wychodzące z katalogu, instrukcje agentów i notatki redakcyjne. Dodatkowo wymagana jest niezależna ocena wyrenderowanego HTML, obrazów, metadanych i licencji.

Nie publikuj dokumentacji `docs/development/`, `docs/operations/contributing.md`, planów issue, wewnętrznych procedur, prywatnych informacji o urządzeniach, danych uczestników i niezakończonych analiz. Opis witryny ma być neutralny i skierowany do odbiorcy zewnętrznego.

**Prywatne repo nie gwarantuje prywatnej strony Pages.** Wszelka publikacja wymaga osobnej decyzji właściciela i oceny faktycznej widoczności. Nie jest dozwolona publikacja z `main:/docs` ani root repo. Dotychczasowy automatyczny deploy zostaje zastąpiony generowaniem artefaktu do ręcznego przeglądu, bez `deploy-pages`.

# ARC Affective: historia przeniesienia manuskryptów

Osiem źródłowych projektów zachowuje identyfikatory i historyczny snapshot `0ff5f1531f03270c4f9fdcc7f3af6d2e9aca85dd`. [Manifest](affective_to_arc.json) zawiera pierwotne ścieżki i identyfikatory Git blob; kopie źródłowe pozostają w tym repozytorium.

| MSC | Program | Stan źródeł |
| --- | --- | --- |
| MSC-AFFECT-P01 | [arc-ai](https://github.com/MatPomGit/arc-ai) | [TARGET_MANUSCRIPT_INTEGRATED_CODE_PENDING](https://github.com/MatPomGit/arc-ai/pull/1) |
| MSC-AFFECT-P02 | [arc-ai](https://github.com/MatPomGit/arc-ai) | [TARGET_MANUSCRIPT_INTEGRATED_CODE_PENDING](https://github.com/MatPomGit/arc-ai/pull/1) |
| MSC-AFFECT-P03 | [arc-ai](https://github.com/MatPomGit/arc-ai) | [TARGET_MANUSCRIPT_INTEGRATED_CODE_PENDING](https://github.com/MatPomGit/arc-ai/pull/1) |
| MSC-AFFECT-P04 | [arc-ai](https://github.com/MatPomGit/arc-ai) | [TARGET_MANUSCRIPT_INTEGRATED_CODE_PENDING](https://github.com/MatPomGit/arc-ai/pull/1) |
| MSC-AFFECT-P05 | [arc-neuro](https://github.com/MatPomGit/arc-neuro) | [TARGET_PLAN_INTEGRATED](https://github.com/MatPomGit/arc-neuro/pull/10) |
| MSC-AFFECT-P06 | [arc-ai](https://github.com/MatPomGit/arc-ai) | [TARGET_MANUSCRIPT_INTEGRATED_CODE_PENDING](https://github.com/MatPomGit/arc-ai/pull/1) |
| MSC-AFFECT-P07 | [arc-robo](https://github.com/MatPomGit/arc-robo) | [TARGET_PLAN_INTEGRATED](https://github.com/MatPomGit/arc-robo/pull/2) |
| MSC-AFFECT-P08 | [arc-ai](https://github.com/MatPomGit/arc-ai) | [TARGET_MANUSCRIPT_INTEGRATED_CODE_PENDING](https://github.com/MatPomGit/arc-ai/pull/1) |

## Zakres utrwalony w programach

Sześć prac `P01–P04/P06/P08` otrzymało własne katalogi źródeł LaTeX i planów w [ARC AI](https://github.com/MatPomGit/arc-ai/tree/main/manuscripts). Oryginalne szkice IEEEtran P01 i P08, ich sekcje, bibliografie i protokoły przeniesiono w postaci niezmienionych kopii do podkatalogów `original/`. [PR #1](https://github.com/MatPomGit/arc-ai/pull/1) przeszedł CI i został scalony jako `7877b57a2cb7b8bb6923db9f376e14ce191922b2`. W programie zarejestrowano także odrębne koncepcje badawcze, bez deklarowanych wyników.

Plan P05 znajduje się w [ARC Neuro](https://github.com/MatPomGit/arc-neuro/tree/main/papers/affect/MSC-AFFECT-P05), a P07 w [ARC Robo](https://github.com/MatPomGit/arc-robo/tree/main/manuscripts/MSC-AFFECT-P07). Obydwa odpowiednie PR źródłowe są scalone.

## Niezmieniony obszar odpowiedzialności

Kod pomiarowy, testy Python, raporty QC i inżynieria danych P01/P08 **nadal pozostają w ARC Affective**. Przeniesienie artykułu nie potwierdza migracji zależności wykonawczych ani eksperymentów na danych rzeczywistych. Prawa do zbiorów danych, warunki licencji źródeł i protokoły eksperymentalne zachowują wymagane bramki; bez badań nie zgłasza się wyników.

Kod i dokumenty zachowują oryginalną licencję Apache-2.0, odtwarzalność po SHA i nieprzerwaną historię Git. Pozostaje oddzielna decyzja, czy i kiedy przenieść moduły implementacyjne do aplikacji lub biblioteki. Archiwizacja tego repozytorium wymaga osobnej zgody i nie jest częścią obecnego przekazania.

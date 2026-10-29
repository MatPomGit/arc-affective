# Zasady pracy nad projektem

Dokumentacja i kod są rozwijane przez małe, weryfikowalne zmiany w PR. Każda publikacja ma issue nadrzędne i siedem etapów M0–M6.

## Praca z issues

- Wybierz etap z [rejestru 56 issues](../publication-milestones.md).
- Zrealizuj pojedynczą, mierzalną jednostkę pracy JRA (kod, testy, wyniki lub raport).
- Sprawdź zależności w [DAG projektu](../research-dependencies.md).
- Udokumentuj warunki akceptacji, polecenia testowe, artefakty i dokładny SHA.
- Zamknij issue dopiero po zrealizowaniu bramki, nie po stworzeniu planu.

Szczegóły: [standard realizacji JRA](../issue-operating-procedure.md).

## Kodeks danych i pomiarów

- Dane biometryczne i restrykcyjne zbiory benchmarkowe nie trafiają do Git ani publicznej witryny.
- Tobii Eye Tracker 5 nie służy do nieautoryzowanego rejestrowania spojrzenia; dostęp do Muse Athena wymaga potwierdzenia praw.
- Każde badanie z udziałem ludzi przechodzi właściwą ocenę etyczną i ochrony danych, również N=1.
- Modele nie uprawniają do diagnozy klinicznej ani nieobwarowanego wnioskowania o emocjach.

## Dokumentacja i automatyzacja

[Zasady techniczne MkDocs](pages.md) określają test `mkdocs build --strict`, generowanie kart publikacji i publikację GitHub Pages.

Źródło instrukcji dla agentów: [AGENTS.md](https://github.com/MatPomGit/arc-affective/blob/main/AGENTS.md).

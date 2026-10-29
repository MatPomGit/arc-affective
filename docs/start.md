# Jak korzystać z projektu

Dokumentacja jest przeznaczona dla badaczy, programistów i agentów AI realizujących prace w repozytorium `arc-affective`.

## 1. Wybierz publikację i bramkę

1. Sprawdź [portfolio i unikalny wkład](portfolio.md).
2. Otwórz [protokoły P01–P08](papers/index.md).
3. Znajdź aktualne zadania M0–M6 w [rejestrze kamieni milowych](publication-milestones.md).
4. Sprawdź [zależności i blokery](research-dependencies.md) oraz [warunki etyczne](governance.md).

Nie uznawaj etapu za zakończony bez dowodów: kodu, protokołu, wyników testów, metryk i linku do PR.

## 2. Rozpocznij od niezależnych ścieżek

| Ścieżka | Co można zrobić bez uczestników | Bramka krytyczna |
| --- | --- | --- |
| P08 · Edge | Generator zdarzeń, replay, profilowanie CPU | Rzeczywiste pomiary opóźnienia |
| P01 · EEG | Przegląd literatury, audit splitów i montażu elektrod | Legalnie dostępne zbiory EEG |
| P04 · RGB | Projekt buforów i testy prywatności z danymi syntetycznymi | Prawa do zbioru referencyjnego |
| P07 · robot | Symulacja ROS 2/Gazebo, scenariusze testowe | Niezależny nadzorca bezpieczeństwa |

## 3. Sprawdź repozytorium lokalnie

W katalogu repozytorium:

```bash
python -m unittest discover -s tests -v
PYTHONPATH=src python -m arc_affective.cli --events 100 --output data/synthetic-demo.jsonl
```

To jedynie test zdarzeń syntetycznych. Nie mierzy stanu afektywnego.

## 4. Dokumentacja i GitHub Pages

Instrukcje uruchomienia, aktualizacji i publikacji: [MkDocs i GitHub Pages](operations/pages.md). Zasady pracy: [wkład w projekt](operations/contributing.md).

!!! warning "N=1 nie oznacza walidacji populacyjnej"
    Eksperymenty własne z udziałem maksymalnie trzech pracowników uczelni mają charakter wewnątrzosobniczy lub techniczny. Wnioskowanie międzypodmiotowe wymaga odpowiednich, legalnie dostępnych zbiorów danych.

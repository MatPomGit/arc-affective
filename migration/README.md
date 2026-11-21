# ARC Affective — etapowa migracja właścicieli prac naukowych

**Snapshot źródłowy:** `0ff5f1531f03270c4f9fdcc7f3af6d2e9aca85dd` (21 listopada 2026). **Rejestr centralny:** `research-autopilot@84fd9acb0a9ec36d1585da0471f1516eb61339f9`. **Format:** [wersjonowany manifest](affective_to_arc.json). Przenosimy odpowiedzialność za zakres i prospektywne plany badań, nie fikcyjne wyniki ani rzekomo gotowy kod pomiarowy.

| Manuskrypt | Nowy właściciel | Stan operacji | Dowód |
| --- | --- | --- | --- |
| MSC-AFFECT-P01 | `arc-ai` | `BLOCKED_TARGET_REPOSITORY_ABSENT` | Repozytorium `MatPomGit/arc-ai` nie istnieje |
| MSC-AFFECT-P02 | `arc-ai` | `BLOCKED_TARGET_REPOSITORY_ABSENT` | Repozytorium `MatPomGit/arc-ai` nie istnieje |
| MSC-AFFECT-P03 | `arc-ai` | `BLOCKED_TARGET_REPOSITORY_ABSENT` | Repozytorium `MatPomGit/arc-ai` nie istnieje |
| MSC-AFFECT-P04 | `arc-ai` | `BLOCKED_TARGET_REPOSITORY_ABSENT` | Repozytorium `MatPomGit/arc-ai` nie istnieje |
| MSC-AFFECT-P05 | `arc-neuro` | `STAGED_IN_OPEN_PR` | [PR](https://github.com/MatPomGit/arc-neuro/pull/10) |
| MSC-AFFECT-P06 | `arc-ai` | `BLOCKED_TARGET_REPOSITORY_ABSENT` | Repozytorium `MatPomGit/arc-ai` nie istnieje |
| MSC-AFFECT-P07 | `arc-robo` | `STAGED_IN_OPEN_PR` | [PR](https://github.com/MatPomGit/arc-robo/pull/2) |
| MSC-AFFECT-P08 | `arc-ai` | `BLOCKED_TARGET_REPOSITORY_ABSENT` | Repozytorium `MatPomGit/arc-ai` nie istnieje |

## Zakres przeniesienia

**P05**: skopiowano merytoryczny plan wraz z założeniami, punktami końcowymi i oryginalnym odwołaniem do metodyki. W `arc-neuro` trafia do `research/affective/MSC-AFFECT-P05/`, **poza** 63 neutralnymi slotami `papers/` i poza publiczną stroną.

**P07**: import planu do istniejącego PR ARC Robo obok `manuscripts/MSC-AFFECT-P07/main.tex`. System ROS2/Gazebo i deterministyczny governor pozostają **projektem**, nie uruchomiono robota ani nie zatwierdzono pracy na sprzęcie fizycznym.

**P01–P04, P06, P08**: **BLOCKED**, bo nowe `arc-ai` nie istnieje. P01 i P08 mają działające szkielety IEEEtran, moduły `src/arc_affective/`, testy i raporty QC, więc przeniesienie wyłącznie pliku `plan.md` byłoby utratą możliwości reprodukcji. Spis plików z ich SHA i powiązaniami utrwala `software_inventory` w manifeście. Obecne repozytorium pozostaje źródłem wykonawczym do czasu zakończonego przeniesienia i testów w repozytorium docelowym.

**XR i współdzielone metody:** projekty interfejsów XR i gry adaptacyjnej nie są automatycznie kopiowane do `arc-xr`; migracja dotyczy właściciela pierwszorzędowego pytania, a interfejs jest zależnością. Kod wspólny `events.py`, `synthetic.py` i raporty QC powinny zachować wspólną bazę testową przy ewentualnej przyszłej separacji LIB/APP. Szczegóły aparatury należą do prywatnego rejestru urządzeń; identyfikatorów ani danych uczestników nie przenosić do publicznych repozytoriów.

**Licencje:** planowane źródła są objęte licencją `Apache-2.0` w pierwotnym repozytorium. Przy imporcie P05/P07 skopiowano pełną licencję `ORIGINAL_LICENSE` i zapisano źródłowy blob; nowe repozytoria nie zmieniają automatycznie praw do materiałów. Ostateczne przeniesienie P01/P08 musi także zachować licencję kodu i zależności.

**Zadanie kontynuacji:** [Research Autopilot #489](https://github.com/MatPomGit/research-autopilot/issues/489) — utworzenie docelowego `arc-ai` i pełna migracja sześciu prac z testami.

## Kryteria zamknięcia

1. **Provisioning:** istniejące docelowe repo i uprawnienia, zweryfikowany target SHA; bez przenoszenia do fikcyjnego `arc-ai`.
2. **Integralność:** lista wszystkich plików i Git blob SHA ze snapshotu, odnośniki względne i licence; brak zgubionych planów, bibliografii i warunków etycznych.
3. **Sprawność:** migracja P01/P08 z zależnościami `src/`, `tests/`, `reports/`, `pyproject.toml`, pełny Python CI, oddzielna kompilacja LaTeX; kontrola no-leakage i rzeczywistych danych, nie deklarowane sukcesy.
4. **Handover:** nowe miejsca źródłowe wskazane w rejestrze, zidentyfikowany kanoniczny właściciel i status; odnośniki ze starych dokumentów przekierowane po scaleniu PR docelowych.
5. **Archival:** stary repozytorium zachowuje historię i Issues. Przejście do read-only dopiero po potwierdzeniu wszystkich 8 źródeł, kontroli Pages, dokładnego SHA oraz osobnym zatwierdzeniu archiwizacji. Żadnych zmian na stronach publicznych w tym etapie.

## Status

**Migracja częściowo przygotowana**, nie zakończona: P05/P07 oczekują scalenia i kontroli docelowej, a sześć pozostałych prac oczekuje repozytorium AI. Brak przeniesienia danych, wyników pomiarowych i kodu fizycznej akwizycji.

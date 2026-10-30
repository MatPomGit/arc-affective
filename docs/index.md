# ARC Affective

**Multimodalne monitorowanie stanu afektywnego i poznawczego człowieka**

Program badań inżynierskich obejmujący analizę EEG, komputerowe przetwarzanie obrazu, kinematykę dłoni, fuzję danych, adaptację gier, robotykę oraz systemy Edge AI.

[Przegląd publikacji](papers/index.md){ .md-button .md-button--primary }
[Plan prac i issues](publication-milestones.md){ .md-button }

!!! info "Status projektu"
    Dokumentacja opisuje **osiem planowanych publikacji**, ich protokoły, zależności i warunki dopuszczenia do badań. Nie jest raportem o przeprowadzonych eksperymentach ani o potwierdzonej skuteczności modeli.

## Obszary badań

| Obszar | Publikacje | Główne zagadnienie |
| --- | --- | --- |
| Przetwarzanie sygnałów i AI | [P01](papers/P01-low-channel-transfer.md), [P02](papers/P02-robust-fusion.md) | Generalizacja EEG, niezawodność fuzji i kalibracja |
| Interakcja człowiek–komputer | [P03](papers/P03-personal-drift.md), [P04](papers/P04-private-vision.md), [P05](papers/P05-hand-workload.md) | Zmiany w czasie, wzorce zachowania i prywatność |
| Systemy adaptacyjne i robotyka | [P06](papers/P06-adaptive-game.md), [P07](papers/P07-safe-hri.md) | Sterowanie sprzężeniem zwrotnym, nadzór bezpieczeństwa |
| Architektury obliczeniowe | [P08](papers/P08-edge-systems.md) | Opóźnienia, utrata sygnału i obliczenia brzegowe |

## Dostępna aparatura

- **Tobii Eye Tracker 5:** widoczny pod monitorem; producent podaje zasięg 45–95 cm, 40° × 40° i obrazowanie 133 Hz (nominalne aktualizacje spojrzenia 33 Hz). Licencja konsumencka **nie pozwala na badawcze rejestrowanie danych eye-trackingu**.
- **Muse S Athena:** potencjalne EEG i sygnały optyczne, ale dostęp do surowych strumieni badawczych pozostaje niepotwierdzony.
- **Ultraleap Leap Motion Controller 2:** zidentyfikowany sprzęt do stereowizyjnego śledzenia dłoni (IR 850 nm, zasięg 10–110 cm, FoV maks. 160° × 160°, kamery do 120 FPS). Integracja Hyperion/LeapC i uprawnienia do rejestracji danych nadal wymagają weryfikacji. Pełna [specyfikacja i bramki uruchomieniowe](hardware.md).
- **Kamery RGB:** lokalna analiza cech obrazu, preferencyjnie bez zapisywania klatek.
- **Slayo Mike S9 (2 szt., jeden odbiornik USB-C):** opcjonalna analiza zdarzeń dźwiękowych i toru lewy/prawy po sprawdzeniu, czy odbiornik rzeczywiście udostępnia **dwa rozdzielne kanały**. Bez tego nie wolno deklarować nagrań stereo ani lokalizacji przestrzennej. [Procedura weryfikacji](hardware.md).

[Weryfikacja aparatury i licencji](hardware.md) · [Metodologia](methodology.md) · [Ochrona danych](governance.md)

## Organizacja programu

Każdy artykuł przechodzi **M0–M6**, od analizy literatury i wykonalności do niezależnej walidacji oraz manuskryptu. Wszystkie zadania i warunki zamknięcia są dostępne przez [rejestr issues](publication-milestones.md).

[Mapa zależności](research-dependencies.md) · [Harmonogram warunkowy](research-schedule.md) · [Pierwsze kroki](start.md)

<small>Repozytorium: [MatPomGit/arc-affective](https://github.com/MatPomGit/arc-affective). Badania własne N ≤ 3, preferowane N=0–1. Zero płatnych API i usług wymaganych do uruchomienia.</small>

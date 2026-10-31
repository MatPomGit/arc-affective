# Uzupełniający cykl pracy agentów ARC Affective

**Wersja:** 1.0.0 (2026-10-31). Odczytaj także root `AGENTS.md` i [procedurę Issues](../issue-operating-procedure.md); niniejszy dokument nie zastępuje ich warunków.

## Rozpoznanie i dobór zadania
Sprawdź źródłowy main, aktualne Issues, milestone, PR, właściciela, rezerwacje i stan z dowodami. Najpierw zamykaj naprawy i istniejące PR. DoR: cel, wynik, zależności, kryteria, prawa do danych, potrzebne zasoby i bramki naukowe. Wybierz jeden JUMP i odnotuj rezerwację w istniejącym kontrolerze Research Autopilot. Nie zakładaj dodatkowego schedulera. Limit: jeden feature PR na repozytorium i pięć w zarządzanym portfolio.

Przed użyciem skilli zweryfikuj pochodzenie, wersję, uprawnienia, warunki uruchomienia i wykluczenia. Nie wykonuj niezaufanego kodu na trwałych runnerach i nie uruchamiaj płatnych usług. Różne narzędzia nie mogą nadawać sobie wzajemnie uprawnień.

## Implementacja, badania i dane
Stosuj KISS, DRY, YAGNI, jedno źródło prawdy, niewielki diff, odpowiednie PEP 8/20/257/484 i projektowe narzędzia. Nie dodawaj powielonych konfiguracji. Przed badaniami czytaj docs/governance.md i docs/datasets.md; przed publikacją docs/portfolio.md i docs/research-dependencies.md. Projekt inżynierski nie jest kliniczną diagnostyką ani odczytywaniem emocji. Uczestnicy, dostęp do danych i uprawnienia muszą być zgodne z zatwierdzonym protokołem. Dokumentuj pochodzenie, wersje modeli i danych, seeds, podziały bez przecieku, wyniki negatywne, niepewność i ograniczenia. Nie fabrykuj wyników i źródeł.

## Walidacja, PR i zakończenie
Uruchom odpowiednie istniejące testy na exact SHA. Rejestruj komendy, wersje środowiska i status PASS/FAIL/BLOCKED/UNAVAILABLE/NOT_RUN. Składnia, symulacja i dobry wynik CI nie dowodzą naukowej skuteczności. Sprawdź wymagane GitHub checks i niezależną recenzję. Komentarz z tego samego konta nie jest formalnym GitHub approval. Po zmianie HEAD ponów walidację.

DoD: kryteria spełnione, testy i dokumenty aktualne, Issue uzupełnione, PR scalony po bramkach, oddzielnie potwierdzony deployment Pages/aplikacji jeśli dotyczy, usunięta tylko własna scalona gałąź/worktree. Nie usuwaj źródeł i negatywnych wyników badań. W razie blokady podaj exit condition i następny bezpieczny krok.

Teksty użytkowe: poprawna polszczyzna, zdaniowe nagłówki, bez U+2013/U+2014 poza cytatami/danymi. Materiały dydaktyczne: polecenia konkretne, cztery wiarygodne odpowiedzi, klucz prowadzącego oddzielony.

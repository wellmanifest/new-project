# Audyt migracji research

## Cel audytu

Celem audytu bylo sprawdzenie, czy historyczne foldery badawcze zostaly przeniesione do `research/` bez utraty zawartosci. Stare foldery nie byly przywracane.

Audyt porownal usuniete pliki widoczne w Git z ich odpowiednikami w `research/` przez porownanie Git blob ID:

- stara zawartosc: `git rev-parse HEAD:<stara-sciezka>`,
- nowa zawartosc: `git hash-object <nowa-sciezka>`.

Wynik `OK` oznacza zgodnosc bajtowa zawartosci.

## Wynik porownania

| Status | Stara sciezka | Nowa sciezka |
| --- | --- | --- |
| OK | `GPT56Luna/ANALIZA-DOKUMENTACJI.md` | `research/GPT56Luna/ANALIZA-DOKUMENTACJI.md` |
| OK | `GPT56Luna/CONTRIBUTING.md` | `research/GPT56Luna/CONTRIBUTING.md` |
| OK | `GPT56Luna/NOTATKI-PRACY.md` | `research/GPT56Luna/NOTATKI-PRACY.md` |
| OK | `GPT56Luna/POLICY.md` | `research/GPT56Luna/POLICY.md` |
| OK | `GPT56Luna/Prompt.txt` | `research/GPT56Luna/Prompt.txt` |
| OK | `Opus48Medium/CONTRIBUTING.final.md` | `research/Opus48Medium/CONTRIBUTING.final.md` |
| OK | `Opus48Medium/CONTRIBUTING.md` | `research/Opus48Medium/CONTRIBUTING.md` |
| OK | `Opus48Medium/POLICY.md` | `research/Opus48Medium/POLICY.md` |
| OK | `Opus48Medium/Prompt.txt` | `research/Opus48Medium/Prompt.txt` |
| OK | `Opus48Medium/analiza-contributing.md` | `research/Opus48Medium/analiza-contributing.md` |
| OK | `SWE17/CONTRIBUTING.md` | `research/SWE17/CONTRIBUTING.md` |
| OK | `SWE17/POLICY.md` | `research/SWE17/POLICY.md` |
| OK | `SWE17/Prompt.txt` | `research/SWE17/Prompt.txt` |
| OK | `perplexity/Prompt.txt` | `research/perplexity/22.07/Prompt.txt` |
| OK | `perplexity/dobra a co z plikiem CONTRIBUTING czy ona moze byc.md` | `research/perplexity/22.07/dobra a co z plikiem CONTRIBUTING czy ona moze byc.md` |
| OK | `perplexity/przeanalizuj te pliki i daj infomracje jakie sa ro.md` | `research/perplexity/22.07/przeanalizuj te pliki i daj infomracje jakie sa ro.md` |
| OK | `perplexity/tu masz informacje z readme powiedz mi jaki format.md` | `research/perplexity/22.07/tu masz informacje z readme powiedz mi jaki format.md` |
| OK | `perplexity/wygeneruj.md` | `research/perplexity/22.07/wygeneruj.md` |

## Nowe materialy zachowane w research

W `research/` znajduja sie tez nowe materialy, ktore nie sa odpowiednikami usunietych plikow z HEAD:

- `research/perplexity/23.07/prompt1.txt`
- `research/perplexity/23.07/Bazując na opisanym celu projektu i wypracowanym p.md`

Te pliki sa zachowane jako dodatkowy material badawczy.

## Wniosek

Wszystkie 18 usunietych plikow historycznych ma odpowiednik w `research/`, a zawartosc kazdego odpowiednika jest bajtowo zgodna z wersja z HEAD. Nie wykryto utraty zawartosci podczas migracji.

Repozytorium nadal wymaga osobnego uporzadkowania stanu Git, poniewaz migracja jest widoczna jako zestaw usuniec starych sciezek i nowych plikow w `research/`. Ten audyt nie przywraca starych folderow i nie rozstrzyga jeszcze calego roboczego stanu repozytorium.

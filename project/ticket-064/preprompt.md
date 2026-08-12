# Preprompt: ticket-064

Napraw wykryty w rzeczywistym fleet audit edge case unborn Git HEAD. Zachowaj
read-only charakter checkera, rozróżnij poprawny stan initial od uszkodzenia,
dodaj regresję pustego primary i duplicate clone oraz nie osłabiaj pozostałych
błędów Git. Użyj LLM-first todo2code bez deterministycznego substytutu i
niezależnego exact-head Validatora przed merge.

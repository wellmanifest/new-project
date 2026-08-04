# Preprompt techniczny (ticket-012)

- Fixture nie może zależeć od ruchomego brancha ani sieci w trakcie testu.
- Użyj dwóch pełnych SHA zapisanych jako jawne dane testowe.
- Rollback ma być niedestrukcyjny i sprawdzony hashami.

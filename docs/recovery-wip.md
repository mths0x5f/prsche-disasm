# Сохранённая незавершённая работа

2026-10-15: untracked исходники, probes, verifiers и отчёты сохранены по просьбе
пользователя. Это сохранение работы, не production-интеграция.

- 111: исторические отчёты; общие зависимости частично обновлены позже.
- 131: изолированный audio-init packet, интеграция ещё открыта.
- 172/174/175: formatter search, network RTTI и stdio; очередь интеграции176 остаётся.
- 200: семь float4 extern views, один COFF00485100 с известными FP/raw32 conversion gaps.
  Он исключён из проверенного общего архива1072.
- 201: read-only triage109 отсутствующих тел; скрипт и summary сохранены.
  25 TUs подходят для отдельного declaration pilot; успешная сборка не доказана.
- 202: readonly exporter/wrapper и успешный capture одной00485100 сохранены.
  Capture: local/experiments/v2-float-bits-202/export. Original Ghidra project неизменён.
  Lowering9 raw32 stores/8 bitviews и native fixture не завершены из-за лимита агента.

Следующий шаг: продолжить202 по capture без повторного экспорта;200 не подключать
к игре до исправления известных conversion gaps. Старые отчёты не считаются свежими проверками.

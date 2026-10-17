# Сохранённая незавершённая работа

2026-10-17: незавершённый278/280 сохранён отдельно от проверенных пакетов.
- `scripts/research/audit-v2-native-union-280.py`, `native-replacements-280.py`,
  `native-platform-contract-280.py`: scaffold identity-pinned caller replacements
  и одного cdecl SetLastError bridge. Только syntax check; не выполнялись,
  replacement/native receipts отсутствуют, game/archive не изменены.
- Four raw callers568ae0/b10/b50/b90 всё ещё имеют char handle_device595d0
  declaration. Исправление, fixture282 и physical gap281 не были начаты.
- До использования280 нужны bounded negative guards, реальные replacement
  metadata/COFF и ABI native comparison. Действующий collector —268.
- Приоритет сдвинут к normal-entry285; этот прототип не закрывает595d0hold.


2026-10-15: untracked исходники, probes, verifiers и отчёты сохранены по просьбе
пользователя. Это сохранение работы, не production-интеграция.

- 111: исторические отчёты; общие зависимости частично обновлены позже.
- 131: изолированный audio-init packet, интеграция ещё открыта.
- 172/174/175: formatter search, network RTTI и stdio; очередь интеграции176 остаётся.
- 200: семь float4 extern views; небезопасный COFF00485100 с FP/raw32 conversion gaps
  исключён из union. Исправленный candidate получен в202 и включён в206.
- 201: historical read-only triage109 отсутствующих тел. Declaration pilot203 дал
  21/25 actual COFF;4pointer-call failures остаются. Frontier206 теперь97missing bodies.
- 202: завершены9raw32 stores/8bitviews,97original instructions и1024nativebitcases PASS.
  Capture: local/experiments/v2-float-bits-202/export; Original Ghidra project неизменён.
  Полное тело/x87/caller register equivalence отложены в validation backlog.
- 203–206: законченный compile-candidate checkpoint,1094native objects; production
  integration и запуск игры не выполнены. Не путать с сохранёнными историческими WIP.

Следующий шаг: original pointer-call consumers четырёх failures203 и зависимости206;
старые отчёты111/131/172/174/175 не считаются свежими проверками.

2026-10-15 checkpoint216:207–214 candidate packets and215/216 archives completed,
1108distinctfunctionVAs. Soundoutvalue214 fixed/fixturechecked; fullprovider and
native storage/ABI binding remainbacklog. Original production173 remainsunchanged.

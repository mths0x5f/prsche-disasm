# Run268 — exact existing Win32 providers and a strict support boundary

One native support object reuses the two existing `platform_enter_critical_section`
and `platform_leave_critical_section` bodies from `source/platform/win32_core.cpp`.
Exact source fragments, actual compiler/dependency closure and COFFs are pinned.
Both stdcall adapters call the original SDK imports named by the corrected index
and Run263: Porsche.exe IAT005b2078 /005b206c, KERNEL32 Enter/LeaveCriticalSection.
No game algorithm or original function VA is added; platform code counts as support.

One `/MP6` compile of two TUs passed with zero warnings. A native fixture linked
the real SDK providers and passed 64 recursive lock cycles /256 provider calls,
including recursion counts before and after release. This proves valid recursive
operations for the two adapters; contention, faults and game behavior remain open.
Receipts `compile-001`, `link-001`, `native-001` were saved before assertions;
none was overwritten or retried. Independent audit:204pins and8negative guards PASS.

The new frozen collector `audit-v2-native-union-268.py` preserves Run241 and adds
`native-platform-provider` support. It requires exact native definitions/imports,
source fragments from the platform directory, and declared stdcall provider names.
Data and alias objects must have no executable COFF sections. Namespaced data
definitions are allowed with the same non-code restriction. Provider code cannot
masquerade as original function counts or inferred game implementations.

```powershell
py -3 scripts/research/audit-v2-native-platform-268.py
```

Actual inputs, commands and closure checks: [summary.json](summary.json) and
[validation.json](validation.json). Native artifacts remain under
`local/experiments/v2-native-platform-providers-268/`. The original heap table
provider and full game EXE remain absent.

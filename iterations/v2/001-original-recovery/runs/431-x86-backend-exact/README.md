# Run 431: x86 lowering backend, exact against hardware

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

`scripts/research/x86-cpp-backend-exact.py` derives from the frozen
`x86-cpp-backend-fpu.py` and checks its SHA (`651faf47…`). The frozen file stays untouched,
because existing validations pin its hash. The new module fixes what the hardware oracles of the
`feat/lowered-whole-game` branch (Run 430) found, in portable C++ with no inline assembly.

## Fixes

Flags:
- **PF and AF**: no helper computed them. Now PF is the parity of the result's low byte for
  every flag-writing helper. AF is the carry or borrow out of bit 3 for
  add/adc/sub/sbb/cmp/neg/inc/dec, and 0 for logical operations and shifts.
- **MUL/IMUL**: the flags Intel leaves undefined follow the target CPU. SF comes from the sign
  and PF from the parity of the (low) result; ZF and AF are cleared.
- **Shifts and rotates** (`shl/shr/sar/rol/ror/rcl/rcr/shld/shrd`): measured on the target CPU
  for every width, every count 0..31, and both the immediate and the CL form, then written as
  rules (`local/experiments/shift-probe`, about 100k samples):
  - A zero masked count changes nothing.
  - Otherwise OF is the OF of the **first single-bit step**. The one exception is ROL/ROR with
    an **immediate** count above 1, which keeps OF. The CL form follows the first-step rule.
  - Shifts set CF to the last bit out, set SF/ZF/PF from the result, and clear AF.
  - Rotates change only CF and OF. RCL/RCR change nothing when the count is a multiple of
    width + 1.
  - The frozen backend left OF at 0 for counts above 1. Its ROL/ROR/SHLD/SHRD set no flags,
    and its RCR handled only 32 bits.

Semantic bugs:
- `div r/m8` was lowered as a 32-bit DIV. It now divides AX, with the quotient in AL and the
  remainder in AH.
- `lahf` did not set bit 1.
- `bt`/`bts` with a memory operand and a register offset ignored bit-string addressing: the
  address must advance by `(offset >> 5) * 4`, signed.
- `jp`/`jnp`/`jo`/`jno` were missing. Run 430 met them in the CRT `fmod` loop at `005a18e4`.
- `cld`/`std` were no-ops. They now set DF, and every string step (ESI/EDI) follows it.
- `lock inc/dec` were a plain read-modify-write. They are now an interlocked add with the
  same flags.
- `prefetch*` were rejected; they are cache hints without architectural effect and lower to nothing.

x87 stays the frozen binary64 model. Run 430 runs x87 natively instead; that is a design choice
of that executable, not of this translator.

## Proof (target CPU: Intel Core i3-3220)

`scripts/research/verify-v2-x86-exact.py` turns every distinct instruction form Porsche.exe uses
into a case. Memory operands are re-encoded as `[esi]` and `[esi+ebx*2+0x10]`, and each form runs
natively and through the backend from the same random state. The comparison covers GPRs, EFLAGS
& 0xcd5 (DF included), memory, XMM and MXCSR.

| Set | Forms | Cases | Differences | Receipt |
|---|---|---|---|---|
| Integer (`--set int`) | 961 | 285,765 | 0 | `int-oracle.json` |
| SSE (`--set sse`) | 172 | 51,600 | 0 | `sse-oracle.json` |
| Short Jcc 70..7f (`--set branch`) | 16 | 4,800 | 0 | `branch-oracle.json` |
| String forms, random DF (`--set string`) | 14 | 4,200 | 0 | `string-oracle.json` |
| `lock inc/dec`: flags + 2-thread atomicity (`verify-v2-x86-exact-lock.py`) | 2 | 200,000 + 2×2M | 0 | `lock-oracle.json` |

Negative controls (`--mutate`) must fail:

| Mutant | Failed forms |
|---|---|
| no PF | 650 |
| no AF | 223 |
| ROL/ROR always keep OF | 1 |
| string helpers ignore DF | 7 |

The non-atomic `lock` control loses 37–47% of the increments.

The integer set excludes control flow, stack, `rdtsc`, `cpuid`, `int3` and instructions that use
ESP as data. The behaviour of undefined flags is that of the target CPU; a CPU from 2000 may differ
there.

## Commands

```
py -3 scripts/research/verify-v2-x86-exact.py --set int
py -3 scripts/research/verify-v2-x86-exact.py --set sse
py -3 scripts/research/verify-v2-x86-exact.py --set branch
py -3 scripts/research/verify-v2-x86-exact.py --set string
py -3 scripts/research/verify-v2-x86-exact.py --set int --mutate no-parity   # must fail
py -3 scripts/research/verify-v2-x86-exact-lock.py
```

The oracles need `local/game/Porsche.exe` and MSVC x86 (`cl.exe` Hostx64/x86).

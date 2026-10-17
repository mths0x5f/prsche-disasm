"""Bounded integer lowering extension; mechanically inherits frozen Run257.

The state/header/runtime API remains Machine257/read257/write257/dispatch257.
No original per-body algorithm, host float conversion or machine-code fallback.
"""
import hashlib
import importlib.util
import inspect
from pathlib import Path

BASELINE_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'
BASELINE_PATH=Path(__file__).with_name('x86-cpp-backend-257.py')
if hashlib.sha256(BASELINE_PATH.read_bytes()).hexdigest()!=BASELINE_SHA:
    raise ValueError('Frozen257 backend SHA mismatch')
_spec=importlib.util.spec_from_file_location('frozen257_for277',BASELINE_PATH)
_base=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_base)
HEADER=_base.HEADER

PATCHES=[
 ("branches = ('jl','jge','je','jz','jne','jnz')", "branches = ('jl','jge','je','jz','jne','jnz','jg','jle','ja','jbe','jb','jae')"),
 ("        elif m == 'lea'", "        elif m in ('movsx','movzx') and len(ops)==2:\n"
  "            if not(ops[0].type==X86_OP_REG and ops[0].size in (2,4) and ops[1].type in (X86_OP_REG,X86_OP_MEM) and ops[1].size in (1,2) and ops[1].size<ops[0].size):\n"
  "                raise ValueError('Unsupported extension widths/operands')\n"
  "            code='U value='+expression(i,ops[1])+';'\n"
  "            if m=='movsx':\n"
  "                sign=1<<(ops[1].size*8-1)\n"
  "                code+=f'value=(value^0x{sign:x}u)-0x{sign:x}u;'\n"
  "            code+=store(i,ops[0],'value')\n"
  "        elif m=='not' and len(ops)==1 and ops[0].size in (1,2,4):\n"
  "            code='U value=~('+expression(i,ops[0])+');'+store(i,ops[0],'value')\n"
  "        elif m == 'lea'"),
 ("('xor','and','test','cmp','sbb','sub','add')", "('xor','or','and','test','cmp','sbb','sub','add')"),
 ("m in ('xor','and','test')", "m in ('xor','or','and','test')"),
 ("('^' if m == 'xor' else '&')", "{'xor':'^','or':'|','and':'&','test':'&'}[m]"),
 ("            code = f'if({condition})goto", "            elif m=='jg': condition='!(s.flags&0x40u)&&!(((s.flags>>7)^(s.flags>>11))&1u)'\n"
  "            elif m=='jle': condition='(s.flags&0x40u)||(((s.flags>>7)^(s.flags>>11))&1u)'\n"
  "            elif m=='ja': condition='!(s.flags&0x41u)'\n"
  "            elif m=='jbe': condition='(s.flags&0x41u)'\n"
  "            elif m=='jb': condition='(s.flags&1u)'\n"
  "            elif m=='jae': condition='!(s.flags&1u)'\n"
  "            code = f'if({condition})goto"),
]
DERIVED_SOURCE=inspect.getsource(_base.translate)
for _before,_after in PATCHES:
    if DERIVED_SOURCE.count(_before)!=1:raise ValueError('Frozen lowering patch context drift: '+_before)
    DERIVED_SOURCE=DERIVED_SOURCE.replace(_before,_after)
_namespace=dict(vars(_base))
exec(compile(DERIVED_SOURCE,str(Path(__file__))+'::derived','exec'),_namespace)
translate=_namespace['translate']

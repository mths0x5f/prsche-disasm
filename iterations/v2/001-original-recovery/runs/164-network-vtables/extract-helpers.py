"""Compile exact canonical helper definitions without unrelated TU link seams."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
workers=(root/'source/recovered/Porsche.exe/network_workers_members.cpp').read_text()
cleanup=(root/'source/recovered/Porsche.exe/network_cleanup.cpp').read_text()
def extract(source,name):
 start=source.rfind('\n',0,source.index(name+'('))+1
 opening=source.index('{',start);depth=1;end=opening+1
 while depth:
  depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]+'\n'
result='#include "porsche/network_workers_members.hpp"\n#include "porsche/network_services.hpp"\n#include "porsche/application_context_base.hpp"\n#include <cstring>\nnamespace porsche {\nnamespace {using U=std::uint32_t;\n'
for name in ('load','store','pointer'):result+=extract(workers,name)
result+='}\n'
for name in ('network_member_end_00529050','network_member_copy_0050e140','network_member_insert_004937f0'):result+=extract(workers,name)
result+=extract(cleanup,'network_services_begin_004c3150')+'}\n'
Path(sys.argv[1]).write_text(result)

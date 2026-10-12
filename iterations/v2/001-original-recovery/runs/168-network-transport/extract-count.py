"""Compile the exact canonical159 count helper, not its unrelated TU seams."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
source=(root/'source/recovered/Porsche.exe/network_workers_members.cpp').read_text()
def extract(name):
 start=source.rfind('\n',0,source.index(name+'('))+1;opening=source.index('{',start);end=opening+1;depth=1
 while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]+'\n'
Path(sys.argv[1]).write_text('#include "porsche/network_workers_members.hpp"\n#include <cstring>\nnamespace porsche {namespace {using U=std::uint32_t;\n'+extract('load')+'}\n'+extract('network_worker_queue_count_005809f0')+'}\n')

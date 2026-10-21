# Run342: original live heap callbacks

Three relocation-backed entries (149 PE bytes) are added to the supplemental
index and restored as C++: allocation tag, signed maximum-block scan and
containing-block lookup. Original half-open unsigned ranges, flagged-block
next-heap behavior and sentinel-check order are preserved.

Native attempt002 passes59 cases at /Od and /O2 (118 total); four mutations are
detected. Attempt001's fixture type compile failure remains local. Malformed,
nonterminating or unmapped inputs remain outside acceptance. Index/data evidence
and exact source pins are recorded here; shared game intake is [Run344](../344-heap-dependencies-integration/README.md).

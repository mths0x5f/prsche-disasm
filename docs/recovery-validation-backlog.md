# Отложенные проверки восстановления v2

Run257 (2026-10-17):
- [x] Static CALL/RET/stack lowering; 4 guard groups, 19 rejection cases PASS.
- [x] Run258:6originalbodies/104B/34instructions,36864native comparisons and4negative
  checks PASS;59pins and6actual COFForacles independentlychecked,3CALLREL32 only.
  FullCPU/game acceptance remainsopen; allclaims limitedtoselectedoriginalchains.
- [x]262:bounded synthetic byte/word/32 ADD/SUB/SBB/NEG, highbyte/word views,
  PUSH ESP/POP ESP/POP[ESP],indirectCALL[ESP]/JMP[ESP+4]:15744native cases PASS,
  19exactCOFForacles/70B/40instructions/28pins,19840explicit code-PC slot mappings.
- [ ]262:remaining ISA/operands/flags, guest memory faults/recursion/import/callback
  behavior and realgame execution; finite synthetic fixtures do not prove all of these.

Checkpoint264/265:
- [x]263:3existingcanonicalfree/lock bodies/302PEbytes,1compilerbatch/0warnings;
  4original-Unicorn free cutpoints/2048arena bytes/native lock/null checks PASS.
  Prior078551heap+31lock cases cited, not rerun; source/COFF/closure audit PASS.
- [x]264:1125candidatefunctionVAs+15support/1140members,419linknames/581diags;
  7493pins before/after PASS,1137symbolsnapshots reused/3newCOFFs,0compiles.
- [ ]264:raw00531f90 ten-consumer ABI binding, existing Win32providers,
  original006b4f20 table/initialization, concurrency/fault/fullgame composition.
- [x]265:actual419names→417tasks,22resolvedrows excluded;159pins/6guards.
  Genericqueue ranking does not revoke259unsafe005925d0 or005a4c05layout holds.

Checkpoint261:
- [x]259:2canonicalbodies/2exactbindings PE/source/COFF/native audit PASS.
  Fixture-only repairs preserved game/binding objects; one overwritten stale-native
  receipt explicitly recorded as a limitation. Five include roots now match observed order.
- [ ]259:005925d0 actual char-return consumer sign-extends AL, unlike originalDWORD.
  Recover caller return contract before alias; FILE/TLS/heap provider composition open.
- [x]260:257syntax coverage25/85,60rejected; not native/game acceptance.
- [x]261:1122candidatefunctionVAs+15support,417linknames/579diags,7461pins PASS;
  1133symbolsnapshots reused/4newCOFFs,0compiles. Actual EXE/DLL absent.
- [ ]261:newcanonical free_00531f90 dependency; original heap table/lifetime/locks
  must compose with real consumers. Controlled providers alone do not establish this.

Checkpoint249/256:1120candidatefunctionVAs/13support;418linkednames remain. NoEXE.
- [x]246:static76B/28instruction-to-C++pilot,375808native state comparisons (CF/ZF/SF/OF,
  GPregs/relativeESP/RET8/64Bmemory),exactPE+3COFForacles/46pins independentPASS.
- [ ]246:fullCPU/PF/AF/undefinedflags/x87/SSE/CALL/import/callback/guestmemoryloader;
  pilotusesexistingowners andadds0acceptedfunctions. Unknowninstructions failbeforecompile.
- [x]247:3canonicalbodies+3bindings,103originaloraclebytes/52CALLs/4056cases/293pinsPASS.
- [ ]247:sharedFILE/TLS/provider composition;5a4c05 originalIDs28..47 not covered by
  canonical26slotprefix. No silentbounds workaround or duplicateowner.
- [x]250/254:23writablezeroDWORDs,219directMEM4/fullHIGHLOW refs;independentaudits/nativePASS.
- [ ]250/254:computedaliases/wholelayout/lifetime;9screenedcells deferred duecoverage/WIP.
- [x]251:248cachedselection was not fullPE/WIPproof;006c0508fourunindexedrefs and
  0065b928existingWIPaddressprovider recorded. Never treatcandidatepoolasallocationapproval.
- [x]252:all85missingbody spans decoded/8516instructions;0wholebodiessupportedby246.
  CALL+stack and3externaltailJMP cases guidefuturebackendwork, not acceptance.
- [x]255/249:exactsourcecompilerreceipts/COFF bundled forfrozencollector withoutnativecommands.
- [x]256:validatedactual249diagnostics refreshedautomatic416task queue;no gameexecution.
- [x]253:30exactPE/oraclebytes/6instructions;18432nativecutpointcomparisons/49pins/8guardsPASS.
  ExplicitMissingEntry+threeoriginaltargetPCs, JSONretainsisolatedVMpilotprovenance;no gamequeuefeed.
- [ ]253:actualcallees/nativeFUNreceiverABI/indirecttransfers/CALL/guestloader/gameEXE.
  Pilotstopsbeforetarget; it doesnotprovefunctioncompletion oractualgame miss capture.

Checkpoint245:automaticfrontierqueue builtfromvalidated243archive andactualdiagnosticlog.
- [x]245:442exactunresolvednames/632diagnostics ->440tasks;17resolvedrows excluded.
  Accepted/partial/WIP/probe/interior/ABI/data/provider states keptdistinct;159pinsPASS.
- [x]245:6meaningful guards inclduplicateowners, unmappedrefs, sourcecomments/strings,
  runtimeidentity/unknownentries/dedup; runtimeinputparser only, no actualgame miss capture.
- [ ]Automaticcompilation/recoveryloop and instruction-to-C++pilot remainplanned,
  not completedbyqueuegeneration. Fullgame launch/fulloriginalfidelity stillopen.

Checkpoint243:1117functionVAs+8support,442linkedunresolvednames; actualgameEXE absent.
- [x]234:4originalwrappers,2048SDKoriginal/nativepairs+2048thiscallcaptures,445PEinstructions.
- [ ]234:lostECX/nativevoid(void) contracts00468100/004d8230/004d8240/00538d80 requirecaller
  receiver propagation; no genericaliases. New4d23f0/4d2100 callee implementations open.
- [x]240:exactcanonical C++fragments+2cdeclbindings,70originaloraclebytes/8callers,
  2268cases/targetidentity/ESP/nonvolatile;279pins/28headers independentauditPASS.
- [ ]240:realCRTlocktable prefix26vsoriginal48 andprovider/globalcomposition;
  fullfault/concurrency/register/game fidelity. Controlledfixture is not production.
- [x]241/243:canonical include roots verified against actualsuccessful compilerreceipt;
  allquotedsourceclosurepinned. Serial240batch reportedaccurately, notclaimedMP6.
- [x]242/243:exactsame4-byte signed/unsigned storage;125MEM4/HIGHLOWrefs andnative
  addressidentity/highbitcrosswrites/restorePASS. No genericalias/wholedataownership claim.
- [ ]Automation:realnativegame miss traces and broad instruction-to-C++ pilot remainopen;
  see docs/recovery-automation.md. Staticlink queue does not replace nativeexecution.

Checkpoint233 (2026-10-16):1111functionVAs+4supportobjects,442linkedunresolvednames.
- [x]223/229: exact native/original x86 comparisons229376+368640; direct callee signedBYTE,
  retained stack arguments, index/count/status behavior restored. Independent audits PASS.
- [ ]229:005907b0 callback targets006b49e0/input contracts; original parser output >=164B
  contiguous and callback packet4DWORD. Do not adopt getC overlapping locals/guessed casts.
- [x]226/231:5original writable scalar cells, exact zero/128/1/10 bits, native permissions,
  write/read/restore;226 adjacent pair retains4-byte separation. All direct HIGHLOW sites checked.
- [ ]226/231: computed aliases/whole original.data layout/ownership/lifetime before production.
- [x]227/228/233: actual support COFF closures, separate function/support counts and archive/link.
- [ ]224:canonical005a2248 cached probe has formatter_text_read_trace instrumentation; excluded.
  Build uninstrumented canonical owner only after exact ABI/shared locale globals coalescing.
- [ ]232:trace actual006b49e0 callback initialization;0058ff50 only proves006b49c8/49a1,
  not the006b49e0/49a2 table. Static index refs are navigation, not semantic proof.

Checkpoint222 (2026-10-16):1109functionVAs+2supportobjects,445linkedunresolvednames.
- [x]217/222: exact00590290cdecl binding resolvedactualwholearchive;1088cases/18497ABIchecks.
- [x]218: original renderer state dataflow repaired;119consumerinstructions/416B,
  1341totalPEinstructions,28controllednativeboundarytraces. GameC4146/fixtureC4244retained.
- [ ]218: fulloriginalprovider/lifetime/register/fault fidelity; FUN00571630 rawdata-pointer
  int/code* contract must be preserved when its actual owner is bound; no genericcast.
- [x]221/222: two originalreadonlyfloat4cells, exactbits+nativeREAD!WRITEpermissions,
  738indexedreads actualPE/Capstonechecked; existingformalbytealiasesmustsharecells later.
- [ ]219/221:26additionalHIGHLOWsites target1.0f outsideindexedspans. Resolveinstruction
  boundaries/controlflow before inferring absenceofaddress-taking/arrayrelationships.
  Candidate decodes are in research/binary-index/readonly-scalar-relocation-gaps.json.
- [ ]221: whole original.rdata relationships/indirectuses/sharedalias ownership beforeproduction.
- [x]220: duplicate/tampered support packets rejectedbeforeanynativecommands; functions/support
  countedseparately,actualCOFFdirectives verified, provenaliases separatedfromCRTresolution.
- [x]225/226: bounded zero initialization/writepermissions/adjacent layout fixture PASS;
  wholeprogramownership remains deferred above.

Checkpoint216:1108native functions;432unresolved names/624diagnostics:
89missingfunctions,36canonicaloutsideunion,1compiledsymbolmismatch,299dataviews,
7printedCRTcontracts. This is candidate frontier, not complete game remainder.
- [x]214: actualDWORDoutput restored, modulo32SUB/ADD/*1000 andsignedIDIV;
  42originalPEinstructions/SDKcontract,36864native asm-tail comparisons+3guardcasesPASS.
  Metadata-only RETcount correction:3originalpaths→1nativeepilogue, no native rerun.
- [ ]214: fulloriginalbody/providerexecution, successfulproviderinitialization,
  divisor-zero faults, concurrency/objectlifetime andoutgoingregister equivalence.
  Nativefixture usescontrolledcallback+verifiedinteger asm, not originalDirectSound.
- [x]216: one newobject,1107symbol snapshots/531platformpins reused;6804pinsPASS,
  onearchive/link,0compilations. No EXE orproduction integration.

Checkpoint215:1107native candidate functions, actual archive/link426unresolved
names/618diagnostics;90missing bodies/36canonical outside union/1compiled-VA mismatch,
292data names/7printed CRT contracts. Production173 unchanged.
- [x]211:127PEinstructions,2proven direct-call contracts and2native CALL+ADDESP8 sites.
- [ ]211/215:00590290 actualdefinition0args vs caller2unusedslots: rawcdecl ABI maymatch
  but C++symbols differ. Resolve through proven shared declaration/owner contract,
  not blanketalias; preserve extra caller slots where hardwaretrace requires them.
- [x]215:1094symbol snapshots reused/13new actualobjects,6780exact pins before/after;
  no new compilation. Supplementary exact/interior ownership210/212 found0overlaps.
- [ ]213: only remaining callback-reuse candidate00537b40; C2065/C2664/C2440 andcaller
  dataflow still needproof. Slotidentity207 doesnotpermitwhole-corpus callablecasts.
- [ ]214: bind private WORD_006b48da_214 to original006b48da:2 (base006b48d8+2)
  when native data owners are restored; standaloneword allocation mustnotbreakaliases.

Checkpoint207–212 (2026-10-15), пока до общего union:
- [x]207:4actualCOFF; original renderer callbacks/SDK Release CALL/RET contracts,
  1042PEinstructions и native callsite/stack evidence проверены;0Ghidra/native runtime reruns.
- [ ]207: renderer providers/slots initialization/ownership, full runtime/volatile
  register equivalence; typed externs не создаютdata owners.
- [ ]208:3compiled candidates из9;6failures сохранены.211 отдельно проверяет два
  direct-call contracts; остальныеcallable/type/string failures не скрывать.
- [x]210:2COFF;004012b0 signedFILD32alias/7exactexterns и004032d0 ECXself+stack1
  vcall contract,61PEinstructions.212:2COFF/5byte-slice occurrences/57PEinstructions.
- [ ]210:004012b0 x87 retained unrounded intermediates/rounding/controlword,
  integeroverflow, full callees;004032d0 actualcallee/global lifetime/ABI execution.
- [ ]212: uint4 extent views не canonical allocations/alias coalescing;
  original execution/global lifetimes/00598630 signedindexoverflow remainopen.
  C4146 from unchanged unsignednegation retained; do not silently change signedness.
- [ ]214:0058f5d0 concrete lost-output counterexample:0058f5edCALL[vtable+10],
  0058f5f8MOV EAX,[ESP], SHR1; getC mistakenly usesCOMobjectaddress. Restore proven
  DWORD outvalue and SDKcallback before considering compilation a usable algorithm.

Checkpoint202–206 (2026-10-15):1094 distinct native candidates, actual diagnostic link
413names/600diagnostics; production173 unchanged. Сборка кандидатов не закрывает fidelity.
- [x]202:97original PE instructions,9raw32 stores/8float bitviews и1024native bitcases
  (unaligned/overlap/NaN/subnormal/capture order) проверены; read-only audit PASS.
- [ ]202: полный00485100 против original execution, x87/SSE exceptions/rounding и
  callers/register equivalence. Physical outgoing ECX clobbered; original сохранял ECX.
  Совпадение ECX input/EAX return/RET8 не закрывает этот риск.
- [ ]203: original ABI/full-body validation21 compiled candidates; четыре pointer-call
  failures00540480/005404e0/00554530/0058f1f0 требуют original consumers.
  Observed compiler exit/timing не сохранились после metadata crash и остаются null;
  actual COFF/source/includes/owned diagnostics проверены, batch не повторялся.
- [ ]206:133function names (36canonical outside union/97missing),273data names
  (owners/initializers/overlapping aliases),7printed CRT contracts; no guessed definitions.
  Total unresolved413 относится к diagnostic candidate union, не полному остатку игры.
- [ ]205: historical warnings/regex — только priority queue; подтвердить каждую будущую
  representation rewrite по original RAM/CAST/instructions до изменения исходника.

Команды read-only проверки текущих пакетов:
`py -3 scripts/research/audit-v2-float-bits-202.py` и
`py -3 iterations/v2/001-original-recovery/runs/203-consumer-declaration-pilot/audit.py`.
Actual union command/cache evidence: `runs/206-frontier-and-float-union/README.md`.
Ниже — исторические checkpoints; их численные границы заменены206.

2026-10-15 final checkpoint199:1072 actualCOFF (924+148),28literal leaf-body matches.
Actualarchive/link выполнены повторяемым198CLI без компиляции:403raw/393linked names,
frontier полностью совпал с198.197 добавил2реальныхCOFF, не новые accepted functions.
- [ ]197: full caller high-IR/native lowering и state/volatile-register equivalence;
 44PEinstructions/4CALLsnippets/rawECX+stack+EAX/RET8 проверены,004930f0 byte-exact15B.
- [ ]194/200:7float4 per-consumer views → bounded changed-TU batch;8direct RAM links
  не доказывают data ownership/aliasing/lifetime.3Capstone FSTP direction conflicts,
 register/unique tokenstorage и address-only/unresolved strings сохранять отдельно.
 Potential757_DAT/330string gap bodies — очередь исследования, не accepted coverage.

2026-10-15:198 actual1070-object archive/link:403raw names/780objectrefs,
393linked unresolved names/581diagnostic occurrences;16new data owners,145function frontier
без изменений. Platform CRT resolved10, outputEXE/DLL отсутствует. Аудит6516pins PASS.
- [ ]198:241data definitions/initializers/aliasing,145FUN dependencies и7printed CRT contracts.
  Повторяемый --thiscall-summary принимает будущие disjoint ABI packets; не добавлятьstubs.

2026-10-15:196 —1070distinct compile candidates (924+146),16 новых объектов,
27cached body-byte matches сохранены.195 —actual1054-object diagnostic link:
377names/564diagnostic occurrences, raw387names/763objectrefs, noEXE.
- [ ]196:13 remaining leaf failures; printed FP aliases194, pointervalue store00536120,
  two partial scalar expressions/uint3; conversion warnings00485100 сохранять явно.
 14 raw32 address stores проверены по PE MOV/HIGHLOW/ECX и179tableVA;
 class lifetime/layout/dispatch и full algorithm fidelity этим не доказаны.
- [ ]195: связать36 canonical owners через доказанный ABI; восстановить109 отсутствующих
  FUN bodies,225data owners/aliases/initializers и7printed CRT contracts.
  These are candidate union dependencies, не замена game-link173267/303 и не полный остаток.

2026-10-15:193 подтвердил два raw32 storage corrections на original CALL/RET
и high IR,373 indexed instructions совпали с PE. Это закрывает два counterexample
для механизма восстановления потерянных call inputs, не их native/full-body acceptance.
- [ ]193: проверить остальные42 mismatch contracts индивидуально по hardware inputs;
  два из них исправлены в isolated Ghidra pilot, без production/native integration.
  У00489530 inferred void/hidden registers и22 nested calls всё ещё открыты;
  raw32/custom storage не доказывает semantic types/class/lifetime.

Прямое требование пользователя 2026-10-10: возвращаться к пропущенным проверкам.
Координатор обновляет этот список при каждом checkpoint и проверяет его
перед архитектурной приёмкой/переносом на Rust; пункт закрывается только
со ссылкой на фактически выполненную проверку. Сборка, bounded differential oracle
и визуальное соответствие — отдельные результаты.

Checkpoint173:476full+6partial;157projects/292TUs,24560freshoriginalcomparisons
(8791productionrepeats),12native/linkchecksPASS. Game-link267symbols/303refs; noEXE.
Nativevtables подключены и в constructors171; actualRTTI/provider/networkstartup ещё не доказаны.
Float output167 и parse170 проходят actualnativeoriginal, completearena/ABI/x87state;
Unicorn outputNaN/FPU расхождения сохранены явно, не скрыты.
00580ad0 canonicalreuse и observer/production equivalence8791cases подтверждены173.

Первый experimentalcandidate compile/run допускается до завершения всех boundedproofs;
каждый пропущенный consumer/ABI/global/data/behaviorcheck сохранять здесь или в связанном
packetREADME. Такой кандидат не считать faithfulacceptedgame; не подменять исходник
заглушками/догадками.178bulkcompileaudit и177mechanicalbody имеют отдельный статус.
Вернуться к полным fullgraph comparisons, CRT/unmaskedexceptions/invalidinput boundaries,
RTTI/typecache lifetime и liveOS/fidelity перед итоговой приёмкой/Rust.

2026-10-14 compilation-first192/190:1054distinctnativecandidateVAs,
924automatic+130thiscallleaf;27leafbodybytesexactoriginal. FullEXEнет.
184globals/layout declarations4604checked;837conflicts/681invalidspellings/unnamedMXCSR
и печатныеalias gaps не закрыты.188cache733/new190,3batchednativecallsPASS.
186 originalRET42mismatches/1noRET и пропущенныеcallreceiver/args требуют
originalCALL/RET consumers;1258RETmatch не разрешает blanketcallerrewrite.
190retry32:3new/127reused,130leafCOFF;29compilefailures открыты,189safe-slices proof1920checks complete;519unsupported slices остаютсяявными.
192new00553a70 compiled after189; gamebehavior/x87/aliases/callerABI stillopen.
ClassmethodnativeABI proof не доказывает реальнуюclass lifetime/globalstorage/callbacks.

2026-10-14 compilation-first experiments:
- [ ]177: canonical effects/global address owners для134direct+10virtual+52address
  seams; original/native full body comparison, DF60 и x87-live5, реальные callbacks.
- [ ]178/180/181: syntax/COFF success не доказывает original ABI/semantics;
  проверить inferred prototypes, скрытые регистры, overlapping storage и extended floats
  перед продвижением кандидатов. Объектные файлы строятся без guessed dependencies.
- [ ]179: inferred headers/HighGlobals — свидетельство Ghidra analysis;
  конфликты типов/layout/alias/initializers сохранять и проверять по original consumers.
  Read-only complete export не считать готовыми original source declarations.
Проверки объединять по зависимым блокам; pinned baseline/SHA использовать повторно,
не удалять эти обязательства ради первого запуска.

- [ ] Собрать игровой EXE и выполнить исходный startup с настоящими ресурсами.
  Блокер: Run173 game-link имеет267 unresolved symbols /303 references;
  compiler errors и other linker errors —0. Возврат: после устранения
  зависимостей; сначала запуск/выход, затем кадр, ввод, меню и режимы игры.
- [ ] Проверить закрытие через WM_CLOSE→GetMessage=0→исходный timer callback,
  включая producer времени006b7c40. Run086/098 проверяет другую исходную ветку
  cleanup message0x466→destroy→join. Возврат: после подключения исходного diagnostic callback/init и live timer-thread fixture. Run110 нашёл пропущенный
  worker00565270..533e (207B), исходный setup565030 передаёт его в55f420.
  Run112 worker восстановлен и интегрирован111 (6/6 oracle cases); setup/
  thread/timer packet118 интегрирован121: 9 cases, persistent28-byte ThreadRecord,
  live event/id loop retests. OS shutdown bindings125 проверены6 дочерними процессами.
  123 lifecycle(21 cases),127 wait(16) и130 stop→wait integration(3) приняты126.
  Живое расписание таймера и end-to-end WM_CLOSE ещё не выполнены.
- [ ] Проверить полный startup context004d1a90→004d3420→004d1ba0 внутри app_main.
  Review128/129: оригинал резервирует0x188 stack bytes, объект0x180 bytes передаётся
  в ECX; старый caller описывал лишь два DWORD и fixture скрывал это расхождение.
  Run129 исправляет caller/storage/ABI;4 span cases и15 main cases с реальными
  ctor/dtor прошли изолированно. Общая приёмка126 прошла: [15 composed main cases](../iterations/v2/001-original-recovery/runs/126-event-integration/application-main/verification.json) с реальными ctor/dtor.
  Возврат: после полного parser/context graph и live startup;
  полный004d3420 (8589B), vtable и его реальные зависимости остаются открытыми.
  Также открыть единственный owner/extent строки005e8e50: Run081 нашёл две
  раздельные модели пустой строки;129 использует существующий owner без новой догадки о размере.
- [ ] Проверить реальные DirectInput devices и caps/read paths со связанной
  оконной цепочкой. Run096 проверяет consumer0055feb0 с контролируемыми границами;
  native lifecycle fixture не подключает весь input graph. Возврат: после bindings.
- [ ] Выполнить THRASH driver dispatch, fullscreen transitions и настоящий кадр.
  stdcall declarations и успешные oracle checks не доказывают реальный драйвер.
  Возврат: после восстановления driver/service/vtable зависимостей game-link.
- [ ] Воспроизвести MAD stream/playback/audio/render loop целиком. Run094
  восстанавливает только header consumer; не использовать его как полную004dc850.
  Возврат: после восстановления stream/decoder/audio consumers.
- [ ] Сравнить producers путей0065b32c/334/360 и movie service0069ed0c с оригиналом.
  Текущие единые BSS owners не доказывают исходную инициализацию/валидные assets.
  Возврат: при восстановлении соответствующих startup producers. Run116
  нашёл startup_subsystem004b6ff0: install.txt→60pointer table65b2a0..65b38f.
  Run117: 9 component oracle cases и 7 composed checks подтвердили49 записей
  настоящего install.txt и пять shared table views. Реальный startup с assets
  ещё не выполнен; movie service0069ed0c остаётся открытым.
- [ ] Проверить длинные пути и исходные границы stack buffers у00427a60/0059dd00.
  Run103 oracle ограничен префиксами, помещающимися в100-byte local buffer;
  исходный overflow за пределами этих случаев не проверен. Возврат: вместе
  с path producers и контролируемым isolated original-x86 experiment.
- [ ] Подтвердить compiler/CRT/flags и байтовое совпадение там, где оно требуется.
  Run100 no-op семантически совпадает, но MSVC RET0 отличается от original RET.
  Ноль binary matches не скрывается за количеством recovered functions.
- [ ] Полная визуальная и игровая приёмка: оригинальные кадры/переходы,
  Quick Race, обе карьеры, физика/повреждения/ИИ/экономика/сохранения/звук.
  Возврат: после рабочего original baseline; текущие probes этого не доказывают.

- [ ] Завершить полный original formatter: float/wide/locale paths, runtime callback
  initialization, file-write/auxiliary/descriptor-preparation effects и lowio startup.
  Run136 соединяет production108 wrapper→124 parser→119 helpers→132 cleanup;
  canonical descriptor имеет32 bytes, wrapper пишет только исходный16-byte prefix.
  Непроинициализированный opaque tail не обнуляется; seeded test adapter отдельно.
  Run124:62 cases после lead-byte table, zero hexadecimal prefix и wide padding fixes.
  Run132:23 cases, flags перечитываются после callback, tail не декодируется до early exit.
  Run134:12 connected cases с actual wrapper и actual137 unsigned divide/remainder;
  Run137:72 runtime cases. Эти bounded проверки не доказывают live CRT/locale.
  Run138 принят в production archive:8 initial-image ranges /5057 bytes, PE relocations и pointer identities;
  callbacks не исполнялись, функций не добавлено. Это не runtime initialization.
  Возврат:005abee8→005a2e22 fatal path,005a0f5d callback writer и его float consumers,
  lowio initializer005a953e и реальные backend consumers.
- [ ] Восстановить полный EAX contract base destructor00525ec0.
  Run135: null-allocation branch сохраняет входной EAX в original x86, typed C++
  возвращает0; два разных seeds документируют расхождение. Partial destructor
  изолирован, в production library/реестр не подключён. Шесть full функций имеют
  отдельный scoped proof на16 cases, весь isolated packet —20 bounded contracts.
  Возврат: доказать caller-visible return/ABI всех веток и повторить composed
  ctor→context→dtor со связанными dependencies; vtable004d3420 остаётся открытой.
- [ ] Доказать signed mode domain audio initializer004a66b0 и полный consumer graph.
  Run131:8 isolated cases; signed timer half исправлен (−2→−1), query00565680
  заполняет все124 bytes. Index−9 ещё в pinned span,−10 выходит за него;
  original guard отсутствует. Не подменять чтение guessed clamp/throw.
  Возврат: проследить реальные producers mode и таблицы, проверить отрицательные
  значения с original x86 и затем общий startup/device graph. Пакет изолирован.

Владелец всех открытых пунктов — координатор. Состояние на checkpoint136:
ни один end-to-end пункт выше не объявлен выполненным. Run133 device имеет10
bounded cases после overlap/authoritative pointer-cell fixes; это не проверка
настоящего audio device. Активных назначений исполнителей нет.

Checkpoint143:28 новых полных функций приняты с исходными ABI/state/effect checks.
139 pooled memory callbacks,140 CRT bootstrap/fatal,141 application bridges,
142 audio lifecycle,144 strings/dialog,145 network lifecycle включены в общую библиотеку.
CRT error path:94 connected cases с реальными string/dialog bodies;17 свежих
original-x86 reports/7928 comparisons и4 composed cases не закрывают live startup.
Новые Win32 imports compiled и сверены с IAT, но отдельного live dialog/error OS
fixture ещё нет. Возврат: проверить реальные module-name/stdhandle/WriteFile и
lazy user32 resolution без terminal fatal до полноценного game startup.
142 устраняет duplicate656868/9 storage через aliases. Audio virtual mode
не ограничен исходным consumer004a6a00: signed-domain blocker131 остаётся.
145 storage trace подтверждает count/table005e8bfc/005e8c00, но максимальный
extent и canonical owner не доказаны; source таблица остаётся unresolved.
Готовые147/148/149 требуют общей приёмки; x87 Unicorn flags не считать аппаратной
истиной:147 содержит отдельный actual-original hardware oracle, принятие впереди.

Checkpoint153:35 новых full bodies приняты147..151.18 fresh original-x86 reports/
5816 comparisons (включая256 actual-original CPU x87 cases),4 composed cases и
8 native/link checks прошли. Native CRT error bindings проверены real OS fixture:
module path/truncation, stdhandles, WriteFile roundtrip/invalid handle и user32
symbol lookup. Live MessageBox, terminal fatal и полный CRT startup остаются открыты.
147 сохраняет128 Unicorn flag discrepancies; аппаратные FPU flags сверены с
реальными исходными24 байтами (единственный zero operand relocation проверен).
149 native walker read trace проверен private PAGE_GUARD/VEH observer; production
body без инструментации.150 context copy ещё использует typed005a1a40 boundary.
151 original vtable identities005b4968/70 ещё требуют canonical native relocation
и consumers; raw literal identity в oracle не доказывает native virtual dispatch.
152 lowio,154 context move,155 network sessions находятся в параллельной работе.

Checkpoint156:152/154/155 приняты,13 full bodies/4394 newcases.12 fresh reports/
8546 comparisons,4 composed и9 native/link checks прошли.154 exactmemorycopy
сравнивает130440 ordered accesses, включая overlap/selfcopy/alignment/DF.
152 Win32 bindings подтверждены IAT и real OS fixture, включая recursive lock /
cross-thread contention; это не full CRT inherited-handle/live concurrency acceptance.
155 teardown связывает реальные callees139/145/148/151; vtable5b4978 добавлен к
explicit native-relocation backlog вместе с5b4968/70.157/158/159 выполняются параллельно.
Batch SHA оптимизация не меняет критерии поведения:3 mutation/cache safety tests
прошли, benchmark9.2897→2.3805с/counts_equal=true. Перед checkpoint запускать
scripts/research/audit-v2-proofs.py с новым --report; исходники каждого уникального
файла хешируются один раз, изменения во время аудита отклоняются.

## Checkpoint160: CRT/text/network integration

- [x] Принять157/158/159:43 full bodies/10339 packet comparisons; общий build144 projects/270 TUs,
 12 fresh original reports/14491 comparisons +4 component-proven composed cases,
 10 native/link fixtures. Источники и границы —runs/160-crt-text-workers-integration.
- [x] Исправить canonical CRT lock-table prefix до26 DWORD: lock19 у text consumer,
 lock25 у locale setter;104 исходных байта/SHA, initial aliases, lazy/existing/unlock19/25 проверены.
- [x] Проверить10 новых Win32 IAT адаптеров: heap zero-fill/free, TLS/thread IDs/last error,
 thread isolation, Interlocked wrap и concurrent increments.
- [ ] Соединить новые CRT wrappers с настоящим smallblock allocator и original locale engines;
 live allocator/TLS startup/init/failure/concurrency проверить после161/162. Recording seams
 в original oracle не доказывают эти OS/game paths. Signal table005e5ec8 остаётся unresolved.
- [ ] Заменить raw original network vtable identity словами с canonical native relocations.
 163 доказал slot0/RTTI/HIGHLOW и пропуски index48ad70/48b340/5a1056;164 восстанавливает targets.
 Production native virtual dispatch ещё не принят.5e8e50 и5e8bfc/5e8c00 extent/owners открыты.
- [ ] Вернуться к полному004d3420 и запуску игры.279 unresolved symbols — текущая
 граница, не число всего остатка. Batch SHA/cache сокращает повторную работу, не заменяет original проверки.

## Checkpoint165: small heap, locale and groups

- [x] Принять161/162/163:25 full bodies/3909 packet cases;148projects/278TUs,
 13 fresh original reports/8082 comparisons +4 composedcases;11 native/linkfixtures PASS.
 161pins15207intermediate/14936preboundary snapshots иcopyalias835B/46HIGHLOW.
 162pins34 actualprotectedexceptions,originalscopes/handlerbytes/nativeFS restoration.
- [x] Проверить15 platform adapters с real Win32 heap/VM lifecycle,
 LCMapString/characterconversion/classification/CPInfo.Это OS smoke, не complete game parity.
- [x] Batch original SHA в manualindex:37functions→1binaryread/hash, concurrentchanges
 отклоняются;9cache/refresh/manualindex tests PASS. Historical reports unchanged.
- [ ] Live original smallblock allocator/TLS/locale initialization/concurrency/stackoverflow
 с настоящими ресурсами остаются открытыми. Native VM fixture не доказывает весьallocator.
- [ ] Принять164vtabletargets/166output; indexgap48ad70/48b340/5a1056 дополнитьпоSHA.
 Raw constructorvptr и identitycomparisons заменить вместе canonicalnativeowners;
 RTTI и sharedemptystring extent требуют originalconsumers, fixturedata не переноситьвgame.
- [ ] Полный игровой EXE:273unresolved/308refs;compile/otherdiagnostics0.
 Послеclosingfrontier вернутьсякstartup004d3420,режимам/карьерам/live/visual acceptance.

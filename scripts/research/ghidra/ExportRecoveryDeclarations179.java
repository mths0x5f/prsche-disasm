// Read-only declaration export; never commits inferred types or function signatures.
// @category Porsche.V2
import ghidra.app.util.headless.HeadlessScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.*;
import ghidra.util.task.TaskMonitor;
import com.google.gson.*;
import java.io.*;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

public class ExportRecoveryDeclarations179 extends HeadlessScript {
 private final Gson json=new GsonBuilder().disableHtmlEscaping().create();
 private final String originalSha="ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39";
 private Map<String,Object> row(Object...pairs){Map<String,Object>r=new LinkedHashMap<>();for(int i=0;i<pairs.length;i+=2)r.put((String)pairs[i],pairs[i+1]);return r;}
 private void line(BufferedWriter w,Object r)throws IOException{w.write(json.toJson(r));w.newLine();w.flush();}
 private BufferedWriter writer(Path dir,String name)throws IOException{return Files.newBufferedWriter(dir.resolve(name),StandardCharsets.UTF_8);}
 private void atomicJson(Path path,Object value)throws IOException{Path temp=path.resolveSibling(path.getFileName()+".tmp");Files.writeString(temp,json.toJson(value)+"\n",StandardCharsets.UTF_8);Files.move(temp,path,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
 private Map<String,Object> storageInfo(VariableStorage s){List<Object>nodes=new ArrayList<>();for(Varnode v:s.getVarnodes())nodes.add(row("space",v.getAddress().getAddressSpace().getName(),"offset",Long.toUnsignedString(v.getOffset()),"bytes",v.getSize(),"address",v.getAddress().toString()));return row("display",s.toString(),"serialization",s.getSerializationString(),"bytes",s.size(),"memory",s.isMemoryStorage(),"register",s.isRegisterStorage(),"stack",s.isStackStorage(),"compound",s.isCompoundStorage(),"forced_indirect",s.isForcedIndirect(),"varnodes",nodes);}
 private String declaration(DataTypeWriter dtw,Method method,String name,DataType type,int size)throws Exception{return ((String)method.invoke(dtw,name,type,size,false,monitor)).strip();}
 private Map<String,Object> typeInfo(DataType t){return row("path",t.getPathName(),"name",t.getName(),"display",t.getDisplayName(),"length",t.getLength(),"alignment",t.getAlignment(),"class",t.getClass().getName());}
 @Override public void run()throws Exception{
  String[]args=getScriptArgs();if(args.length<1)throw new IllegalArgumentException("output-dir [timeout=30] [limit=0] [checkpoint-dir]");
  Path out=Path.of(args[0]).toAbsolutePath().normalize();Files.createDirectories(out);int timeout=args.length>1?Integer.parseInt(args[1]):30,limit=args.length>2?Integer.parseInt(args[2]):0;
  Path checkpoints=args.length>3?Path.of(args[3]):out.resolve("checkpoints");Files.createDirectories(checkpoints);
  if(args.length<5)throw new IllegalArgumentException("Exporter/tool provenance SHA required");String exportIdentity=args[4];
  boolean finalizeOnly=args.length>5&&!args[5].isBlank();if(finalizeOnly)exportIdentity=args[5];
  if(!currentProgram.getName().equals("Porsche.exe"))throw new IOException("Only original Porsche.exe is authorized");
  String nativePath=currentProgram.getExecutablePath();if(nativePath.length()>3&&nativePath.charAt(0)=='/'&&nativePath.charAt(2)==':')nativePath=nativePath.substring(1);
  String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(Path.of(nativePath))));
  if(!sha.equals(originalSha)||!sha.equalsIgnoreCase(currentProgram.getExecutableSHA256()))throw new IOException("Original/analyzed SHA mismatch");
  boolean changedBefore=currentProgram.isChanged();DataTypeManager dtm=currentProgram.getDataTypeManager();
  Method format=DataTypeWriter.class.getDeclaredMethod("getTypeDeclaration",String.class,DataType.class,int.class,boolean.class,TaskMonitor.class);format.setAccessible(true);
  List<DataType> types=new ArrayList<>();Iterator<DataType> ti=dtm.getAllDataTypes();while(ti.hasNext())types.add(ti.next());
  try(BufferedWriter w=writer(out,"types.h")){w.write("/* AUTOMATIC GHIDRA TYPES; analysis declarations, not original recovered source. SHA256 "+sha+" */\n");new DataTypeWriter(dtm,w,false).write(dtm,monitor);}
  DataTypeWriter declarator=new DataTypeWriter(dtm,new StringWriter(),false);
  try(BufferedWriter w=writer(out,"types.jsonl")){
   for(DataType t:types){monitor.checkCancelled();Map<String,Object>r=typeInfo(t);
    if(t instanceof Composite){Composite c=(Composite)t;List<Object>fields=new ArrayList<>();for(DataTypeComponent f:c.getDefinedComponents())fields.add(row("ordinal",f.getOrdinal(),"offset",f.getOffset(),"bytes",f.getLength(),"field",f.getFieldName(),"type",f.getDataType().getPathName(),"bitfield",f.isBitFieldComponent()));r.put("fields",fields);r.put("packing_enabled",c.isPackingEnabled());r.put("alignment",c.getAlignment());}
    if(t instanceof ghidra.program.model.data.Enum){ghidra.program.model.data.Enum e=(ghidra.program.model.data.Enum)t;Map<String,Long>values=new LinkedHashMap<>();for(String n:e.getNames())values.put(n,e.getValue(n));r.put("values",values);}
    if(t instanceof TypeDef)r.put("base",((TypeDef)t).getDataType().getPathName());
    if(t instanceof ghidra.program.model.data.Array){ghidra.program.model.data.Array a=(ghidra.program.model.data.Array)t;r.put("count",a.getNumElements());r.put("element_bytes",a.getElementLength());r.put("element_type",a.getDataType().getPathName());}
    if(t instanceof Pointer){DataType p=((Pointer)t).getDataType();r.put("pointee",p==null?null:p.getPathName());}
    line(w,r);
   }
  }
  int listingCount=0,listingErrors=0;
  try(BufferedWriter w=writer(out,"listing-globals.jsonl")){
   for(Data d:currentProgram.getListing().getDefinedData(true)){monitor.checkCancelled();listingCount++;Map<String,Object>r=row("va",d.getAddress().toString(),"bytes",d.getLength(),"type",typeInfo(d.getDataType()),"labels",Arrays.stream(d.getSymbols()).map(s->s.getName(true)).toList());
    try{r.put("declaration",declaration(declarator,format,d.getLabel(),d.getDataType(),d.getLength()));}catch(Exception ex){listingErrors++;r.put("declaration_error",ex.toString());}line(w,r);
   }
  }
  List<Function>functions=new ArrayList<>();for(Function f:currentProgram.getFunctionManager().getFunctions(true))functions.add(f);
  if(functions.size()!=5772)throw new IOException("Unexpected analyzed function count: "+functions.size());
  Set<String>done=new HashSet<>();Path functionPath=out.resolve("functions.jsonl");
  for(Function f:functions){String va=f.getEntryPoint().toString();Path saved=checkpoints.resolve(va+".json");if(!Files.exists(saved))continue;JsonObject r=JsonParser.parseString(Files.readString(saved)).getAsJsonObject();if(r.get("schema").getAsInt()!=2||!r.get("export_identity_sha256").getAsString().equals(exportIdentity)||!r.get("module_sha256").getAsString().equals(sha)||!r.get("entry_va").getAsString().equals(va))throw new IOException("Resume provenance mismatch: "+saved);done.add(va);}
  if(finalizeOnly&&done.size()!=functions.size())throw new IOException("Finalize-only requires every captured function; no mixed chunks permitted");
  int fresh=0,fail=0;DecompInterface decomp=new DecompInterface();decomp.toggleCCode(true);decomp.toggleSyntaxTree(true);
  if(!decomp.openProgram(currentProgram))throw new IOException("Decompiler open failed: "+decomp.getLastMessage());
  try{
   for(Function f:functions){monitor.checkCancelled();String va=f.getEntryPoint().toString();if(done.contains(va))continue;if(limit>0&&fresh>=limit)break;
    Map<String,Object>r=row("schema",2,"module","Porsche.exe","module_sha256",sha,"export_identity_sha256",exportIdentity,"entry_va",va,"name",f.getName(true),"database_prototype",f.getPrototypeString(true,true),"database_signature_source",f.getSignatureSource().toString(),"database_calling_convention",f.getCallingConventionName(),"thunk",f.isThunk(),"external",f.isExternal(),"provenance","Ghidra 12.1.3 cached analysis; decompiler inference; no signature commit");
    try{
     DecompileResults result=decomp.decompileFunction(f,timeout,monitor);r.put("error",result.getErrorMessage());
     if(!result.decompileCompleted()||result.getDecompiledFunction()==null||result.getHighFunction()==null){r.put("status","decompile_failed");fail++;}
     else{r.put("status","decompiled");String signature=result.getDecompiledFunction().getSignature();r.put("inferred_signature",signature);r.put("prototype",signature.strip().replaceAll(";$","")+";");HighFunction high=result.getHighFunction();FunctionPrototype p=high.getFunctionPrototype();
      r.put("inferred_calling_convention",p.getModelName());r.put("extra_pop",p.getExtraPop());r.put("return_type",typeInfo(p.getReturnType()));r.put("return_storage",p.getReturnStorage().toString());r.put("return_storage_detail",storageInfo(p.getReturnStorage()));r.put("noreturn",p.hasNoReturn());r.put("this_pointer",p.hasThisPointer());r.put("varargs",p.isVarArg());r.put("inline",p.isInline());
      List<Object>params=new ArrayList<>();for(int i=0;i<p.getNumParams();i++){HighSymbol s=p.getParam(i);params.add(row("name",s.getName(),"type",typeInfo(s.getDataType()),"storage",s.getStorage().toString(),"storage_detail",storageInfo(s.getStorage()),"this",s.isThisPointer(),"hidden_return",s.isHiddenReturn(),"type_locked",s.isTypeLocked()));}r.put("parameters",params);
      List<Object>globals=new ArrayList<>();Iterator<HighSymbol>gi=high.getGlobalSymbolMap().getSymbols();while(gi.hasNext()){HighSymbol s=gi.next();Map<String,Object>g=row("name",s.getName(),"namespace",s.getNamespace()==null?null:s.getNamespace().getName(true),"type",typeInfo(s.getDataType()),"bytes",s.getSize(),"storage",s.getStorage().toString(),"storage_detail",storageInfo(s.getStorage()),"type_locked",s.isTypeLocked(),"name_locked",s.isNameLocked());
       try{g.put("declaration",declaration(declarator,format,s.getName(),s.getDataType(),s.getSize()));}catch(Exception ex){g.put("declaration_error",ex.toString());}globals.add(g);}
      r.put("globals",globals);
     }
    }catch(Exception ex){r.put("status","export_failed");r.put("exception",ex.toString());fail++;}
    atomicJson(checkpoints.resolve(va+".json"),r);done.add(va);fresh++;
    if(fresh%25==0){Files.writeString(out.resolve("progress.json"),json.toJson(row("module",currentProgram.getName(),"module_sha256",sha,"attempted",done.size(),"total",functions.size(),"fresh",fresh,"failed_this_pass",fail,"complete",false))+"\n",StandardCharsets.UTF_8);println("DECL179 "+done.size()+"/"+functions.size());}
   }
  }finally{decomp.dispose();}
  int failedTotal=0,globalErrors=0,globalOccurrences=0;Map<String,Map<String,JsonObject>>globalVariants=new TreeMap<>();Map<String,List<String>>globalConsumers=new TreeMap<>();
  try(BufferedWriter w=writer(out,"functions.jsonl");BufferedWriter h=writer(out,"prototypes.h")){
   h.write("/* Inferred getC signatures verbatim. ABI is recorded in functions.jsonl; no ABI lowering or semantic acceptance. */\n#pragma once\n#include \"types.h\"\n");
   for(Function f:functions){Path saved=checkpoints.resolve(f.getEntryPoint()+".json");if(!Files.exists(saved))continue;JsonObject r=JsonParser.parseString(Files.readString(saved)).getAsJsonObject();line(w,r);if(!r.get("status").getAsString().equals("decompiled")){failedTotal++;continue;}h.write("/* VA "+r.get("entry_va").getAsString()+"; inferred ABI "+r.get("inferred_calling_convention").getAsString()+" */\n"+r.get("prototype").getAsString()+"\n");
    for(JsonElement ge:r.getAsJsonArray("globals")){JsonObject g=ge.getAsJsonObject();globalOccurrences++;if(g.has("declaration_error"))globalErrors++;String key=(g.has("namespace")?g.get("namespace").getAsString():"")+"::"+(g.has("name")?g.get("name").getAsString():"<unnamed:"+g.get("storage").getAsString()+">");String variant=g.get("storage").getAsString()+"|"+g.getAsJsonObject("type").get("path").getAsString()+"|"+(g.has("declaration")?g.get("declaration").getAsString():"ERROR");globalVariants.computeIfAbsent(key,k->new TreeMap<>()).put(variant,g);globalConsumers.computeIfAbsent(key+"|"+variant,k->new ArrayList<>()).add(r.get("entry_va").getAsString());}
   }
  }
  int conflicts=0,globalHeaderCount=0;
  try(BufferedWriter w=writer(out,"globals.jsonl");BufferedWriter c=writer(out,"conflicts.jsonl");BufferedWriter h=writer(out,"globals.h")){
   h.write("/* Unambiguous HighFunction global declarations. No storage definitions or address-owner assumptions. */\n#pragma once\n#include \"types.h\"\n");
    for(var entry:globalVariants.entrySet()){List<Object>variants=new ArrayList<>();for(var v:entry.getValue().entrySet())variants.add(row("symbol",v.getValue(),"consumer_vas",globalConsumers.get(entry.getKey()+"|"+v.getKey())));Map<String,Object>g=row("module_sha256",sha,"identity",entry.getKey(),"conflict",variants.size()>1,"variants",variants);line(w,g);if(variants.size()>1){conflicts++;line(c,g);}else{JsonObject s=entry.getValue().values().iterator().next();if(s.has("name")&&s.has("declaration")&&s.getAsJsonObject("storage_detail").get("memory").getAsBoolean()){h.write("/* "+s.get("storage").getAsString()+" */ extern "+s.get("declaration").getAsString()+";\n");globalHeaderCount++;}}}
  }
  if(currentProgram.isChanged()!=changedBefore)throw new IOException("Read-only export unexpectedly changed program state");
  atomicJson(out.resolve("progress.json"),row("schema",2,"module",currentProgram.getName(),"module_sha256",sha,"ghidra_version",ghidra.framework.Application.getApplicationVersion(),"language",currentProgram.getLanguageID().toString(),"compiler_spec",currentProgram.getCompilerSpec().getCompilerSpecID().toString(),"types",types.size(),"listing_data",listingCount,"listing_declaration_errors",listingErrors,"attempted",done.size(),"total",functions.size(),"fresh",fresh,"failed_this_pass",fail,"failed_total",failedTotal,"high_global_occurrences",globalOccurrences,"high_global_identities",globalVariants.size(),"high_global_declaration_errors",globalErrors,"high_global_conflicts",conflicts,"high_global_header_declarations",globalHeaderCount,"complete",done.size()==functions.size(),"program_changed_before",changedBefore,"program_changed_after",currentProgram.isChanged(),"boundary","Read-only existing analysis; inferred signatures/types preserve Ghidra uncertainty, not recovered-source or behavior proof"));
  println("DECL179_DONE attempted="+done.size()+"/"+functions.size()+" fresh="+fresh+" failed="+fail);
 }
}

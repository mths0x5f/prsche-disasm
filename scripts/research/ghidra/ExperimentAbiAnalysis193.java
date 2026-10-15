// Bounded signature/storage experiment on a copied project only. No autoanalysis.
// @category Porsche.V2
import ghidra.app.util.headless.HeadlessScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.*;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public class ExperimentAbiAnalysis193 extends HeadlessScript {
 private final Gson json=new GsonBuilder().disableHtmlEscaping().setPrettyPrinting().create();
 private final String sha="ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39";
 private final String[] vas={"00482f70","00483290","00489370","00489530"};
 private Map<String,Object> row(Object...p){Map<String,Object>r=new LinkedHashMap<>();for(int i=0;i<p.length;i+=2)r.put((String)p[i],p[i+1]);return r;}
 private void write(Path p,Object o)throws Exception{Files.writeString(p,json.toJson(o)+"\n",StandardCharsets.UTF_8);}
 private Map<String,Object> storage(VariableStorage s){List<Object>v=new ArrayList<>();for(Varnode n:s.getVarnodes())v.add(row("space",n.getAddress().getAddressSpace().getName(),"offset",n.getOffset(),"bytes",n.getSize(),"address",n.getAddress().toString()));return row("display",s.toString(),"bytes",s.size(),"varnodes",v);}
 private Object node(Varnode n,int depth){if(n==null)return null;Map<String,Object>r=row("address",n.getAddress().toString(),"space",n.getAddress().getAddressSpace().getName(),"offset",n.getOffset(),"bytes",n.getSize(),"input",n.isInput(),"constant",n.isConstant());HighVariable h=n.getHigh();if(h!=null){r.put("high_name",h.getName());r.put("high_type",h.getDataType().getPathName());if(h.getSymbol()!=null)r.put("high_storage",storage(h.getSymbol().getStorage()));}PcodeOp d=n.getDef();if(d!=null){r.put("defined_at",d.getSeqnum().toString());r.put("defined_by",d.getMnemonic());if(depth>0){List<Object>a=new ArrayList<>();for(Varnode x:d.getInputs())a.add(node(x,depth-1));r.put("producer_inputs",a);}}return r;}
 private Object op(PcodeOp p,int depth){List<Object>a=new ArrayList<>();for(Varnode n:p.getInputs())a.add(node(n,depth));return row("sequence",p.getSeqnum().toString(),"instruction_va",p.getSeqnum().getTarget().toString(),"opcode",p.getMnemonic(),"output",node(p.getOutput(),0),"inputs",a);}
 private void tokens(ClangNode n,List<Object> out){if(n instanceof ClangToken){ClangToken t=(ClangToken)n;out.add(row("kind",n.getClass().getSimpleName(),"text",t.getText(),"min_va",t.getMinAddress()==null?null:t.getMinAddress().toString(),"max_va",t.getMaxAddress()==null?null:t.getMaxAddress().toString(),"pcode_sequence",t.getPcodeOp()==null?null:t.getPcodeOp().getSeqnum().toString(),"varnode",node(t.getVarnode(),0)));}for(int i=0;i<n.numChildren();i++)tokens(n.Child(i),out);}
 private Object database(Function f){List<Object>params=new ArrayList<>();for(Parameter p:f.getParameters())params.add(row("name",p.getName(),"type",p.getDataType().getPathName(),"bytes",p.getLength(),"storage",storage(p.getVariableStorage()),"auto",p.isAutoParameter()));return row("signature",f.getPrototypeString(true,true),"convention",f.getCallingConventionName(),"source",f.getSignatureSource().toString(),"custom_storage",f.hasCustomVariableStorage(),"stack_purge_bytes",f.getStackPurgeSize(),"return_type",f.getReturnType().getPathName(),"return_storage",storage(f.getReturn().getVariableStorage()),"parameters",params);}
 private List<Object> capture(Path out,String stage)throws Exception{
  DecompInterface di=new DecompInterface();di.toggleCCode(true);di.toggleSyntaxTree(true);if(!di.openProgram(currentProgram))throw new IllegalStateException(di.getLastMessage());List<Object>rows=new ArrayList<>();
  try{for(String va:vas){Function f=getFunctionAt(toAddr(va));if(f==null)throw new IllegalStateException("Missing function "+va);Map<String,Object>r=row("entry_va",va,"stage",stage,"database",database(f));DecompileResults d=di.decompileFunction(f,60,monitor);r.put("error",d.getErrorMessage());r.put("complete",d.decompileCompleted());if(!d.decompileCompleted()||d.getHighFunction()==null)throw new IllegalStateException("Decompile failed "+va+": "+d.getErrorMessage());
   HighFunction h=d.getHighFunction();FunctionPrototype fp=h.getFunctionPrototype();List<Object>params=new ArrayList<>();for(int i=0;i<fp.getNumParams();i++){HighSymbol s=fp.getParam(i);params.add(row("name",s.getName(),"type",s.getDataType().getPathName(),"bytes",s.getSize(),"storage",storage(s.getStorage()),"this",s.isThisPointer(),"type_locked",s.isTypeLocked()));}r.put("inferred",row("signature",d.getDecompiledFunction().getSignature(),"convention",fp.getModelName(),"extra_pop",fp.getExtraPop(),"parameters",params,"return_type",fp.getReturnType().getPathName(),"return_storage",storage(fp.getReturnStorage())));
   List<Object>ops=new ArrayList<>(),calls=new ArrayList<>(),ts=new ArrayList<>();Iterator<PcodeOpAST> it=h.getPcodeOps();while(it.hasNext()){PcodeOp p=it.next();ops.add(op(p,0));if(p.getOpcode()==PcodeOp.CALL||p.getOpcode()==PcodeOp.CALLIND)calls.add(op(p,5));}tokens(d.getCCodeMarkup(),ts);r.put("pcode",ops);r.put("calls",calls);r.put("tokens",ts);Files.writeString(out.resolve(stage+"-"+va+".c"),d.getDecompiledFunction().getC().replace("\r\n","\n"),StandardCharsets.UTF_8);write(out.resolve(stage+"-"+va+".json"),r);rows.add(row("entry_va",va,"signature",d.getDecompiledFunction().getSignature(),"error",d.getErrorMessage(),"call_count",calls.size(),"pcode_count",ops.size()));println("ABI193 "+stage+" "+va+" "+d.getDecompiledFunction().getSignature());
  }}finally{di.dispose();}return rows;
 }
 private void correct(String va,int words,boolean zeroReturn)throws Exception{
  Function f=getFunctionAt(toAddr(va));DataType raw=Undefined4DataType.dataType;List<Variable>p=new ArrayList<>();p.add(new ParameterImpl("receiver_bits",raw,currentProgram.getRegister("ECX"),currentProgram,SourceType.USER_DEFINED));for(int i=0;i<words;i++)p.add(new ParameterImpl("stack_"+Integer.toHexString(4+i*4)+"_bits",raw,4+i*4,currentProgram,SourceType.USER_DEFINED));
  ReturnParameterImpl ret=zeroReturn?new ReturnParameterImpl(raw,currentProgram.getRegister("EAX"),currentProgram):new ReturnParameterImpl(VoidDataType.dataType,currentProgram);
  f.updateFunction("__thiscall",ret,p,Function.FunctionUpdateType.CUSTOM_STORAGE,true,SourceType.USER_DEFINED);f.setStackPurgeSize(words*4);
 }
 @Override public void run()throws Exception{
  String[]args=getScriptArgs();if(args.length!=2)throw new IllegalArgumentException("output experiment-root");Path out=Path.of(args[0]).toAbsolutePath().normalize(),experiment=Path.of(args[1]).toAbsolutePath().normalize();String projectLocation=currentProgram.getDomainFile().getProjectLocator().getLocation(); if(projectLocation.matches("^/[A-Za-z]:.*"))projectLocation=projectLocation.substring(1); Path project=Path.of(projectLocation).toAbsolutePath().normalize();if(!project.startsWith(experiment)||!experiment.getFileName().toString().equals("v2-abi-analysis-193"))throw new IllegalStateException("Refuse mutation outside193 copied project: "+project);Files.createDirectories(out);
  if(!currentProgram.getName().equals("Porsche.exe")||!sha.equalsIgnoreCase(currentProgram.getExecutableSHA256()))throw new IllegalStateException("Original source identity mismatch");String nativePath=currentProgram.getExecutablePath();if(nativePath.startsWith("/")&&nativePath.charAt(2)==':')nativePath=nativePath.substring(1);String actual=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(Path.of(nativePath))));if(!sha.equals(actual))throw new IllegalStateException("Original bytes mismatch");
  List<Object>before=capture(out,"before");write(out.resolve("before-complete.json"),row("original_sha256",sha,"project",project.toString(),"functions",before,"mutations",0));
  // Only these two callees are changed, after all four baseline snapshots exist.
  int tx=currentProgram.startTransaction("ABI193 raw original CALL/RET storage");boolean success=false;try{correct("00489530",2,false);correct("00482f70",3,true);success=true;}finally{currentProgram.endTransaction(tx,success);}
  List<Object>after=capture(out,"after-callees");write(out.resolve("result.json"),row("original_sha256",sha,"ghidra_version",ghidra.framework.Application.getApplicationVersion(),"project",project.toString(),"language",currentProgram.getLanguageID().toString(),"compiler_spec",currentProgram.getCompilerSpec().getCompilerSpecID().toString(),"before",before,"after",after,"modified_functions",List.of("00489530","00482f70"),"autoanalysis",false,"semantic_type_recovery",false));
 }
}

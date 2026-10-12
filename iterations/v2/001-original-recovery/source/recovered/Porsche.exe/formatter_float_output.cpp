#include "porsche/formatter_float_output.hpp"
#include "porsche/formatter_runtime.hpp"
#include "porsche/formatter_strings.hpp"
#include "porsche/formatter_crt_runtime.hpp"
#include "porsche/context_move.hpp"
#include <cstring>
namespace porsche {
#if defined(PORSCHE_FLOAT_OUTPUT_TRACE)
void formatter_float_output_trace(std::uint32_t,std::uint32_t,const void*,std::uint32_t);
#endif
#include "formatter_float_output_data.inc"
namespace {
using U=std::uint32_t;
using W=FormatterFloatWords12;
std::uint16_t half(const void* p,unsigned n){std::uint16_t v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+n,2);return v;}
void half(void* p,unsigned n,std::uint16_t v){std::memcpy(static_cast<std::uint8_t*>(p)+n,&v,2);}
U word(const void* p,unsigned n){U v;std::memcpy(&v,static_cast<const std::uint8_t*>(p)+n,4);return v;}
void word(void* p,unsigned n,U v){std::memcpy(static_cast<std::uint8_t*>(p)+n,&v,4);}
U add_int(int a,int b){return static_cast<U>(a)+static_cast<U>(b);}
#if defined(PORSCHE_FLOAT_OUTPUT_TRACE)
U text_bytes(const char* p){U n=0;while(p[n++]){}return n;}
struct StageTrace {
 U tag;void* out;FormatterFloatDecimal16* value=nullptr;
 StageTrace(U t,const void* in,U n,void* result):tag(t),out(result){formatter_float_output_trace(tag,0,in,n);}
 ~StageTrace(){
  if(tag==4){formatter_float_output_trace(tag,1,&value->exponent,4);formatter_float_output_trace(tag,3,out,text_bytes(static_cast<const char*>(out)));}
  else formatter_float_output_trace(tag,1,out,tag==1?10:tag==2?12:5+static_cast<FormatterFloatDecimal28*>(out)->count);
 }
};
#endif
// Each original public entry uses precisely FLD m64; FSTP m64 before dispatch.
void load_number(const void* source,U (&result)[2]) {
 __asm {
  mov eax,source
  mov edx,result
  fld qword ptr [eax]
  fstp qword ptr [edx]
 }
}
}
U __cdecl formatter_float_add_word_005adaae(U a,U b,U* out){const U sum=a+b;const U carry=sum<a||sum<b;*out=sum;return carry;}
void __cdecl formatter_float_add96_005adacf(W* a,const W* b){
 if(formatter_float_add_word_005adaae(a->words[0],b->words[0],a->words))
  if(formatter_float_add_word_005adaae(a->words[1],1,a->words+1))++a->words[2];
 if(formatter_float_add_word_005adaae(a->words[1],b->words[1],a->words+1))++a->words[2];
 formatter_float_add_word_005adaae(a->words[2],b->words[2],a->words+2);
}
void __cdecl formatter_float_left96_005adb2d(W* a){const U low=a->words[0],mid=a->words[1];a->words[0]=low*2;a->words[1]=mid*2|(low>>31);a->words[2]=a->words[2]*2|(mid>>31);}
void __cdecl formatter_float_right96_005adb5b(W* a){const U high=a->words[2],mid=a->words[1];a->words[1]=(mid>>1)|(high<<31);a->words[2]=high>>1;a->words[0]=(a->words[0]>>1)|(mid<<31);}
void __cdecl formatter_float_multiply96_005adf5b(W* a,const W* b){
#if defined(PORSCHE_FLOAT_OUTPUT_TRACE)
 W input[2]={*a,*b};StageTrace trace(2,input,24,a);
#endif
 const U ea=half(a,10)&0x7fff,eb=half(b,10)&0x7fff,sign=(half(a,10)^half(b,10))&0x8000;
 U exponent=ea+eb;W product{};
 auto zero=[&](){a->words[2]=0;a->words[1]=0;a->words[0]=0;};
 auto infinity=[&](){a->words[1]=0;a->words[0]=0;a->words[2]=(sign?0x80000000u:0u)+0x7fff8000u;};
 if(ea>=0x7fff||eb>=0x7fff||static_cast<std::uint16_t>(exponent)>0xbffd){infinity();return;}
 if(static_cast<std::uint16_t>(exponent)<=0x3fbf){zero();return;}
 if(!ea){++exponent;if(!(a->words[2]&0x7fffffffu)&&!a->words[1]&&!a->words[0]){half(a,10,0);return;}}
 if(!eb){++exponent;if(!(b->words[2]&0x7fffffffu)&&!b->words[1]&&!b->words[0]){zero();return;}}
 for(U i=0;i<5;++i)for(U j=0;j<5-i;++j){
  const U offset=i*2,term=static_cast<U>(half(a,(i+j)*2))*half(b,8-j*2);
  U current=word(&product,offset);
  const auto carry=formatter_float_add_word_005adaae(current,term,&current);word(&product,offset,current);
  if(carry)half(&product,offset+4,static_cast<std::uint16_t>(half(&product,offset+4)+1));
 }
 exponent+=0xc002;
 while(static_cast<std::int16_t>(exponent)>0&&!(product.words[2]&0x80000000u)){formatter_float_left96_005adb2d(&product);exponent+=0xffff;}
 if(static_cast<std::int16_t>(exponent)<=0){
  exponent+=0xffff;
  if(static_cast<std::int16_t>(exponent)<0){int n=-static_cast<std::int16_t>(exponent);exponent+=static_cast<U>(n);bool sticky=false;while(n--){sticky|=(product.words[0]&1)!=0;formatter_float_right96_005adb5b(&product);}if(sticky)product.words[0]|=1;}
 }
 if(half(&product,0)>0x8000||(product.words[0]&0x1ffffu)==0x18000){
  U low=word(&product,2),mid=word(&product,6);auto high=half(&product,10);
  if(low==0xffffffffu){low=0;if(mid==0xffffffffu){mid=0;if(high==0xffff){++exponent;high=0x8000;}else ++high;}else ++mid;}else ++low;
  word(&product,2,low);word(&product,6,mid);half(&product,10,high);
 }
 if(static_cast<std::uint16_t>(exponent)>=0x7fff){infinity();return;}
 half(a,0,half(&product,2));word(a,2,word(&product,4));word(a,6,word(&product,8));half(a,10,static_cast<std::uint16_t>(exponent|sign));
}
void __cdecl formatter_float_scale96_005ae17b(W* a,std::int32_t exponent,int retain_low){
 if(!exponent)return;
 const std::uint8_t* table=formatter_float_powers_positive_005e6380;
 U magnitude=static_cast<U>(exponent);if(exponent<0){magnitude=0u-magnitude;table=formatter_float_powers_negative_005e64e0;}
 if(!retain_low)half(a,0,0);
 for(U level=0;magnitude;magnitude>>=3,++level){const U index=magnitude&7;if(!index)continue;
  W factor;std::memcpy(&factor,table+level*84+(index-1)*12,12);
  if(half(&factor,0)>=0x8000)word(&factor,2,word(&factor,2)-1);
  formatter_float_multiply96_005adf5b(a,&factor);
 }
}
void __cdecl formatter_float_expand64_005abdcc(void* output,const void* input){
#if defined(PORSCHE_FLOAT_OUTPUT_TRACE)
 StageTrace trace(1,input,8,output);
#endif
 const U low=word(input,0),high=word(input,4),sign=high>>16&0x8000;
 const U raw=high>>20&0x7ff;U exponent,top=0x80000000u;
 if(!raw){if(!(high&0xfffff)&&!low){word(output,4,0);word(output,0,0);half(output,8,0);return;}exponent=0x3c01;top=0;}
 else exponent=raw==0x7ff?0x7fff:raw+0x3c00;
 U bottom=low<<11;top|=(low>>21)|((high&0xfffff)<<11);word(output,4,top);word(output,0,bottom);
 while(!(top&0x80000000u)){top=top*2|(bottom>>31);bottom*=2;word(output,0,bottom);word(output,4,top);exponent+=0xffff;}
 half(output,8,static_cast<std::uint16_t>(exponent|sign));
}
int __cdecl formatter_float_extended_digits_005adc4f(U low,U high,U sign_exponent,int precision,int flags,FormatterFloatDecimal28* out){
#if defined(PORSCHE_FLOAT_OUTPUT_TRACE)
 const U input[]={low,high,sign_exponent&0xffff,static_cast<U>(precision),static_cast<U>(flags)&255};StageTrace trace(3,input,20,out);
#endif
 const U exponent=sign_exponent&0x7fff;out->sign=(sign_exponent&0x8000)?'-':' ';
 auto zero=[&](){out->exponent=0;out->sign=' ';out->count=1;out->digits[0]='0';out->digits[1]=0;return 1;};
 if(!exponent&&!high&&!low)return zero();
 if(exponent==0x7fff){
  out->exponent=1;const char* text;
  if((high==0x80000000u&&!low)||(high&0x40000000u)){
   if((sign_exponent&0x8000)&&high==0xc0000000u&&!low)text="1#IND";
   else text=high==0x80000000u&&!low?"1#INF":"1#QNAN";
  }else text="1#SNAN";
  formatter_error_copy_005aa4e0(out->digits,text);out->count=(text[2]=='I')?5:6;return 0;
 }
 const U estimate=(exponent>>8)+((high>>24)*2);
 std::int16_t decimal=static_cast<std::int16_t>(static_cast<std::int32_t>(estimate*0x4d+exponent*0x4d10+0xecbced0cu)>>16);
 W value{};half(&value,0,0);word(&value,2,low);word(&value,6,high);half(&value,10,static_cast<std::uint16_t>(exponent));
 formatter_float_scale96_005ae17b(&value,-static_cast<int>(decimal),1);
 if(half(&value,10)>=0x3fff){++decimal;const W tenth={{0xccccccccu,0xccccccccu,0x3ffbccccu}};formatter_float_multiply96_005adf5b(&value,&tenth);}
 out->exponent=decimal;
 int count=precision;if(flags&1){count=static_cast<std::int32_t>(add_int(precision,decimal));if(count<=0)return zero();}if(count>21)count=21;
 const int shift=static_cast<int>(half(&value,10))-0x3ffe;half(&value,10,0);
 for(int i=0;i<8;++i)formatter_float_left96_005adb2d(&value);
 if(shift<0)for(U i=0;i<(static_cast<U>(-shift)&255);++i)formatter_float_right96_005adb5b(&value);
 char* cursor=out->digits;
 for(int i=0;i<count+1;++i){W saved=value;formatter_float_left96_005adb2d(&value);formatter_float_left96_005adb2d(&value);formatter_float_add96_005adacf(&value,&saved);formatter_float_left96_005adb2d(&value);const auto digit=static_cast<std::uint8_t>(value.words[2]>>24);value.words[2]&=0x00ffffffu;*cursor++=static_cast<char>(digit+'0');}
 int last=static_cast<int>(cursor-out->digits)-2;
 if(static_cast<signed char>(cursor[-1])>='5'){
  while(last>=0&&out->digits[last]=='9')out->digits[last--]='0';
  if(last<0){++last;++out->exponent;}++out->digits[last];
 }else {while(last>=0&&out->digits[last]=='0')--last;if(last<0)return zero();}
 out->count=static_cast<std::uint8_t>(last+1);out->digits[out->count]=0;return 1;
}
FormatterFloatDecimal16* __cdecl formatter_float_decimal_digits_005abd70(U low,U high,FormatterFloatDecimal16* out,char* digits){
 const U input[]={low,high};std::uint8_t extended[12];formatter_float_expand64_005abdcc(extended,input);
 FormatterFloatDecimal28 converted;out->status=formatter_float_extended_digits_005adc4f(word(extended,0),word(extended,4),half(extended,8),17,0,&converted);
 out->sign=static_cast<signed char>(converted.sign);out->exponent=converted.exponent;formatter_error_copy_005aa4e0(digits,converted.digits);out->digits=digits;return out;
}
void __cdecl formatter_float_round_digits_005abcf9(char* out,int count,FormatterFloatDecimal16* value){
#if defined(PORSCHE_FLOAT_OUTPUT_TRACE)
 const U input[]={static_cast<U>(count),static_cast<U>(value->sign),static_cast<U>(value->exponent)};StageTrace trace(4,input,12,out);trace.value=value;formatter_float_output_trace(4,2,value->digits,text_bytes(value->digits));
#endif
 char* original=out;const char* in=value->digits;*out++='0';char* first=out;
 if(count>0){int remaining=count;count=0;while(remaining--){char c=*in;if(c)++in;else c='0';*out++=c;}}
 *out=0;if(count>=0&&static_cast<signed char>(*in)>'4'){while(*--out=='9')*out='0';++*out;}
 if(*original=='1')++value->exponent;else context_move_005a1a40(original,first,formatter_strlen_005a6730(first)+1);
}
void __cdecl formatter_float_shift_text_005a4234(char* text,int count){if(count)context_move_005a1a40(text+count,text,formatter_strlen_005a6730(text)+1);}
char* __cdecl formatter_float_scientific_digits_005a3f92(char* out,int precision,int caps,FormatterFloatDecimal16* value,int general){
 if(static_cast<std::uint8_t>(general))formatter_float_shift_text_005a4234(out+(value->sign=='-'),precision>0);
 char* p=out;if(value->sign=='-')*p++='-';if(precision>0){*p=p[1];*++p=static_cast<char>(formatter_float_decimal_word_005e54e0);}
 p=formatter_error_copy_005aa4e0(p+precision+(static_cast<std::uint8_t>(general)==0),"e+000");if(caps)*p='E';
 if(*value->digits!='0'){int exponent=static_cast<std::int32_t>(static_cast<U>(value->exponent)-1);if(exponent<0){exponent=-exponent;p[1]='-';}if(exponent>=100){p[2]=static_cast<char>(p[2]+exponent/100);exponent%=100;}if(exponent>=10){p[3]=static_cast<char>(p[3]+exponent/10);exponent%=10;}p[4]=static_cast<char>(p[4]+exponent);}return out;
}
char* __cdecl formatter_float_fixed_digits_005a40a9(char* out,int precision,FormatterFloatDecimal16* value,int general){
 if(static_cast<std::uint8_t>(general)&&static_cast<U>(value->exponent)-1==static_cast<U>(precision)){char* p=out+(value->sign=='-')+value->exponent-1;p[0]='0';p[1]=0;}
 char* p=out;if(value->sign=='-')*p++='-';if(value->exponent<=0){formatter_float_shift_text_005a4234(p,1);*p++='0';}else p+=value->exponent;
 if(precision>0){formatter_float_shift_text_005a4234(p,1);*p++=static_cast<char>(formatter_float_decimal_word_005e54e0);int exponent=value->exponent;if(exponent<0){exponent=-exponent;if(static_cast<std::uint8_t>(general)||precision>=exponent)precision=exponent;formatter_float_shift_text_005a4234(p,precision);formatter_crt_memset_005abe90(p,'0',static_cast<U>(precision));}}return out;
}
char* __cdecl formatter_float_scientific_005a3f31(const void* number,char* out,int precision,int caps){
 U input[2];load_number(number,input);FormatterFloatDecimal16 value;char digits[24];formatter_float_decimal_digits_005abd70(input[0],input[1],&value,digits);
 formatter_float_round_digits_005abcf9(out+(value.sign=='-')+(precision>0),static_cast<std::int32_t>(static_cast<U>(precision)+1),&value);formatter_float_scientific_digits_005a3f92(out,precision,caps,&value,0);return out;
}
char* __cdecl formatter_float_fixed_005a4054(const void* number,char* out,int precision){
 U input[2];load_number(number,input);FormatterFloatDecimal16 value;char digits[24];formatter_float_decimal_digits_005abd70(input[0],input[1],&value,digits);
 formatter_float_round_digits_005abcf9(out+(value.sign=='-'),static_cast<std::int32_t>(add_int(value.exponent,precision)),&value);formatter_float_fixed_digits_005a40a9(out,precision,&value,0);return out;
}
char* __cdecl formatter_float_general_005a4150(const void* number,char* out,int precision,int caps){
 U input[2];load_number(number,input);FormatterFloatDecimal16 value;char digits[24];formatter_float_decimal_digits_005abd70(input[0],input[1],&value,digits);const int original=value.exponent-1;char* p=out+(value.sign=='-');formatter_float_round_digits_005abcf9(p,precision,&value);
 const int exponent=value.exponent-1;if(exponent< -4||exponent>=precision)return formatter_float_scientific_digits_005a3f92(out,precision,caps,&value,1);
 if(original<exponent){while(*p++){}p[-2]=0;}return formatter_float_fixed_digits_005a40a9(out,precision,&value,1);
}
}

#include "porsche/formatter_float_parse.hpp"

namespace porsche {
#if defined(PORSCHE_FLOAT_PARSE_TRACE)
void formatter_float_parse_trace(std::uint32_t,std::uint32_t,const void*,std::uint32_t);
#endif
namespace {
using U=std::uint32_t;
using W=FormatterFloatWords12;
#if defined(PORSCHE_FLOAT_PARSE_TRACE)
struct ParseTrace {
 U tag;const void* output;
 ParseTrace(U t,const void* input,U n,const void* out):tag(t),output(out) {formatter_float_parse_trace(tag,0,input,n);}
 ~ParseTrace() {formatter_float_parse_trace(tag,1,output,12);}
};
#endif
U shl(U x,int n) {return x<<(static_cast<U>(n)&31u);}
U shr(U x,int n) {return x>>(static_cast<U>(n)&31u);}
U read32(const void* p) {return *static_cast<const volatile U*>(p);}
std::uint16_t read16(const void* p) {return *static_cast<const volatile std::uint16_t*>(p);}
void write32(void* p,U v) {*static_cast<volatile U*>(p)=v;}
void write16(void* p,std::uint16_t v) {*static_cast<volatile std::uint16_t*>(p)=v;}
int digit(std::uint8_t c) {
    if(formatter_float_character_width_005e54dc>1)return formatter_float_classify_005a2eae(c,4);
    return *reinterpret_cast<const volatile std::uint8_t*>(formatter_ctype_table_005e52d0+c*2u)&4;
}
std::uint8_t character(const char* p) {return *reinterpret_cast<const volatile std::uint8_t*>(p);}
bool decimal(std::uint8_t c) {return c==static_cast<std::uint8_t>(formatter_float_decimal_word_005e54e0);}
}
int __cdecl formatter_float_tail_zero_005ab90d(const U* words,int bit) {
    int index=bit/32;
    if(read32(words+index)&~shl(0xffffffffu,31-bit%32))return 0;
    while(++index<3)if(read32(words+index))return 0;
    return 1;
}
U __cdecl formatter_float_bump_bit_005ab956(U* words,int bit) {
    int index=bit/32;
    U carry=formatter_float_add_word_005adaae(read32(words+index),shl(1,31-bit%32),words+index);
    while(--index>=0 && carry)carry=formatter_float_add_word_005adaae(read32(words+index),1,words+index);
    return carry;
}
int __cdecl formatter_float_round_words_005ab9ac(U* words,int bit) {
#if defined(PORSCHE_FLOAT_PARSE_TRACE)
 ParseTrace trace(1,words,12,words);formatter_float_parse_trace(1,2,&bit,4);
#endif
    const int index=bit/32,shift=31-bit%32;
    int carry=0;
    if((read32(words+index)&shl(1,shift)) && !formatter_float_tail_zero_005ab90d(words,bit+1))
        carry=static_cast<int>(formatter_float_bump_bit_005ab956(words,bit-1));
    write32(words+index,read32(words+index)&shl(0xffffffffu,shift));
    for(int i=index+1;i<3;++i)write32(words+i,0);
    return carry;
}
void __cdecl formatter_float_copy_words_005aba38(U* destination,const U* source) {
    for(unsigned i=0;i<3;++i)write32(destination+i,read32(source+i));
}
void __cdecl formatter_float_zero_words_005aba53(U* words) {for(unsigned i=0;i<3;++i)write32(words+i,0);}
int __cdecl formatter_float_words_zero_005aba5f(const U* words) {
    for(unsigned i=0;i<3;++i)if(read32(words+i))return 0;
    return 1;
}
void __cdecl formatter_float_shift_words_005aba7a(U* words,int bits) {
#if defined(PORSCHE_FLOAT_PARSE_TRACE)
 ParseTrace trace(2,words,12,words);formatter_float_parse_trace(2,2,&bits,4);
#endif
    const int quotient=bits/32,remainder=bits%32;
    const U mask=~shl(0xffffffffu,remainder);
    U carry=0;
    for(unsigned i=0;i<3;++i) {
        const U value=read32(words+i),low=value&mask;
        write32(words+i,shr(value,remainder)|carry);
        carry=shl(low,32-remainder);
    }
    for(int i=2;i>=0;--i)write32(words+i,i>=quotient?read32(words+i-quotient):0);
}
int __cdecl formatter_float_pack_words_005abb07(const W* input,void* output,const U* config) {
    const auto* raw=reinterpret_cast<const std::uint8_t*>(input);
    const U sign=read16(raw+10)&0x8000u;
    int exponent=static_cast<int>(read16(raw+10)&0x7fffu)-0x3fff;
    U words[3]={read32(raw+6),read32(raw+2),static_cast<U>(read16(raw))<<16};
    U saved[3],field=0;int result=0;
    if(exponent==-0x3fff) {
        if(!formatter_float_words_zero_005aba5f(words)) {formatter_float_zero_words_005aba53(words);result=2;}
    } else {
        formatter_float_copy_words_005aba38(saved,words);
        if(formatter_float_round_words_005ab9ac(words,static_cast<int>(read32(config+2))))++exponent;
        const int minimum=static_cast<int>(read32(config+1));
        if(exponent<static_cast<int>(static_cast<U>(minimum)-read32(config+2))) {
            formatter_float_zero_words_005aba53(words);result=2;
        } else if(exponent<=minimum) {
            const int shift=static_cast<int>(static_cast<U>(minimum)-static_cast<U>(exponent));
            formatter_float_copy_words_005aba38(words,saved);
            formatter_float_shift_words_005aba7a(words,shift);
            formatter_float_round_words_005ab9ac(words,static_cast<int>(read32(config+2)));
            formatter_float_shift_words_005aba7a(words,static_cast<int>(read32(config+3)+1));result=2;
        } else if(exponent>=static_cast<int>(read32(config))) {
            formatter_float_zero_words_005aba53(words);words[0]|=0x80000000u;
            formatter_float_shift_words_005aba7a(words,static_cast<int>(read32(config+3)));
            field=read32(config+5)+read32(config);result=1;
        } else {
            words[0]&=0x7fffffffu;field=read32(config+5)+static_cast<U>(exponent);
            formatter_float_shift_words_005aba7a(words,static_cast<int>(read32(config+3)));
        }
    }
    field=shl(field,31-static_cast<int>(read32(config+3)))|(sign?0x80000000u:0u)|words[0];
    const auto width=read32(config+4);
    if(width==64) {write32(static_cast<std::uint8_t*>(output)+4,field);write32(output,words[1]);}
    else if(width==32)write32(output,field);
    return result;
}
void __cdecl formatter_float_digits_words_005adb88(const char* digits,U count,W* output) {
#if defined(PORSCHE_FLOAT_PARSE_TRACE)
 ParseTrace trace(3,digits,count,output);formatter_float_parse_trace(3,2,&count,4);
#endif
    U exponent=0x404e;
    output->words[0]=output->words[1]=output->words[2]=0;
    while(count--) {
        W saved=*output;
        formatter_float_left96_005adb2d(output);formatter_float_left96_005adb2d(output);
        formatter_float_add96_005adacf(output,&saved);formatter_float_left96_005adb2d(output);
        saved.words[0]=static_cast<U>(static_cast<std::int32_t>(static_cast<signed char>(*digits++)));
        saved.words[1]=saved.words[2]=0;
        formatter_float_add96_005adacf(output,&saved);
    }
    while(!output->words[2]) {
        const U low=output->words[0],mid=output->words[1];
        output->words[2]=mid>>16;output->words[1]=(low>>16)|(mid<<16);output->words[0]=low<<16;exponent+=0xfff0;
    }
    while(!(output->words[2]&0x8000u)) {formatter_float_left96_005adb2d(output);exponent+=0xffff;}
    write16(reinterpret_cast<std::uint8_t*>(output)+10,static_cast<std::uint16_t>(exponent));
}
int __cdecl formatter_float_parse_words_005ac716(W* output,const char** end,const char* text,int retain_low,int no_exp_adjust,int no_dot_adjust,int implicit_exp) {
    const char* cursor=text;const char* rollback=text;
    std::uint8_t digits[28],c=0;U count=0,sign=0,adjust=0;
    int exp_sign=1,has_digit=0,has_dot=0,has_exp=0,explicit_exp=0,state=0,result=0;
    W value{};
    while(character(cursor)==32 || character(cursor)==9 || character(cursor)==10 || character(cursor)==13)++cursor;
next:
    c=character(cursor++);
    switch(state) {
    case 0:goto state0;case 1:goto state1;case 2:goto state2;case 3:goto state3;
    case 4:goto state4;case 5:goto state5;case 6:goto state6;case 7:goto state7;
    case 8:goto state8;case 9:goto state9;case 10:goto finish;case 11:goto state11;
    default:goto next;
    }
state0:
    if(static_cast<signed char>(c)>='1' && static_cast<signed char>(c)<='9') {state=3;--cursor;goto next;}
    if(decimal(c)) {state=5;goto next;}
    if(c=='-') {sign=0x8000;state=2;goto next;}
    if(c=='+') {sign=0;state=2;goto next;}
    if(c=='0') {state=1;goto next;}
    goto stop;
state1:
    has_digit=1;
    if(static_cast<signed char>(c)>='1' && static_cast<signed char>(c)<='9') {state=3;--cursor;goto next;}
    if(decimal(c)) {state=4;goto next;}
    if(c=='+' || c=='-') {--cursor;state=11;goto next;}
    if(c=='0') {state=1;goto next;}
    goto exponent_marker;
state2:
    if(static_cast<signed char>(c)>='1' && static_cast<signed char>(c)<='9') {state=3;--cursor;goto next;}
    if(decimal(c)) {state=5;goto next;}
    if(c=='0') {state=1;goto next;}
    goto rewind;
state3:
    has_digit=1;
    while(digit(c)) {
        if(count<25)digits[count++]=static_cast<std::uint8_t>(c-'0');else ++adjust;
        c=character(cursor++);
    }
    if(decimal(c)) {state=4;goto next;}
    goto after_digits;
state4:
    has_digit=1;has_dot=1;
    if(!count)while(c=='0') {--adjust;c=character(cursor++);}
    while(digit(c)) {
        if(count<25) {digits[count++]=static_cast<std::uint8_t>(c-'0');--adjust;}
        c=character(cursor++);
    }
after_digits:
    if(c=='+' || c=='-') {--cursor;state=11;goto next;}
exponent_marker:
    if((static_cast<signed char>(c)>'C' && static_cast<signed char>(c)<='E') ||
       (static_cast<signed char>(c)>'c' && static_cast<signed char>(c)<='e')) {state=6;goto next;}
    goto stop;
state5:
    has_dot=1;
    if(digit(c)) {state=4;--cursor;goto next;}
    goto rewind;
state6:
    rollback=cursor-2;
    if(static_cast<signed char>(c)>='1' && static_cast<signed char>(c)<='9') {state=9;--cursor;goto next;}
    if(c=='+') {state=7;goto next;}
    if(c=='-') {exp_sign=-1;state=7;goto next;}
    if(c=='0') {state=8;goto next;}
    cursor=rollback;goto finish;
state7:
    if(static_cast<signed char>(c)>='1' && static_cast<signed char>(c)<='9') {state=9;--cursor;goto next;}
    if(c=='0') {state=8;goto next;}
    goto rewind;
state8:
    has_exp=1;
    while(c=='0')c=character(cursor++);
    if(static_cast<signed char>(c)>='1' && static_cast<signed char>(c)<='9') {state=9;--cursor;goto next;}
    goto stop;
state9:
    has_exp=1;explicit_exp=0;
    while(digit(c)) {
        explicit_exp=static_cast<int>(static_cast<U>(static_cast<signed char>(c))+static_cast<U>(explicit_exp)*10u-0x30u);
        if(explicit_exp>5200) {explicit_exp=5201;break;}
        c=character(cursor++);
    }
    while(digit(c))c=character(cursor++);
    goto stop;
state11:
    if(!implicit_exp) {--cursor;goto finish;}
    rollback=cursor-1;
    if(c=='+') {state=7;goto next;}
    if(c=='-') {exp_sign=-1;state=7;goto next;}
    cursor=rollback;goto finish;
rewind:
    cursor=rollback;goto finish;
stop:
    --cursor;
finish:
    *end=cursor;
    if(!has_digit) {result=4;goto store;}
    if(count>24) {
        if(static_cast<signed char>(digits[23])>=5)++digits[23];
        count=24;++adjust;
    }
    if(!count)goto store;
    while(!digits[count-1]) {--count;++adjust;}
    formatter_float_digits_words_005adb88(reinterpret_cast<const char*>(digits),count,&value);
    {
        U exponent=(exp_sign<0?0u-static_cast<U>(explicit_exp):static_cast<U>(explicit_exp))+adjust;
        if(!has_exp)exponent+=static_cast<U>(no_exp_adjust);
        if(!has_dot)exponent-=static_cast<U>(no_dot_adjust);
        if(static_cast<int>(exponent)>5200) {value.words[0]=0;value.words[1]=0;value.words[2]=0x7fff8000;result=2;}
        else if(static_cast<int>(exponent)<-5200) {value.words[0]=value.words[1]=value.words[2]=0;result=1;}
        else {
#if defined(PORSCHE_FLOAT_PARSE_TRACE)
            const U input[]={value.words[0],value.words[1],value.words[2],exponent,static_cast<U>(retain_low)};
            ParseTrace trace(4,input,20,&value);
#endif
            formatter_float_scale96_005ae17b(&value,static_cast<int>(exponent),retain_low);
        }
    }
store:
    auto* raw=reinterpret_cast<std::uint8_t*>(output);
    write32(raw+6,read32(reinterpret_cast<const std::uint8_t*>(&value)+6));
    write32(raw+2,read32(reinterpret_cast<const std::uint8_t*>(&value)+2));
    write16(raw+10,static_cast<std::uint16_t>(read16(reinterpret_cast<const std::uint8_t*>(&value)+10)|sign));
    write16(raw,read16(&value));
    return result;
}
}

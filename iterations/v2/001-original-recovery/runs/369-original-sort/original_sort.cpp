#include "porsche/window_handlers.hpp"
#include <cstdint>

namespace porsche {
// Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// Exact consumers: 005a112b quicksort, 005a127f shortsort, 005a12cd byte swap.
// Integer addresses preserve the original unsigned comparisons and byte offsets.
static_assert(sizeof(std::uintptr_t)==4,"original sort requires x86 addresses");
using Address=std::uintptr_t;
using Compare=std::int32_t(__cdecl*)(const void*,const void*);

void __cdecl original_sort_swap_005a12cd(void* a,void* b,std::uint32_t bytes) {
    if(a==b)return;
    auto* left=static_cast<unsigned char*>(a);
    auto* right=static_cast<unsigned char*>(b);
    while(bytes--) {
        const auto saved=*left;
        *left++=*right;
        *right++=saved;
    }
}

void __cdecl original_sort_short_005a127f(Address low,Address high,
                                         std::uint32_t width,Compare compare) {
    while(low<high) {
        Address maximum=low;
        for(Address candidate=low+width;candidate<=high;candidate+=width)
            if(compare(reinterpret_cast<const void*>(candidate),
                       reinterpret_cast<const void*>(maximum))>0)maximum=candidate;
        original_sort_swap_005a12cd(reinterpret_cast<void*>(maximum),
                                  reinterpret_cast<void*>(high),width);
        high-=width;
    }
}

void __cdecl window_handler_sort_005a112b(void* base,std::uint32_t count,
                                         std::uint32_t width,Compare compare) {
    if(count<2 || width==0)return;
    Address lows[30],highs[30];
    std::uint32_t pending=0;
    Address low=reinterpret_cast<Address>(base);
    Address high=low+(count-1u)*width;
    for(;;) {
        const std::uint32_t size=(high-low)/width+1u;
        if(size<=8) {
            original_sort_short_005a127f(low,high,width,compare);
        } else {
            original_sort_swap_005a12cd(reinterpret_cast<void*>(low+(size>>1)*width),
                                      reinterpret_cast<void*>(low),width);
            Address left=low,right=high+width;
            for(;;) {
                do {left+=width;}
                while(left<=high && compare(reinterpret_cast<const void*>(left),
                                           reinterpret_cast<const void*>(low))<=0);
                do {right-=width;}
                while(right>low && compare(reinterpret_cast<const void*>(right),
                                          reinterpret_cast<const void*>(low))>=0);
                if(left>right)break;
                original_sort_swap_005a12cd(reinterpret_cast<void*>(left),
                                          reinterpret_cast<void*>(right),width);
            }
            original_sort_swap_005a12cd(reinterpret_cast<void*>(low),
                                      reinterpret_cast<void*>(right),width);
            // Original 005a1213/16 compares SIGNED wrapping byte differences.
            if(static_cast<std::int32_t>((right-low)-1u)<
               static_cast<std::int32_t>(high-left)) {
                if(left<high) {lows[pending]=left;highs[pending]=high;++pending;}
                if(low+width<right) {high=right-width;continue;}
            } else {
                if(low+width<right) {lows[pending]=low;highs[pending]=right-width;++pending;}
                if(left<high) {low=left;continue;}
            }
        }
        if(pending==0)return;
        --pending;low=lows[pending];high=highs[pending];
    }
}
}

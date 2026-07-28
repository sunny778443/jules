; kernel/entry.asm
bits 64

global _start
extern kernel_main

section .entry
_start:
    ; Set up a clean, 16-byte aligned stack.
    mov rsp, stack_top
    mov rbp, rsp

    ; Push 0 as return address to terminate stack traces
    push 0
    push 0

    ; Call kernel_main with BootInfo* in RDI
    call kernel_main

.halt:
    cli
    hlt
    jmp .halt

section .bootstrap_stack nobits
stack_bottom:
    resb 65536 ; 64 KB stack
stack_top:

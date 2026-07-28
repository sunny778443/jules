#include "font.h"
#include "../bootloader/efi.h" // reuse BootInfo structure

// Screen/Console globals
static BootInfo *g_boot_info = NULL;
static uint32_t g_cursor_x = 0;
static uint32_t g_cursor_y = 0;

// Color definition (ARGB8888 standard format)
#define COLOR_WHITE   0x00FFFFFF
#define COLOR_BLUE    0x001F4F7F
#define COLOR_BLACK   0x00000000
#define COLOR_GREEN   0x004CAF50
#define COLOR_ORANGE  0x00FF9800

// Serial output functions (COM1)
static void serial_write_char(char c) {
    volatile uint16_t port = 0x3FD;
    uint8_t status = 0;
    do {
        __asm__ volatile("inb %1, %0" : "=a"(status) : "Nd"(port));
    } while ((status & 0x20) == 0);

    port = 0x3F8;
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)c), "Nd"(port));
}

static void serial_write_str(const char *str) {
    while (*str) {
        if (*str == '\n') {
            serial_write_char('\r');
        }
        serial_write_char(*str);
        str++;
    }
}

// Low-level Framebuffer drawing functions
static void draw_pixel(uint32_t x, uint32_t y, uint32_t color) {
    if (!g_boot_info) return;
    if (x >= g_boot_info->HorizontalResolution || y >= g_boot_info->VerticalResolution) return;

    uint32_t *fb = (uint32_t*)g_boot_info->FrameBufferBase;
    fb[y * g_boot_info->PixelsPerScanLine + x] = color;
}

// Draw a filled rectangle
static void draw_rect(uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint32_t color) {
    for (uint32_t j = 0; j < h; j++) {
        for (uint32_t i = 0; i < w; i++) {
            draw_pixel(x + i, y + j, color);
        }
    }
}

// Draw a character using the 8x16 font
static void draw_char(char c, uint32_t x, uint32_t y, uint32_t fg_color, uint32_t bg_color, int draw_bg) {
    uint8_t uc = (uint8_t)c;
    for (int row = 0; row < 16; row++) {
        uint8_t byte = font_8x16[uc][row];
        for (int col = 0; col < 8; col++) {
            if (byte & (0x80 >> col)) {
                draw_pixel(x + col, y + row, fg_color);
            } else if (draw_bg) {
                draw_pixel(x + col, y + row, bg_color);
            }
        }
    }
}

// Scroll screen by 16 pixels
static void scroll_screen(uint32_t bg_color) {
    if (!g_boot_info) return;
    uint32_t *fb = (uint32_t*)g_boot_info->FrameBufferBase;
    uint32_t scanline = g_boot_info->PixelsPerScanLine;
    uint32_t width = g_boot_info->HorizontalResolution;
    uint32_t height = g_boot_info->VerticalResolution;

    for (uint32_t y = 48; y < height; y++) {
        for (uint32_t x = 0; x < width; x++) {
            fb[(y - 16) * scanline + x] = fb[y * scanline + x];
        }
    }
    draw_rect(0, height - 16, width, 16, bg_color);
}

// Custom simple formatted printf-style kernel logger
void kprint_char(char c) {
    if (c == '\n') {
        serial_write_char('\r');
    }
    serial_write_char(c);

    if (!g_boot_info) return;

    if (c == '\n') {
        g_cursor_x = 0;
        g_cursor_y += 16;
        if (g_cursor_y + 16 >= g_boot_info->VerticalResolution) {
            scroll_screen(COLOR_BLACK);
            g_cursor_y -= 16;
        }
        return;
    }
    if (c == '\r') {
        g_cursor_x = 0;
        return;
    }

    draw_char(c, g_cursor_x, g_cursor_y, COLOR_WHITE, COLOR_BLACK, 1);
    g_cursor_x += 8;

    if (g_cursor_x + 8 >= g_boot_info->HorizontalResolution) {
        g_cursor_x = 0;
        g_cursor_y += 16;
        if (g_cursor_y + 16 >= g_boot_info->VerticalResolution) {
            scroll_screen(COLOR_BLACK);
            g_cursor_y -= 16;
        }
    }
}

void kprintf(const char *fmt, ...) {
    __builtin_va_list args;
    __builtin_va_start(args, fmt);

    while (*fmt) {
        if (*fmt == '%' && *(fmt + 1)) {
            fmt++;
            if (*fmt == 's') {
                const char *str = __builtin_va_arg(args, const char *);
                while (*str) {
                    kprint_char(*str++);
                }
            } else if (*fmt == 'd' || *fmt == 'i') {
                int val = __builtin_va_arg(args, int);
                if (val < 0) {
                    kprint_char('-');
                    val = -val;
                }
                char buf[32];
                int i = 0;
                if (val == 0) {
                    buf[i++] = '0';
                } else {
                    while (val > 0) {
                        buf[i++] = '0' + (val % 10);
                        val /= 10;
                    }
                }
                for (int j = i - 1; j >= 0; j--) {
                    kprint_char(buf[j]);
                }
            } else if (*fmt == 'x' || *fmt == 'p') {
                uint64_t val;
                if (*fmt == 'p') {
                    val = (uint64_t)__builtin_va_arg(args, void*);
                    kprint_char('0');
                    kprint_char('x');
                } else {
                    val = __builtin_va_arg(args, uint32_t);
                }
                char buf[32];
                int i = 0;
                if (val == 0) {
                    buf[i++] = '0';
                } else {
                    const char *hex = "0123456789abcdef";
                    while (val > 0) {
                        buf[i++] = hex[val & 0xF];
                        val >>= 4;
                    }
                }
                for (int j = i - 1; j >= 0; j--) {
                    kprint_char(buf[j]);
                }
            } else {
                kprint_char('%');
                kprint_char(*fmt);
            }
        } else {
            kprint_char(*fmt);
        }
        fmt++;
    }

    __builtin_va_end(args);
}

// Primary Kernel Entry Point
void kernel_main(BootInfo *info) {
    g_boot_info = info;
    g_cursor_x = 0;
    g_cursor_y = 48; // leave space from top

    // Clear entire screen to beautiful dark background
    draw_rect(0, 0, info->HorizontalResolution, info->VerticalResolution, COLOR_BLACK);

    // Draw top banner
    draw_rect(0, 0, info->HorizontalResolution, 32, COLOR_BLUE);

    // Print banner title using manual positioning
    const char *banner_text = "SunnyOS 64-bit Core Kernel v1.0 [Milestone 1]";
    uint32_t banner_x = 16;
    for (int i = 0; banner_text[i] != '\0'; i++) {
        draw_char(banner_text[i], banner_x, 8, COLOR_WHITE, COLOR_BLUE, 0);
        banner_x += 8;
    }

    // Print welcome and diagnostic logs to kernel screen and serial
    kprintf("\n[KERNEL] SunnyOS Kernel booted successfully via UEFI.\n");
    kprintf("[KERNEL] Executing inside 64-bit long mode.\n");
    kprintf("[KERNEL] System Information:\n");
    kprintf("  - Framebuffer Base Address: %p\n", (void*)info->FrameBufferBase);
    kprintf("  - Framebuffer Size: %d bytes\n", info->FrameBufferSize);
    kprintf("  - Active Resolution: %dx%d (PixelsPerScanLine: %d)\n",
            info->HorizontalResolution, info->VerticalResolution, info->PixelsPerScanLine);
    kprintf("  - Memory Map Address: %p\n", (void*)info->MemoryMapAddr);
    kprintf("  - Memory Map Size: %d bytes\n", info->MemoryMapSize);
    kprintf("  - UEFI System Table Address: %p\n", (void*)info->SystemTable);

    kprintf("\n[KERNEL] AI-Native OS Platform Layer Bootstrapped.\n");
    kprintf("[KERNEL] Basic kernel structures loaded. System is fully operational.\n");
    kprintf("[KERNEL] Entering low-power CPU halt state...\n");

    serial_write_str("[KERNEL] Diagnostics completed successfully.\n");

    // Loop infinitely
    while (1) {
        __asm__ volatile("hlt");
    }
}

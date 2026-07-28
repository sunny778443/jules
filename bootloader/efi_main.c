#include "efi.h"

// Convert a number to hex string (wide char)
static void hex_to_str(uint64_t val, CHAR16 *buf) {
    CHAR16 hex_chars[] = L"0123456789ABCDEF";
    buf[0] = '0';
    buf[1] = 'x';
    for (int i = 0; i < 16; i++) {
        buf[2 + (15 - i)] = hex_chars[(val >> (i * 4)) & 0xF];
    }
    buf[18] = '\0';
}

// Helper to print a string to UEFI ConOut
static void print_str(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *con_out, const CHAR16 *str) {
    con_out->OutputString(con_out, str);
}

// Helper to print a newline
static void print_nl(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *con_out) {
    print_str(con_out, L"\r\n");
}

// Write to COM1 Serial Port for headless verification / logging
static void write_serial_char(char c) {
    #ifdef __GNUC__
    volatile uint16_t port = 0x3FD;
    uint8_t status = 0;
    do {
        __asm__ volatile("inb %1, %0" : "=a"(status) : "Nd"(port));
    } while ((status & 0x20) == 0);

    port = 0x3F8;
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)c), "Nd"(port));
    #else
    (void)c;
    #endif
}

static void write_serial_str(const char *str) {
    while (*str) {
        if (*str == '\n') {
            write_serial_char('\r');
        }
        write_serial_char(*str);
        str++;
    }
}

// Initialize serial port (COM1)
static void init_serial(void) {
    #ifdef __GNUC__
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)0x00), "Nd"((uint16_t)0x3F9));
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)0x80), "Nd"((uint16_t)0x3FC));
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)0x03), "Nd"((uint16_t)0x3F8));
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)0x00), "Nd"((uint16_t)0x3F9));
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)0x03), "Nd"((uint16_t)0x3FC));
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)0xC7), "Nd"((uint16_t)0x3FA));
    __asm__ volatile("outb %0, %1" : : "a"((uint8_t)0x0B), "Nd"((uint16_t)0x3FC));
    #endif
}

static void print_hex(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *con_out, uint64_t val) {
    CHAR16 buf[20];
    hex_to_str(val, buf);
    print_str(con_out, buf);
}

// EFI Entry point
EFI_STATUS efi_main(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable) {
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *con_out = SystemTable->ConOut;
    EFI_BOOT_SERVICES *bs = SystemTable->BootServices;

    // Initialize serial port first
    init_serial();
    write_serial_str("[UEFI] COM1 Serial logging initialized.\n");

    // Clear screen
    con_out->ClearScreen(con_out);

    // Beautiful ASCII Boot Logo
    print_str(con_out, L"====================================================\r\n");
    print_str(con_out, L"   SSSSS  U   U  N   N  N   N  Y   Y   OOO   SSSSS  \r\n");
    print_str(con_out, L"  S       U   U  NN  N  NN  N   Y Y   O   O S       \r\n");
    print_str(con_out, L"   SSS    U   U  N N N  N N N    Y    O   O  SSS    \r\n");
    print_str(con_out, L"      S   U   U  N  NN  N  NN    Y    O   O     S   \r\n");
    print_str(con_out, L"  SSSSS    UUU   N   N  N   N    Y     OOO  SSSSS   \r\n");
    print_str(con_out, L"====================================================\r\n");
    print_str(con_out, L"               AI-Native Operating System           \r\n");
    print_str(con_out, L"====================================================\r\n");
    print_nl(con_out);

    write_serial_str("====================================================\n");
    write_serial_str("   SSSSS  U   U  N   N  N   N  Y   Y   OOO   SSSSS  \n");
    write_serial_str("  S       U   U  NN  N  NN  N   Y Y   O   O S       \n");
    write_serial_str("   SSS    U   U  N N N  N N N    Y    O   O  SSS    \n");
    write_serial_str("      S   U   U  N  NN  N  NN    Y    O   O     S   \n");
    write_serial_str("  SSSSS    UUU   N   N  N   N    Y     OOO  SSSSS   \n");
    write_serial_str("====================================================\n");
    write_serial_str("               AI-Native Operating System           \n");
    write_serial_str("====================================================\n\n");

    print_str(con_out, L"[UEFI] Starting SunnyOS Bootloader...\r\n");
    write_serial_str("[UEFI] Starting SunnyOS Bootloader...\n");

    // 1. Diagnostics - CPU Vendor
    print_str(con_out, L"[UEFI] Performing Diagnostics...\r\n");
    write_serial_str("[UEFI] Performing Diagnostics...\n");
    #ifdef __GNUC__
    uint32_t eax = 0, ebx = 0, ecx = 0, edx = 0;
    __asm__ volatile("cpuid"
                     : "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
                     : "a"(0));
    char vendor[13];
    *(uint32_t*)&vendor[0] = ebx;
    *(uint32_t*)&vendor[4] = edx;
    *(uint32_t*)&vendor[8] = ecx;
    vendor[12] = '\0';

    print_str(con_out, L"  - CPU Vendor String: ");
    write_serial_str("  - CPU Vendor String: ");
    CHAR16 wvendor[13];
    for (int i = 0; i < 12; i++) {
        wvendor[i] = (CHAR16)vendor[i];
    }
    wvendor[12] = '\0';
    print_str(con_out, wvendor);
    print_nl(con_out);
    write_serial_str(vendor);
    write_serial_str("\n");
    #endif

    // 2. Query Graphics Output Protocol (GOP)
    print_str(con_out, L"[UEFI] Locating Graphics Output Protocol...\r\n");
    write_serial_str("[UEFI] Locating Graphics Output Protocol...\n");
    EFI_GUID gop_guid = EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
    EFI_GRAPHICS_OUTPUT_PROTOCOL *gop = NULL;
    EFI_STATUS status = bs->LocateProtocol(&gop_guid, NULL, (void**)&gop);
    if (status != EFI_SUCCESS || gop == NULL) {
        print_str(con_out, L"  - ERROR: Failed to locate GOP!\r\n");
        write_serial_str("  - ERROR: Failed to locate GOP!\n");
        return status;
    }

    print_str(con_out, L"  - GOP Framebuffer Base: ");
    print_hex(con_out, gop->Mode->FrameBufferBase);
    print_nl(con_out);
    write_serial_str("  - GOP Framebuffer Base: ");
    {
        char fb_str[32];
        uint64_t val = gop->Mode->FrameBufferBase;
        fb_str[0] = '0'; fb_str[1] = 'x';
        for (int i = 0; i < 16; i++) {
            fb_str[2 + (15 - i)] = "0123456789ABCDEF"[(val >> (i * 4)) & 0xF];
        }
        fb_str[18] = '\0';
        write_serial_str(fb_str);
        write_serial_str("\n");
    }

    print_str(con_out, L"  - GOP Resolution: ");
    print_hex(con_out, gop->Mode->Info->HorizontalResolution);
    print_str(con_out, L"x");
    print_hex(con_out, gop->Mode->Info->VerticalResolution);
    print_nl(con_out);

    // 3. File System: Open Simple File System Protocol
    print_str(con_out, L"[UEFI] Loading Kernel (kernel.bin)...\r\n");
    write_serial_str("[UEFI] Loading Kernel (kernel.bin)...\n");

    EFI_GUID loaded_image_guid = EFI_LOADED_IMAGE_PROTOCOL_GUID;
    EFI_LOADED_IMAGE_PROTOCOL *loaded_image = NULL;
    status = bs->HandleProtocol(ImageHandle, &loaded_image_guid, (void**)&loaded_image);
    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - ERROR: Failed to get Loaded Image Protocol!\r\n");
        write_serial_str("  - ERROR: Failed to get Loaded Image Protocol!\n");
        return status;
    }

    EFI_GUID sfsp_guid = EFI_SIMPLE_FILE_SYSTEM_PROTOCOL_GUID;
    EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *sfsp = NULL;
    status = bs->HandleProtocol(loaded_image->DeviceHandle, &sfsp_guid, (void**)&sfsp);
    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - DeviceHandle FS failed. Trying global LocateProtocol...\r\n");
        write_serial_str("  - DeviceHandle FS failed. Trying global LocateProtocol...\n");
        status = bs->LocateProtocol(&sfsp_guid, NULL, (void**)&sfsp);
    }
    if (status != EFI_SUCCESS || sfsp == NULL) {
        print_str(con_out, L"  - ERROR: Failed to get Simple File System Protocol!\r\n");
        write_serial_str("  - ERROR: Failed to get Simple File System Protocol!\n");
        return status;
    }

    EFI_FILE_PROTOCOL *root_dir = NULL;
    status = sfsp->OpenVolume(sfsp, &root_dir);
    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - ERROR: Failed to open root volume!\r\n");
        write_serial_str("  - ERROR: Failed to open root volume!\n");
        return status;
    }

    EFI_FILE_PROTOCOL *kernel_file = NULL;
    status = root_dir->Open(root_dir, &kernel_file, L"kernel.bin", EFI_FILE_MODE_READ, 0);
    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - ERROR: Failed to open kernel.bin on disk!\r\n");
        write_serial_str("  - ERROR: Failed to open kernel.bin on disk!\n");
        return status;
    }

    // Allocate a temporary memory buffer anywhere to load the kernel into
    uint64_t temp_kernel_addr = 0;
    UINTN pages_to_allocate = 128; // 512 KB of kernel space
    status = bs->AllocatePages(AllocateAnyPages, EfiLoaderData, pages_to_allocate, &temp_kernel_addr);
    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - ERROR: Failed to allocate pages for kernel!\r\n");
        write_serial_str("  - ERROR: Failed to allocate pages for kernel!\n");
        return status;
    }

    print_str(con_out, L"  - Temp Kernel Buffer allocated at: ");
    print_hex(con_out, temp_kernel_addr);
    print_nl(con_out);

    // Read kernel file into the temporary buffer
    UINTN buffer_size = pages_to_allocate * 4096;
    status = kernel_file->Read(kernel_file, &buffer_size, (void*)temp_kernel_addr);
    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - ERROR: Failed to read kernel.bin!\r\n");
        write_serial_str("  - ERROR: Failed to read kernel.bin!\n");
        return status;
    }

    print_str(con_out, L"  - Loaded ");
    print_hex(con_out, buffer_size);
    print_str(con_out, L" bytes of kernel.bin.\r\n");
    write_serial_str("  - Loaded kernel.bin successfully into temporary buffer.\n");

    kernel_file->Close(kernel_file);
    root_dir->Close(root_dir);

    // 4. Retrieve Memory Map and Exit Boot Services
    print_str(con_out, L"[UEFI] Retrieving Memory Map and exiting boot services...\r\n");
    write_serial_str("[UEFI] Retrieving Memory Map and exiting boot services...\n");

    UINTN memory_map_size = 0;
    EFI_MEMORY_DESCRIPTOR *memory_map = NULL;
    UINTN map_key = 0;
    UINTN descriptor_size = 0;
    UINT32 descriptor_version = 0;

    // Call once to get required buffer size
    bs->GetMemoryMap(&memory_map_size, NULL, &map_key, &descriptor_size, &descriptor_version);

    // Add extra space to accommodate map growth during allocation
    memory_map_size += 8 * descriptor_size;
    status = bs->AllocatePool(EfiLoaderData, memory_map_size, (void**)&memory_map);
    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - ERROR: Failed to allocate memory for Memory Map!\r\n");
        write_serial_str("  - ERROR: Failed to allocate memory for Memory Map!\n");
        return status;
    }

    // Now get the actual memory map
    status = bs->GetMemoryMap(&memory_map_size, memory_map, &map_key, &descriptor_size, &descriptor_version);
    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - ERROR: Failed to get Memory Map!\r\n");
        write_serial_str("  - ERROR: Failed to get Memory Map!\n");
        return status;
    }

    // Package Boot Information
    BootInfo boot_info;
    boot_info.FrameBufferBase = gop->Mode->FrameBufferBase;
    boot_info.FrameBufferSize = gop->Mode->FrameBufferSize;
    boot_info.HorizontalResolution = gop->Mode->Info->HorizontalResolution;
    boot_info.VerticalResolution = gop->Mode->Info->VerticalResolution;
    boot_info.PixelsPerScanLine = gop->Mode->Info->PixelsPerScanLine;
    boot_info.PixelFormat = (uint32_t)gop->Mode->Info->PixelFormat;
    boot_info.MemoryMapAddr = (uint64_t)memory_map;
    boot_info.MemoryMapSize = memory_map_size;
    boot_info.DescriptorSize = descriptor_size;
    boot_info.SystemTable = (uint64_t)SystemTable;

    // Call ExitBootServices IMMEDIATELY without any debug logging/printing between GetMemoryMap and ExitBootServices
    status = bs->ExitBootServices(ImageHandle, map_key);
    if (status != EFI_SUCCESS) {
        // If exiting failed (e.g. map_key changed due to background activity), re-query memory map size and key immediately
        memory_map_size = 0;
        bs->GetMemoryMap(&memory_map_size, NULL, &map_key, &descriptor_size, &descriptor_version);
        memory_map_size += 8 * descriptor_size;

        bs->FreePool(memory_map);
        status = bs->AllocatePool(EfiLoaderData, memory_map_size, (void**)&memory_map);
        if (status == EFI_SUCCESS) {
            status = bs->GetMemoryMap(&memory_map_size, memory_map, &map_key, &descriptor_size, &descriptor_version);
            if (status == EFI_SUCCESS) {
                boot_info.MemoryMapAddr = (uint64_t)memory_map;
                boot_info.MemoryMapSize = memory_map_size;
                boot_info.DescriptorSize = descriptor_size;

                status = bs->ExitBootServices(ImageHandle, map_key);
            }
        }
    }

    if (status != EFI_SUCCESS) {
        print_str(con_out, L"  - ERROR: ExitBootServices failed permanently!\r\n");
        write_serial_str("  - ERROR: ExitBootServices failed permanently!\n");
        return status;
    }

    // 5. Jump to Kernel
    // At this point, UEFI Boot Services are completely disabled! We are in full control.
    // Copy the kernel from its temporary address to its linked target physical address 0x1000000 (16 MB)
    uint8_t *src = (uint8_t*)temp_kernel_addr;
    uint8_t *dst = (uint8_t*)0x1000000;
    for (UINTN i = 0; i < buffer_size; i++) {
        dst[i] = src[i];
    }

    write_serial_str("[UEFI] Left Boot Services. Kernel relocated to 0x1000000. Jumping...\n");

    // Call the kernel entry point at 0x1000000
    typedef void (__attribute__((sysv_abi)) *KernelEntryPoint)(BootInfo *info);
    KernelEntryPoint entry = (KernelEntryPoint)0x1000000;

    entry(&boot_info);

    // Should never be reached
    while (1) {
        #ifdef __GNUC__
        __asm__ volatile("hlt");
        #endif
    }

    return EFI_SUCCESS;
}

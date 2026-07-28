#ifndef EFI_H
#define EFI_H

#include <stdint.h>
#include <stddef.h>

// Basic UEFI Types
typedef uint64_t UINTN;
typedef int64_t  INTN;
typedef uint8_t  UINT8;
typedef uint16_t UINT16;
typedef uint32_t UINT32;
typedef uint64_t UINT64;
typedef uint8_t  CHAR8;
typedef uint16_t CHAR16;
typedef void*    EFI_HANDLE;
typedef UINTN    EFI_STATUS;

#define EFI_SUCCESS           0
#define EFI_ERR               0x8000000000000000ULL
#define EFI_LOAD_ERROR        (EFI_ERR | 1)
#define EFI_INVALID_PARAMETER (EFI_ERR | 2)
#define EFI_UNSUPPORTED       (EFI_ERR | 3)
#define EFI_BAD_BUFFER_SIZE   (EFI_ERR | 4)
#define EFI_BUFFER_TOO_SMALL  (EFI_ERR | 5)
#define EFI_NOT_READY         (EFI_ERR | 6)
#define EFI_NOT_FOUND         (EFI_ERR | 14)

#define EFI_FILE_MODE_READ    0x0000000000000001ULL

// GUID structure
typedef struct {
    UINT32 Data1;
    UINT16 Data2;
    UINT16 Data3;
    UINT8  Data4[8];
} EFI_GUID;

#define EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID \
    { 0x9042a9de, 0x23dc, 0x4a38, { 0x96, 0xfb, 0x7a, 0xde, 0xd0, 0x80, 0x51, 0x6a } }

#define EFI_LOADED_IMAGE_PROTOCOL_GUID \
    { 0x5b1b31a1, 0x9562, 0x11d2, { 0x8e, 0x3f, 0x00, 0xa0, 0xc9, 0x69, 0x72, 0x3b } }

#define EFI_SIMPLE_FILE_SYSTEM_PROTOCOL_GUID \
    { 0x964e5b22, 0x6459, 0x11d2, { 0x8e, 0x39, 0x00, 0xa0, 0xc9, 0x69, 0x72, 0x3b } }

// Forward declarations
struct _EFI_SIMPLE_TEXT_INPUT_PROTOCOL;
struct _EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL;
struct _EFI_SYSTEM_TABLE;

// Simple Text Input
typedef struct _EFI_INPUT_KEY {
    UINT16 ScanCode;
    CHAR16 UnicodeChar;
} EFI_INPUT_KEY;

typedef EFI_STATUS (/* EFIAPI */ *EFI_INPUT_RESET) (
    struct _EFI_SIMPLE_TEXT_INPUT_PROTOCOL *This,
    uint8_t ExtendedVerification
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_INPUT_READ_KEY) (
    struct _EFI_SIMPLE_TEXT_INPUT_PROTOCOL *This,
    EFI_INPUT_KEY *Key
);

typedef struct _EFI_SIMPLE_TEXT_INPUT_PROTOCOL {
    EFI_INPUT_RESET    Reset;
    EFI_INPUT_READ_KEY ReadKeyStroke;
    void*              WaitForKey;
} EFI_SIMPLE_TEXT_INPUT_PROTOCOL;

// Simple Text Output
typedef struct _EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL;

typedef EFI_STATUS (/* EFIAPI */ *EFI_TEXT_RESET) (
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,
    uint8_t ExtendedVerification
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_TEXT_STRING) (
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,
    const CHAR16 *String
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_TEXT_TEST_STRING) (
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,
    const CHAR16 *String
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_TEXT_QUERY_MODE) (
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,
    UINTN ModeNumber,
    UINTN *Columns,
    UINTN *Rows
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_TEXT_SET_MODE) (
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,
    UINTN ModeNumber
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_TEXT_SET_ATTRIBUTE) (
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This,
    UINTN Attribute
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_TEXT_CLEAR_SCREEN) (
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *This
);

struct _EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL {
    EFI_TEXT_RESET           Reset;
    EFI_TEXT_STRING          OutputString;
    EFI_TEXT_TEST_STRING     TestString;
    EFI_TEXT_QUERY_MODE      QueryMode;
    EFI_TEXT_SET_MODE        SetMode;
    EFI_TEXT_SET_ATTRIBUTE   SetAttribute;
    EFI_TEXT_CLEAR_SCREEN    ClearScreen;
    void*                    SetCursorPosition;
    void*                    EnableCursor;
    void*                    Mode;
};

// Graphics Output Protocol
typedef enum {
    PixelRedGreenBlueReserved8BitPerColor,
    PixelBlueGreenRedReserved8BitPerColor,
    PixelBitMask,
    PixelBltOnly,
    PixelFormatMax
} EFI_GRAPHICS_PIXEL_FORMAT;

typedef struct {
    UINT32 RedMask;
    UINT32 GreenMask;
    UINT32 BlueMask;
    UINT32 ReservedMask;
} EFI_PIXEL_BITMASK;

typedef struct {
    UINT32                     Version;
    UINT32                     HorizontalResolution;
    UINT32                     VerticalResolution;
    EFI_GRAPHICS_PIXEL_FORMAT  PixelFormat;
    EFI_PIXEL_BITMASK          PixelInformation;
    UINT32                     PixelsPerScanLine;
} EFI_GRAPHICS_OUTPUT_MODE_INFORMATION;

typedef struct {
    UINT32                               MaxMode;
    UINT32                               Mode;
    EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *Info;
    UINTN                                SizeOfInfo;
    uint64_t                             FrameBufferBase;
    UINTN                                FrameBufferSize;
} EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE;

typedef struct _EFI_GRAPHICS_OUTPUT_PROTOCOL EFI_GRAPHICS_OUTPUT_PROTOCOL;

typedef EFI_STATUS (/* EFIAPI */ *EFI_GRAPHICS_OUTPUT_PROTOCOL_QUERY_MODE) (
    EFI_GRAPHICS_OUTPUT_PROTOCOL *This,
    UINT32 ModeNumber,
    UINTN *SizeOfInfo,
    EFI_GRAPHICS_OUTPUT_MODE_INFORMATION **Info
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_GRAPHICS_OUTPUT_PROTOCOL_SET_MODE) (
    EFI_GRAPHICS_OUTPUT_PROTOCOL *This,
    UINT32 ModeNumber
);

struct _EFI_GRAPHICS_OUTPUT_PROTOCOL {
    EFI_GRAPHICS_OUTPUT_PROTOCOL_QUERY_MODE QueryMode;
    EFI_GRAPHICS_OUTPUT_PROTOCOL_SET_MODE   SetMode;
    void*                                   Blt;
    EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE       *Mode;
};

// Loaded Image Protocol
typedef struct {
    UINT32     Revision;
    EFI_HANDLE ParentHandle;
    struct _EFI_SYSTEM_TABLE *SystemTable;
    EFI_HANDLE DeviceHandle;
    void*      FilePath;
    void*      Reserved;
    UINT32     LoadOptionsSize;
    void*      LoadOptions;
    void*      ImageBase;
    UINT64     ImageSize;
    int        ImageCodeType;
    int        ImageDataType;
    void*      Unload;
} EFI_LOADED_IMAGE_PROTOCOL;

// File Protocol
struct _EFI_FILE_PROTOCOL;
typedef struct _EFI_FILE_PROTOCOL EFI_FILE_PROTOCOL;

typedef EFI_STATUS (/* EFIAPI */ *EFI_FILE_OPEN) (
    EFI_FILE_PROTOCOL *This,
    EFI_FILE_PROTOCOL **NewHandle,
    const CHAR16 *FileName,
    UINT64 OpenMode,
    UINT64 Attributes
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_FILE_CLOSE) (
    EFI_FILE_PROTOCOL *This
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_FILE_READ) (
    EFI_FILE_PROTOCOL *This,
    UINTN *BufferSize,
    void *Buffer
);

struct _EFI_FILE_PROTOCOL {
    UINT64            Revision;
    EFI_FILE_OPEN     Open;
    EFI_FILE_CLOSE    Close;
    void*             Delete;
    EFI_FILE_READ     Read;
    void*             Write;
    void*             GetPosition;
    void*             SetPosition;
    void*             GetInfo;
    void*             SetInfo;
    void*             Flush;
};

// Simple File System Protocol
struct _EFI_SIMPLE_FILE_SYSTEM_PROTOCOL;
typedef struct _EFI_SIMPLE_FILE_SYSTEM_PROTOCOL EFI_SIMPLE_FILE_SYSTEM_PROTOCOL;

typedef EFI_STATUS (/* EFIAPI */ *EFI_SIMPLE_FILE_SYSTEM_OPEN_VOLUME) (
    EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *This,
    EFI_FILE_PROTOCOL **Root
);

struct _EFI_SIMPLE_FILE_SYSTEM_PROTOCOL {
    UINT64                               Revision;
    EFI_SIMPLE_FILE_SYSTEM_OPEN_VOLUME   OpenVolume;
};

// Boot Services
typedef enum {
    AllocateAnyPages,
    AllocateMaxAddress,
    AllocateAddress,
    MaxAllocateType
} EFI_ALLOCATE_TYPE;

typedef enum {
    EfiReservedMemoryType,
    EfiLoaderCode,
    EfiLoaderData,
    EfiBootServicesCode,
    EfiBootServicesData,
    EfiRuntimeServicesCode,
    EfiRuntimeServicesData,
    EfiConventionalMemory,
    EfiUnusableMemory,
    EfiACPIReclaimMemory,
    EfiACPIMemoryNVS,
    EfiMemoryMappedIO,
    EfiMemoryMappedIOPortSpace,
    EfiPalCode,
    EfiPersistentMemory,
    EfiMaxMemoryType
} EFI_MEMORY_TYPE;

typedef struct {
    UINT32          Type;
    uint64_t        PhysicalStart;
    uint64_t        VirtualStart;
    UINT64          NumberOfPages;
    UINT64          Attribute;
} EFI_MEMORY_DESCRIPTOR;

typedef struct {
    UINT64 Signature;
    UINT32 Revision;
    UINT32 HeaderSize;
    UINT32 CRC32;
    UINT32 Reserved;
} EFI_TABLE_HEADER;

typedef EFI_STATUS (/* EFIAPI */ *EFI_ALLOCATE_PAGES) (
    EFI_ALLOCATE_TYPE Type,
    EFI_MEMORY_TYPE MemoryType,
    UINTN Pages,
    uint64_t *Memory
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_FREE_PAGES) (
    uint64_t Memory,
    UINTN Pages
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_GET_MEMORY_MAP) (
    UINTN *MemoryMapSize,
    EFI_MEMORY_DESCRIPTOR *MemoryMap,
    UINTN *MapKey,
    UINTN *DescriptorSize,
    UINT32 *DescriptorVersion
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_ALLOCATE_POOL) (
    EFI_MEMORY_TYPE PoolType,
    UINTN Size,
    void **Buffer
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_FREE_POOL) (
    void *Buffer
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_LOCATE_PROTOCOL) (
    EFI_GUID *Protocol,
    void *Registration,
    void **Interface
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_HANDLE_PROTOCOL) (
    EFI_HANDLE Handle,
    EFI_GUID *Protocol,
    void **Interface
);

typedef EFI_STATUS (/* EFIAPI */ *EFI_EXIT_BOOT_SERVICES) (
    EFI_HANDLE ImageHandle,
    UINTN MapKey
);

typedef struct {
    EFI_TABLE_HEADER            Hdr;

    // Task Priority Services
    void*                       RaiseTPL;
    void*                       RestoreTPL;

    // Memory Services
    EFI_ALLOCATE_PAGES          AllocatePages;
    EFI_FREE_PAGES              FreePages;
    EFI_GET_MEMORY_MAP          GetMemoryMap;
    EFI_ALLOCATE_POOL           AllocatePool;
    EFI_FREE_POOL               FreePool;

    // Event & Timer Services
    void*                       CreateEvent;
    void*                       SetTimer;
    void*                       WaitForEvent;
    void*                       SignalEvent;
    void*                       CloseEvent;
    void*                       CheckEvent;

    // Protocol Handler Services
    void*                       InstallProtocolInterface;
    void*                       ReinstallProtocolInterface;
    void*                       UninstallProtocolInterface;
    EFI_HANDLE_PROTOCOL         HandleProtocol;
    void*                       Reserved;
    void*                       RegisterProtocolNotify;
    void*                       LocateHandle;
    void*                       LocateDevicePath;
    void*                       InstallConfigurationTable;

    // Image Services
    void*                       LoadImage;
    void*                       StartImage;
    void*                       Exit;
    void*                       UnloadImage;
    EFI_EXIT_BOOT_SERVICES      ExitBootServices;

    // Miscellaneous Services
    void*                       GetNextMonotonicCount;
    void*                       Stall;
    void*                       SetWatchdogTimer;

    // DriverSupport Services
    void*                       ConnectController;
    void*                       DisconnectController;

    // Open and Close Protocol Services
    void*                       OpenProtocol;
    void*                       CloseProtocol;
    void*                       OpenProtocolInformation;

    // Library Services
    void*                       ProtocolsPerHandle;
    void*                       LocateHandleBuffer;
    EFI_LOCATE_PROTOCOL         LocateProtocol;
    void*                       InstallMultipleProtocolInterfaces;
    void*                       UninstallMultipleProtocolInterfaces;

    // 32-bit CRC Services
    void*                       CalculateCrc32;

    // Miscellaneous Services
    void*                       CopyMem;
    void*                       SetMem;
    void*                       CreateEventEx;
} EFI_BOOT_SERVICES;

// System Table
typedef struct _EFI_SYSTEM_TABLE {
    EFI_TABLE_HEADER                Hdr;
    CHAR16                          *FirmwareVendor;
    UINT32                          FirmwareRevision;
    EFI_HANDLE                      ConsoleInHandle;
    EFI_SIMPLE_TEXT_INPUT_PROTOCOL  *ConIn;
    EFI_HANDLE                      ConsoleOutHandle;
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *ConOut;
    EFI_HANDLE                      StandardErrorHandle;
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *StdErr;
    void*                           RuntimeServices;
    EFI_BOOT_SERVICES               *BootServices;
    UINTN                           NumberOfTableEntries;
    void*                           ConfigurationTable;
} EFI_SYSTEM_TABLE;

// Structure passed from Bootloader to Kernel
typedef struct {
    uint64_t FrameBufferBase;
    uint64_t FrameBufferSize;
    uint32_t HorizontalResolution;
    uint32_t VerticalResolution;
    uint32_t PixelsPerScanLine;
    uint32_t PixelFormat;

    // Memory Map information
    uint64_t MemoryMapAddr;
    uint64_t MemoryMapSize;
    uint64_t DescriptorSize;

    // System Tables (for future runtime capabilities)
    uint64_t SystemTable;
} BootInfo;

#endif

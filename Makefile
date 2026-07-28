# SunnyOS Milestone 1 Makefile

CC = clang
LD = lld-link
NASM = nasm

# Target platforms
EFI_TARGET = x86_64-unknown-windows
KERNEL_CC = gcc
KERNEL_LD = ld

# Directories
BOOT_DIR = bootloader
KERN_DIR = kernel
BUILD_DIR = build

# Source files
BOOT_SRCS = $(BOOT_DIR)/efi_main.c
KERN_ASM = $(KERN_DIR)/entry.asm
KERN_SRCS = $(KERN_DIR)/kernel.c $(KERN_DIR)/font.c

# Output binaries
BOOT_EFI = $(BUILD_DIR)/BOOTX64.EFI
KERN_BIN = $(BUILD_DIR)/kernel.bin
DISK_IMG = $(BUILD_DIR)/sunnyos.img

# Compilation flags
EFI_CFLAGS = -target $(EFI_TARGET) -ffreestanding -fshort-wchar -mno-red-zone -O2 -Wall -Wextra -I.
EFI_LDFLAGS = -target $(EFI_TARGET) -nostdlib -Wl,-entry:efi_main -Wl,-subsystem:efi_application -fuse-ld=lld

KERN_CFLAGS = -m64 -ffreestanding -fno-stack-protector -fno-pic -O2 -Wall -Wextra -I. -mno-red-zone
KERN_LDFLAGS = -melf_x86_64 -T $(KERN_DIR)/linker.ld --oformat=binary

.PHONY: all clean image run run-headless

all: $(DISK_IMG)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Compile UEFI Bootloader
$(BOOT_EFI): $(BOOT_SRCS) | $(BUILD_DIR)
	$(CC) $(EFI_CFLAGS) $(EFI_LDFLAGS) -o $@ $<

# Compile Kernel assembly entry
$(BUILD_DIR)/entry.o: $(KERN_ASM) | $(BUILD_DIR)
	$(NASM) -f elf64 -o $@ $<

# Compile Kernel C sources
$(BUILD_DIR)/kernel.o: $(KERN_DIR)/kernel.c | $(BUILD_DIR)
	$(KERNEL_CC) $(KERN_CFLAGS) -c -o $@ $<

$(BUILD_DIR)/font.o: $(KERN_DIR)/font.c | $(BUILD_DIR)
	$(KERNEL_CC) $(KERN_CFLAGS) -c -o $@ $<

# Link Kernel flat binary
$(KERN_BIN): $(BUILD_DIR)/entry.o $(BUILD_DIR)/kernel.o $(BUILD_DIR)/font.o
	$(KERNEL_LD) $(KERN_LDFLAGS) -o $@ $^

# Create formatted FAT disk image
$(DISK_IMG): $(BOOT_EFI) $(KERN_BIN)
	@echo "Creating FAT32 disk image..."
	rm -f $@
	dd if=/dev/zero of=$@ bs=1M count=64
	mformat -i $@ -F -h 64 -t 32 -n 32 ::
	mmd -i $@ ::/EFI
	mmd -i $@ ::/EFI/BOOT
	mcopy -i $@ $(BOOT_EFI) ::/EFI/BOOT/BOOTX64.EFI
	mcopy -i $@ $(KERN_BIN) ::/kernel.bin
	@echo "Disk image successfully packaged with Bootloader and Kernel."

clean:
	rm -rf $(BUILD_DIR)

run: $(DISK_IMG)
	qemu-system-x86_64 -bios /usr/share/ovmf/OVMF.fd -drive file=$(DISK_IMG),format=raw -serial stdio

run-headless: $(DISK_IMG)
	@echo "Running QEMU headlessly..."
	timeout --foreground 5s qemu-system-x86_64 -bios /usr/share/ovmf/OVMF.fd -drive file=$(DISK_IMG),format=raw -nographic -serial stdio || true

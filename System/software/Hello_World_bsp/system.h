/*
 * system.h - SOPC Builder system and BSP software package information
 *
 * Machine generated for CPU 'nios2_cpu' in SOPC Builder design 'basics'
 * SOPC Builder design path: ../../basics.sopcinfo
 *
 * Generated: Tue May 12 00:18:22 EEST 2026
 */

/*
 * DO NOT MODIFY THIS FILE
 *
 * Changing this file will have subtle consequences
 * which will almost certainly lead to a nonfunctioning
 * system. If you do modify this file, be aware that your
 * changes will be overwritten and lost when this file
 * is generated again.
 *
 * DO NOT MODIFY THIS FILE
 */

/*
 * License Agreement
 *
 * Copyright (c) 2008
 * Altera Corporation, San Jose, California, USA.
 * All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 * This agreement shall be governed in all respects by the laws of the State
 * of California and by the laws of the United States of America.
 */

#ifndef __SYSTEM_H_
#define __SYSTEM_H_

/* Include definitions from linker script generator */
#include "linker.h"


/*
 * CPU configuration
 *
 */

#define ALT_CPU_ARCHITECTURE "altera_nios2_gen2"
#define ALT_CPU_BIG_ENDIAN 0
#define ALT_CPU_BREAK_ADDR 0x00010820
#define ALT_CPU_CPU_ARCH_NIOS2_R1
#define ALT_CPU_CPU_FREQ 50000000u
#define ALT_CPU_CPU_ID_SIZE 1
#define ALT_CPU_CPU_ID_VALUE 0x00000000
#define ALT_CPU_CPU_IMPLEMENTATION "tiny"
#define ALT_CPU_DATA_ADDR_WIDTH 0x11
#define ALT_CPU_DCACHE_LINE_SIZE 0
#define ALT_CPU_DCACHE_LINE_SIZE_LOG2 0
#define ALT_CPU_DCACHE_SIZE 0
#define ALT_CPU_EXCEPTION_ADDR 0x00000020
#define ALT_CPU_FLASH_ACCELERATOR_LINES 0
#define ALT_CPU_FLASH_ACCELERATOR_LINE_SIZE 0
#define ALT_CPU_FLUSHDA_SUPPORTED
#define ALT_CPU_FREQ 50000000
#define ALT_CPU_HARDWARE_DIVIDE_PRESENT 0
#define ALT_CPU_HARDWARE_MULTIPLY_PRESENT 0
#define ALT_CPU_HARDWARE_MULX_PRESENT 0
#define ALT_CPU_HAS_DEBUG_CORE 1
#define ALT_CPU_HAS_DEBUG_STUB
#define ALT_CPU_HAS_ILLEGAL_INSTRUCTION_EXCEPTION
#define ALT_CPU_HAS_JMPI_INSTRUCTION
#define ALT_CPU_ICACHE_LINE_SIZE 0
#define ALT_CPU_ICACHE_LINE_SIZE_LOG2 0
#define ALT_CPU_ICACHE_SIZE 0
#define ALT_CPU_INST_ADDR_WIDTH 0x11
#define ALT_CPU_NAME "nios2_cpu"
#define ALT_CPU_OCI_VERSION 1
#define ALT_CPU_RESET_ADDR 0x00000000


/*
 * CPU configuration (with legacy prefix - don't use these anymore)
 *
 */

#define NIOS2_BIG_ENDIAN 0
#define NIOS2_BREAK_ADDR 0x00010820
#define NIOS2_CPU_ARCH_NIOS2_R1
#define NIOS2_CPU_FREQ 50000000u
#define NIOS2_CPU_ID_SIZE 1
#define NIOS2_CPU_ID_VALUE 0x00000000
#define NIOS2_CPU_IMPLEMENTATION "tiny"
#define NIOS2_DATA_ADDR_WIDTH 0x11
#define NIOS2_DCACHE_LINE_SIZE 0
#define NIOS2_DCACHE_LINE_SIZE_LOG2 0
#define NIOS2_DCACHE_SIZE 0
#define NIOS2_EXCEPTION_ADDR 0x00000020
#define NIOS2_FLASH_ACCELERATOR_LINES 0
#define NIOS2_FLASH_ACCELERATOR_LINE_SIZE 0
#define NIOS2_FLUSHDA_SUPPORTED
#define NIOS2_HARDWARE_DIVIDE_PRESENT 0
#define NIOS2_HARDWARE_MULTIPLY_PRESENT 0
#define NIOS2_HARDWARE_MULX_PRESENT 0
#define NIOS2_HAS_DEBUG_CORE 1
#define NIOS2_HAS_DEBUG_STUB
#define NIOS2_HAS_ILLEGAL_INSTRUCTION_EXCEPTION
#define NIOS2_HAS_JMPI_INSTRUCTION
#define NIOS2_ICACHE_LINE_SIZE 0
#define NIOS2_ICACHE_LINE_SIZE_LOG2 0
#define NIOS2_ICACHE_SIZE 0
#define NIOS2_INST_ADDR_WIDTH 0x11
#define NIOS2_OCI_VERSION 1
#define NIOS2_RESET_ADDR 0x00000000


/*
 * Define for each module class mastered by the CPU
 *
 */

#define __ALTERA_AVALON_JTAG_UART
#define __ALTERA_AVALON_ONCHIP_MEMORY2
#define __ALTERA_AVALON_PIO
#define __ALTERA_AVALON_SYSID_QSYS
#define __ALTERA_NIOS2_GEN2


/*
 * System configuration
 *
 */

#define ALT_DEVICE_FAMILY "Cyclone V"
#define ALT_ENHANCED_INTERRUPT_API_PRESENT
#define ALT_IRQ_BASE NULL
#define ALT_LOG_PORT "/dev/null"
#define ALT_LOG_PORT_BASE 0x0
#define ALT_LOG_PORT_DEV null
#define ALT_LOG_PORT_TYPE ""
#define ALT_NUM_EXTERNAL_INTERRUPT_CONTROLLERS 0
#define ALT_NUM_INTERNAL_INTERRUPT_CONTROLLERS 1
#define ALT_NUM_INTERRUPT_CONTROLLERS 1
#define ALT_STDERR "/dev/jtag_uart"
#define ALT_STDERR_BASE 0x10000
#define ALT_STDERR_DEV jtag_uart
#define ALT_STDERR_IS_JTAG_UART
#define ALT_STDERR_PRESENT
#define ALT_STDERR_TYPE "altera_avalon_jtag_uart"
#define ALT_STDIN "/dev/jtag_uart"
#define ALT_STDIN_BASE 0x10000
#define ALT_STDIN_DEV jtag_uart
#define ALT_STDIN_IS_JTAG_UART
#define ALT_STDIN_PRESENT
#define ALT_STDIN_TYPE "altera_avalon_jtag_uart"
#define ALT_STDOUT "/dev/jtag_uart"
#define ALT_STDOUT_BASE 0x10000
#define ALT_STDOUT_DEV jtag_uart
#define ALT_STDOUT_IS_JTAG_UART
#define ALT_STDOUT_PRESENT
#define ALT_STDOUT_TYPE "altera_avalon_jtag_uart"
#define ALT_SYSTEM_NAME "basics"


/*
 * b1 configuration
 *
 */

#define ALT_MODULE_CLASS_b1 altera_avalon_onchip_memory2
#define B1_ALLOW_IN_SYSTEM_MEMORY_CONTENT_EDITOR 0
#define B1_ALLOW_MRAM_SIM_CONTENTS_ONLY_FILE 0
#define B1_BASE 0x10080
#define B1_CONTENTS_INFO ""
#define B1_DUAL_PORT 0
#define B1_GUI_RAM_BLOCK_TYPE "AUTO"
#define B1_INIT_CONTENTS_FILE "b1"
#define B1_INIT_MEM_CONTENT 1
#define B1_INSTANCE_ID "NONE"
#define B1_IRQ -1
#define B1_IRQ_INTERRUPT_CONTROLLER_ID -1
#define B1_NAME "/dev/b1"
#define B1_NON_DEFAULT_INIT_FILE_ENABLED 1
#define B1_RAM_BLOCK_TYPE "AUTO"
#define B1_READ_DURING_WRITE_MODE "DONT_CARE"
#define B1_SINGLE_CLOCK_OP 0
#define B1_SIZE_MULTIPLE 1
#define B1_SIZE_VALUE 32
#define B1_SPAN 32
#define B1_TYPE "altera_avalon_onchip_memory2"
#define B1_WRITABLE 0


/*
 * b2 configuration
 *
 */

#define ALT_MODULE_CLASS_b2 altera_avalon_onchip_memory2
#define B2_ALLOW_IN_SYSTEM_MEMORY_CONTENT_EDITOR 0
#define B2_ALLOW_MRAM_SIM_CONTENTS_ONLY_FILE 0
#define B2_BASE 0x10060
#define B2_CONTENTS_INFO ""
#define B2_DUAL_PORT 0
#define B2_GUI_RAM_BLOCK_TYPE "AUTO"
#define B2_INIT_CONTENTS_FILE "b2"
#define B2_INIT_MEM_CONTENT 1
#define B2_INSTANCE_ID "NONE"
#define B2_IRQ -1
#define B2_IRQ_INTERRUPT_CONTROLLER_ID -1
#define B2_NAME "/dev/b2"
#define B2_NON_DEFAULT_INIT_FILE_ENABLED 1
#define B2_RAM_BLOCK_TYPE "AUTO"
#define B2_READ_DURING_WRITE_MODE "DONT_CARE"
#define B2_SINGLE_CLOCK_OP 0
#define B2_SIZE_MULTIPLE 1
#define B2_SIZE_VALUE 32
#define B2_SPAN 32
#define B2_TYPE "altera_avalon_onchip_memory2"
#define B2_WRITABLE 0


/*
 * b3 configuration
 *
 */

#define ALT_MODULE_CLASS_b3 altera_avalon_onchip_memory2
#define B3_ALLOW_IN_SYSTEM_MEMORY_CONTENT_EDITOR 0
#define B3_ALLOW_MRAM_SIM_CONTENTS_ONLY_FILE 0
#define B3_BASE 0x10040
#define B3_CONTENTS_INFO ""
#define B3_DUAL_PORT 0
#define B3_GUI_RAM_BLOCK_TYPE "AUTO"
#define B3_INIT_CONTENTS_FILE "b3"
#define B3_INIT_MEM_CONTENT 1
#define B3_INSTANCE_ID "NONE"
#define B3_IRQ -1
#define B3_IRQ_INTERRUPT_CONTROLLER_ID -1
#define B3_NAME "/dev/b3"
#define B3_NON_DEFAULT_INIT_FILE_ENABLED 1
#define B3_RAM_BLOCK_TYPE "AUTO"
#define B3_READ_DURING_WRITE_MODE "DONT_CARE"
#define B3_SINGLE_CLOCK_OP 0
#define B3_SIZE_MULTIPLE 1
#define B3_SIZE_VALUE 32
#define B3_SPAN 32
#define B3_TYPE "altera_avalon_onchip_memory2"
#define B3_WRITABLE 0


/*
 * hal configuration
 *
 */

#define ALT_INCLUDE_INSTRUCTION_RELATED_EXCEPTION_API
#define ALT_MAX_FD 4
#define ALT_SYS_CLK none
#define ALT_TIMESTAMP_CLK none


/*
 * input_layer configuration
 *
 */

#define ALT_MODULE_CLASS_input_layer altera_avalon_onchip_memory2
#define INPUT_LAYER_ALLOW_IN_SYSTEM_MEMORY_CONTENT_EDITOR 0
#define INPUT_LAYER_ALLOW_MRAM_SIM_CONTENTS_ONLY_FILE 0
#define INPUT_LAYER_BASE 0x11000
#define INPUT_LAYER_CONTENTS_INFO ""
#define INPUT_LAYER_DUAL_PORT 0
#define INPUT_LAYER_GUI_RAM_BLOCK_TYPE "M10K"
#define INPUT_LAYER_INIT_CONTENTS_FILE "test_image"
#define INPUT_LAYER_INIT_MEM_CONTENT 1
#define INPUT_LAYER_INSTANCE_ID "NONE"
#define INPUT_LAYER_IRQ -1
#define INPUT_LAYER_IRQ_INTERRUPT_CONTROLLER_ID -1
#define INPUT_LAYER_NAME "/dev/input_layer"
#define INPUT_LAYER_NON_DEFAULT_INIT_FILE_ENABLED 1
#define INPUT_LAYER_RAM_BLOCK_TYPE "M10K"
#define INPUT_LAYER_READ_DURING_WRITE_MODE "DONT_CARE"
#define INPUT_LAYER_SINGLE_CLOCK_OP 0
#define INPUT_LAYER_SIZE_MULTIPLE 1
#define INPUT_LAYER_SIZE_VALUE 1568
#define INPUT_LAYER_SPAN 1568
#define INPUT_LAYER_TYPE "altera_avalon_onchip_memory2"
#define INPUT_LAYER_WRITABLE 0


/*
 * jtag_uart configuration
 *
 */

#define ALT_MODULE_CLASS_jtag_uart altera_avalon_jtag_uart
#define JTAG_UART_BASE 0x10000
#define JTAG_UART_IRQ 8
#define JTAG_UART_IRQ_INTERRUPT_CONTROLLER_ID 0
#define JTAG_UART_NAME "/dev/jtag_uart"
#define JTAG_UART_READ_DEPTH 64
#define JTAG_UART_READ_THRESHOLD 8
#define JTAG_UART_SPAN 8
#define JTAG_UART_TYPE "altera_avalon_jtag_uart"
#define JTAG_UART_WRITE_DEPTH 64
#define JTAG_UART_WRITE_THRESHOLD 8


/*
 * leds configuration
 *
 */

#define ALT_MODULE_CLASS_leds altera_avalon_pio
#define LEDS_BASE 0x10010
#define LEDS_BIT_CLEARING_EDGE_REGISTER 0
#define LEDS_BIT_MODIFYING_OUTPUT_REGISTER 0
#define LEDS_CAPTURE 0
#define LEDS_DATA_WIDTH 10
#define LEDS_DO_TEST_BENCH_WIRING 0
#define LEDS_DRIVEN_SIM_VALUE 0
#define LEDS_EDGE_TYPE "NONE"
#define LEDS_FREQ 50000000
#define LEDS_HAS_IN 0
#define LEDS_HAS_OUT 1
#define LEDS_HAS_TRI 0
#define LEDS_IRQ -1
#define LEDS_IRQ_INTERRUPT_CONTROLLER_ID -1
#define LEDS_IRQ_TYPE "NONE"
#define LEDS_NAME "/dev/leds"
#define LEDS_RESET_VALUE 0
#define LEDS_SPAN 16
#define LEDS_TYPE "altera_avalon_pio"


/*
 * onchip_memory configuration
 *
 */

#define ALT_MODULE_CLASS_onchip_memory altera_avalon_onchip_memory2
#define ONCHIP_MEMORY_ALLOW_IN_SYSTEM_MEMORY_CONTENT_EDITOR 0
#define ONCHIP_MEMORY_ALLOW_MRAM_SIM_CONTENTS_ONLY_FILE 0
#define ONCHIP_MEMORY_BASE 0x0
#define ONCHIP_MEMORY_CONTENTS_INFO ""
#define ONCHIP_MEMORY_DUAL_PORT 0
#define ONCHIP_MEMORY_GUI_RAM_BLOCK_TYPE "AUTO"
#define ONCHIP_MEMORY_INIT_CONTENTS_FILE "basics_onchip_memory"
#define ONCHIP_MEMORY_INIT_MEM_CONTENT 0
#define ONCHIP_MEMORY_INSTANCE_ID "NONE"
#define ONCHIP_MEMORY_IRQ -1
#define ONCHIP_MEMORY_IRQ_INTERRUPT_CONTROLLER_ID -1
#define ONCHIP_MEMORY_NAME "/dev/onchip_memory"
#define ONCHIP_MEMORY_NON_DEFAULT_INIT_FILE_ENABLED 0
#define ONCHIP_MEMORY_RAM_BLOCK_TYPE "AUTO"
#define ONCHIP_MEMORY_READ_DURING_WRITE_MODE "DONT_CARE"
#define ONCHIP_MEMORY_SINGLE_CLOCK_OP 0
#define ONCHIP_MEMORY_SIZE_MULTIPLE 1
#define ONCHIP_MEMORY_SIZE_VALUE 65536
#define ONCHIP_MEMORY_SPAN 65536
#define ONCHIP_MEMORY_TYPE "altera_avalon_onchip_memory2"
#define ONCHIP_MEMORY_WRITABLE 1


/*
 * sev_seg configuration
 *
 */

#define ALT_MODULE_CLASS_sev_seg altera_avalon_pio
#define SEV_SEG_BASE 0x10030
#define SEV_SEG_BIT_CLEARING_EDGE_REGISTER 0
#define SEV_SEG_BIT_MODIFYING_OUTPUT_REGISTER 0
#define SEV_SEG_CAPTURE 0
#define SEV_SEG_DATA_WIDTH 7
#define SEV_SEG_DO_TEST_BENCH_WIRING 0
#define SEV_SEG_DRIVEN_SIM_VALUE 0
#define SEV_SEG_EDGE_TYPE "NONE"
#define SEV_SEG_FREQ 50000000
#define SEV_SEG_HAS_IN 0
#define SEV_SEG_HAS_OUT 1
#define SEV_SEG_HAS_TRI 0
#define SEV_SEG_IRQ -1
#define SEV_SEG_IRQ_INTERRUPT_CONTROLLER_ID -1
#define SEV_SEG_IRQ_TYPE "NONE"
#define SEV_SEG_NAME "/dev/sev_seg"
#define SEV_SEG_RESET_VALUE 0
#define SEV_SEG_SPAN 16
#define SEV_SEG_TYPE "altera_avalon_pio"


/*
 * switches configuration
 *
 */

#define ALT_MODULE_CLASS_switches altera_avalon_pio
#define SWITCHES_BASE 0x10020
#define SWITCHES_BIT_CLEARING_EDGE_REGISTER 0
#define SWITCHES_BIT_MODIFYING_OUTPUT_REGISTER 0
#define SWITCHES_CAPTURE 0
#define SWITCHES_DATA_WIDTH 10
#define SWITCHES_DO_TEST_BENCH_WIRING 0
#define SWITCHES_DRIVEN_SIM_VALUE 0
#define SWITCHES_EDGE_TYPE "NONE"
#define SWITCHES_FREQ 50000000
#define SWITCHES_HAS_IN 1
#define SWITCHES_HAS_OUT 0
#define SWITCHES_HAS_TRI 0
#define SWITCHES_IRQ -1
#define SWITCHES_IRQ_INTERRUPT_CONTROLLER_ID -1
#define SWITCHES_IRQ_TYPE "NONE"
#define SWITCHES_NAME "/dev/switches"
#define SWITCHES_RESET_VALUE 0
#define SWITCHES_SPAN 16
#define SWITCHES_TYPE "altera_avalon_pio"


/*
 * sysid_qsys_0 configuration
 *
 */

#define ALT_MODULE_CLASS_sysid_qsys_0 altera_avalon_sysid_qsys
#define SYSID_QSYS_0_BASE 0x10008
#define SYSID_QSYS_0_ID 4112
#define SYSID_QSYS_0_IRQ -1
#define SYSID_QSYS_0_IRQ_INTERRUPT_CONTROLLER_ID -1
#define SYSID_QSYS_0_NAME "/dev/sysid_qsys_0"
#define SYSID_QSYS_0_SPAN 8
#define SYSID_QSYS_0_TIMESTAMP 1778516082
#define SYSID_QSYS_0_TYPE "altera_avalon_sysid_qsys"


/*
 * w1 configuration
 *
 */

#define ALT_MODULE_CLASS_w1 altera_avalon_onchip_memory2
#define W1_ALLOW_IN_SYSTEM_MEMORY_CONTENT_EDITOR 0
#define W1_ALLOW_MRAM_SIM_CONTENTS_ONLY_FILE 0
#define W1_BASE 0x18000
#define W1_CONTENTS_INFO ""
#define W1_DUAL_PORT 0
#define W1_GUI_RAM_BLOCK_TYPE "AUTO"
#define W1_INIT_CONTENTS_FILE "w1"
#define W1_INIT_MEM_CONTENT 1
#define W1_INSTANCE_ID "NONE"
#define W1_IRQ -1
#define W1_IRQ_INTERRUPT_CONTROLLER_ID -1
#define W1_NAME "/dev/w1"
#define W1_NON_DEFAULT_INIT_FILE_ENABLED 1
#define W1_RAM_BLOCK_TYPE "AUTO"
#define W1_READ_DURING_WRITE_MODE "DONT_CARE"
#define W1_SINGLE_CLOCK_OP 0
#define W1_SIZE_MULTIPLE 1
#define W1_SIZE_VALUE 25088
#define W1_SPAN 25088
#define W1_TYPE "altera_avalon_onchip_memory2"
#define W1_WRITABLE 0


/*
 * w2 configuration
 *
 */

#define ALT_MODULE_CLASS_w2 altera_avalon_onchip_memory2
#define W2_ALLOW_IN_SYSTEM_MEMORY_CONTENT_EDITOR 0
#define W2_ALLOW_MRAM_SIM_CONTENTS_ONLY_FILE 0
#define W2_BASE 0x10200
#define W2_CONTENTS_INFO ""
#define W2_DUAL_PORT 0
#define W2_GUI_RAM_BLOCK_TYPE "AUTO"
#define W2_INIT_CONTENTS_FILE "w2"
#define W2_INIT_MEM_CONTENT 1
#define W2_INSTANCE_ID "NONE"
#define W2_IRQ -1
#define W2_IRQ_INTERRUPT_CONTROLLER_ID -1
#define W2_NAME "/dev/w2"
#define W2_NON_DEFAULT_INIT_FILE_ENABLED 1
#define W2_RAM_BLOCK_TYPE "AUTO"
#define W2_READ_DURING_WRITE_MODE "DONT_CARE"
#define W2_SINGLE_CLOCK_OP 0
#define W2_SIZE_MULTIPLE 1
#define W2_SIZE_VALUE 512
#define W2_SPAN 512
#define W2_TYPE "altera_avalon_onchip_memory2"
#define W2_WRITABLE 0


/*
 * w3 configuration
 *
 */

#define ALT_MODULE_CLASS_w3 altera_avalon_onchip_memory2
#define W3_ALLOW_IN_SYSTEM_MEMORY_CONTENT_EDITOR 0
#define W3_ALLOW_MRAM_SIM_CONTENTS_ONLY_FILE 0
#define W3_BASE 0x10400
#define W3_CONTENTS_INFO ""
#define W3_DUAL_PORT 0
#define W3_GUI_RAM_BLOCK_TYPE "AUTO"
#define W3_INIT_CONTENTS_FILE "w3"
#define W3_INIT_MEM_CONTENT 1
#define W3_INSTANCE_ID "NONE"
#define W3_IRQ -1
#define W3_IRQ_INTERRUPT_CONTROLLER_ID -1
#define W3_NAME "/dev/w3"
#define W3_NON_DEFAULT_INIT_FILE_ENABLED 1
#define W3_RAM_BLOCK_TYPE "AUTO"
#define W3_READ_DURING_WRITE_MODE "DONT_CARE"
#define W3_SINGLE_CLOCK_OP 0
#define W3_SIZE_MULTIPLE 1
#define W3_SIZE_VALUE 320
#define W3_SPAN 320
#define W3_TYPE "altera_avalon_onchip_memory2"
#define W3_WRITABLE 0

#endif /* __SYSTEM_H_ */

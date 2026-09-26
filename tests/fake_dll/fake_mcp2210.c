/*
 * Stand-in for Microchip's mcp2210_dll_um DLL, used by the tests on machines
 * without the hardware (and on Linux). It is compiled against the real
 * mcp2210_dll_um.h, so every prototype here must match the vendor header.
 *
 * Handles are 64-bit values with the high bits set: a wrapper that lets
 * ctypes truncate them to 32 bits gets E_ERR_INVALID_HANDLE_VALUE back.
 *
 * SPI transfers are logged, and an MCP23S17 register file (BANK=1 layout) is
 * emulated so read-modify-write sequences can be checked.
 */
#include <stdint.h>
#include <string.h>
#include <wchar.h>

#include "mcp2210_dll_um.h"

#define FAKE_HANDLE ((void *)(uintptr_t)0x7ffe12345678ULL)
#define FAKE_SERIAL L"0001234567"
#define FAKE_PATH L"\\\\?\\hid#vid_04d8&pid_00de#fake"
#define LOG_SIZE 512
#define MAX_XFER 64

/* Knobs and counters the tests read or set through ctypes. */
int fake_device_count = 1;
int fake_reset_result = 0;
int fake_open_handles = 0;
int fake_close_calls = 0;

static int last_error = 0;
static wchar_t manufacturer[MCP2210_DESCRIPTOR_STR_MAX_LEN + 1] = L"Microchip Technology Inc.";
static wchar_t product[MCP2210_DESCRIPTOR_STR_MAX_LEN + 1] = L"MCP2210 USB to SPI Master";
static unsigned int gpio_val = 0;
static unsigned int gpio_dir = 0x1FF;
static unsigned char pin_des[MCP2210_GPIO_NR];
static unsigned int dflt_out = 0, dflt_dir = 0x1FF;
static unsigned char rmt_wkup = 0, int_md = 0, bus_rel = 0;
static unsigned int spi_cfg[7] = {12000000, 0x1FF, 0, 0, 0, 0, 4};
static unsigned char spi_md = 0;
static unsigned char mcp23s17_regs[8][32];

static unsigned char log_tx[LOG_SIZE][MAX_XFER];
static unsigned int log_len[LOG_SIZE];
static unsigned int log_cs[LOG_SIZE];
static unsigned int log_count = 0;

static int check(void *handle)
{
    return handle == FAKE_HANDLE ? E_SUCCESS : E_ERR_INVALID_HANDLE_VALUE;
}

/* ---- test helpers (not part of the vendor API) ---- */
unsigned int fake_xfer_count(void) { return log_count; }

int fake_get_xfer(unsigned int i, unsigned char *out, unsigned int *len, unsigned int *csmask)
{
    if (i >= log_count || i >= LOG_SIZE) return -1;
    memcpy(out, log_tx[i], log_len[i]);
    *len = log_len[i];
    *csmask = log_cs[i];
    return 0;
}

void fake_reset_log(void) { log_count = 0; }

/* ---- vendor API ---- */
int Mcp2210_GetLibraryVersion(wchar_t *version)
{
    if (!version) return E_ERR_NULL;
    wcscpy(version, L"fake-1.0");
    return E_SUCCESS;
}

int Mcp2210_GetLastError(void) { return last_error; }

int Mcp2210_GetConnectedDevCount(unsigned short vid, unsigned short pid)
{
    return (vid == 0x04D8 && pid == 0x00DE) ? fake_device_count : 0;
}

static void *open_common(wchar_t *devPath, unsigned long *devPathsize)
{
    if (!devPath || !devPathsize) { last_error = E_ERR_NULL; return (void *)-1; }
    if (*devPathsize < wcslen(FAKE_PATH) + 1) { last_error = E_ERR_BUFFER_TOO_SMALL; return (void *)-1; }
    wcscpy(devPath, FAKE_PATH);
    *devPathsize = (unsigned long)wcslen(FAKE_PATH) + 1;
    fake_open_handles++;
    return FAKE_HANDLE;
}

void *Mcp2210_OpenByIndex(unsigned short vid, unsigned short pid, unsigned int index, wchar_t *devPath, unsigned long *devPathsize)
{
    if (vid != 0x04D8 || pid != 0x00DE || (int)index >= fake_device_count) {
        last_error = E_ERR_NO_SUCH_INDEX;
        return (void *)-1;
    }
    return open_common(devPath, devPathsize);
}

void *Mcp2210_OpenBySN(unsigned short vid, unsigned short pid, wchar_t *serialNo, wchar_t *devPath, unsigned long *devPathsize)
{
    if (vid != 0x04D8 || pid != 0x00DE || !serialNo || wcscmp(serialNo, FAKE_SERIAL) != 0) {
        last_error = E_ERR_NO_SUCH_SERIALNR;
        return (void *)-1;
    }
    return open_common(devPath, devPathsize);
}

int Mcp2210_Close(void *handle)
{
    fake_close_calls++;
    if (check(handle) || fake_open_handles == 0) return E_ERR_CLOSE_FAILED;
    fake_open_handles--;
    return E_SUCCESS;
}

int Mcp2210_Reset(void *handle) { return check(handle) ? check(handle) : fake_reset_result; }

int Mcp2210_GetUsbKeyParams(void *handle, unsigned short *pvid, unsigned short *ppid,
                            unsigned char *ppwrSrc, unsigned char *prmtWkup, unsigned short *pcurrentLd)
{
    if (check(handle)) return check(handle);
    *pvid = 0x04D8; *ppid = 0x00DE; *ppwrSrc = 0; *prmtWkup = 0; *pcurrentLd = 100;
    return E_SUCCESS;
}

int Mcp2210_SetUsbKeyParams(void *handle, unsigned short vid, unsigned short pid,
                            unsigned char pwrSrc, unsigned char rmtWkup, unsigned short currentLd)
{
    (void)vid; (void)pid; (void)pwrSrc; (void)rmtWkup; (void)currentLd;
    return check(handle);
}

static int get_str(void *handle, wchar_t *dst, const wchar_t *src)
{
    if (check(handle)) return check(handle);
    wcscpy(dst, src);
    return E_SUCCESS;
}

static int set_str(void *handle, wchar_t *dst, const wchar_t *src)
{
    if (check(handle)) return check(handle);
    if (wcslen(src) > MCP2210_DESCRIPTOR_STR_MAX_LEN) return E_ERR_STRING_TOO_LARGE;
    wcscpy(dst, src);
    return E_SUCCESS;
}

int Mcp2210_GetManufacturerString(void *handle, wchar_t *s) { return get_str(handle, s, manufacturer); }
int Mcp2210_SetManufacturerString(void *handle, wchar_t *s) { return set_str(handle, manufacturer, s); }
int Mcp2210_GetProductString(void *handle, wchar_t *s) { return get_str(handle, s, product); }
int Mcp2210_SetProductString(void *handle, wchar_t *s) { return set_str(handle, product, s); }
int Mcp2210_GetSerialNumber(void *handle, wchar_t *s) { return get_str(handle, s, FAKE_SERIAL); }

int Mcp2210_GetGpioPinDir(void *handle, unsigned int *pgpioDir)
{
    if (check(handle)) return check(handle);
    *pgpioDir = gpio_dir;
    return E_SUCCESS;
}

int Mcp2210_SetGpioPinDir(void *handle, unsigned int gpioSetDir)
{
    if (check(handle)) return check(handle);
    gpio_dir = gpioSetDir & 0x1FF;
    return E_SUCCESS;
}

int Mcp2210_GetGpioPinVal(void *handle, unsigned int *pgpioPinVal)
{
    if (check(handle)) return check(handle);
    *pgpioPinVal = gpio_val;
    return E_SUCCESS;
}

int Mcp2210_SetGpioPinVal(void *handle, unsigned int gpioSetVal, unsigned int *pgpioPinVal)
{
    if (check(handle)) return check(handle);
    gpio_val = gpioSetVal & 0x1FF;
    *pgpioPinVal = gpio_val;
    return E_SUCCESS;
}

int Mcp2210_GetGpioConfig(void *handle, unsigned char cfgSelector, unsigned char *pGpioPinDes, unsigned int *pdfltGpioOutput,
                          unsigned int *pdfltGpioDir, unsigned char *prmtWkupEn, unsigned char *pintPinMd, unsigned char *pspiBusRelEn)
{
    (void)cfgSelector;
    if (check(handle)) return check(handle);
    memcpy(pGpioPinDes, pin_des, MCP2210_GPIO_NR);
    *pdfltGpioOutput = dflt_out; *pdfltGpioDir = dflt_dir;
    *prmtWkupEn = rmt_wkup; *pintPinMd = int_md; *pspiBusRelEn = bus_rel;
    return E_SUCCESS;
}

int Mcp2210_SetGpioConfig(void *handle, unsigned char cfgSelector, unsigned char *pGpioPinDes, unsigned int dfltGpioOutput,
                          unsigned int dfltGpioDir, unsigned char rmtWkupEn, unsigned char intPinMd, unsigned char spiBusRelEn)
{
    if (check(handle)) return check(handle);
    if (cfgSelector > MCP2210_NVRAM_CONFIG || intPinMd > MCP2210_INT_MD_CNT_HIGH_PULSES
            || spiBusRelEn > MCP2210_SPI_BUS_RELEASE_DISABLED)
        return E_ERR_INVALID_PARAMETER;
    memcpy(pin_des, pGpioPinDes, MCP2210_GPIO_NR);
    dflt_out = dfltGpioOutput; dflt_dir = dfltGpioDir;
    rmt_wkup = rmtWkupEn; int_md = intPinMd; bus_rel = spiBusRelEn;
    gpio_val = dfltGpioOutput & 0x1FF; gpio_dir = dfltGpioDir & 0x1FF;
    return E_SUCCESS;
}

int Mcp2210_GetInterruptCount(void *handle, unsigned int *pintCnt, unsigned char reset)
{
    (void)reset;
    if (check(handle)) return check(handle);
    *pintCnt = 0;
    return E_SUCCESS;
}

int Mcp2210_GetSpiConfig(void *handle, unsigned char cfgSelector, unsigned int *pbaudRate, unsigned int *pidleCsVal,
                         unsigned int *pactiveCsVal, unsigned int *pCsToDataDly, unsigned int *pdataToCsDly,
                         unsigned int *pdataToDataDly, unsigned int *ptxferSize, unsigned char *pspiMd)
{
    (void)cfgSelector;
    if (check(handle)) return check(handle);
    *pbaudRate = spi_cfg[0]; *pidleCsVal = spi_cfg[1]; *pactiveCsVal = spi_cfg[2];
    *pCsToDataDly = spi_cfg[3]; *pdataToCsDly = spi_cfg[4]; *pdataToDataDly = spi_cfg[5];
    *ptxferSize = spi_cfg[6]; *pspiMd = spi_md;
    return E_SUCCESS;
}

int Mcp2210_SetSpiConfig(void *handle, unsigned char cfgSelector, unsigned int *pbaudRate, unsigned int *pidleCsVal,
                         unsigned int *pactiveCsVal, unsigned int *pCsToDataDly, unsigned int *pdataToCsDly,
                         unsigned int *pdataToDataDly, unsigned int *ptxferSize, unsigned char *pspiMd)
{
    (void)cfgSelector;
    if (check(handle)) return check(handle);
    spi_cfg[0] = *pbaudRate; spi_cfg[1] = *pidleCsVal; spi_cfg[2] = *pactiveCsVal;
    spi_cfg[3] = *pCsToDataDly; spi_cfg[4] = *pdataToCsDly; spi_cfg[5] = *pdataToDataDly;
    spi_cfg[6] = *ptxferSize; spi_md = *pspiMd;
    return E_SUCCESS;
}

/* Emulate MCP23S17s sharing one CS: opcode 0100 A2 A1 A0 R/W, register, data. */
static void mcp23s17(const unsigned char *tx, unsigned char *rx, unsigned int n)
{
    if (n != 3 || (tx[0] & 0xF0) != 0x40) return;
    unsigned int addr = (tx[0] >> 1) & 0x7, reg = tx[1] & 0x1F;
    if (tx[0] & 1) rx[2] = mcp23s17_regs[addr][reg];
    else mcp23s17_regs[addr][reg] = tx[2];
}

static int xfer(void *handle, unsigned char *pdataTx, unsigned char *pdataRx, unsigned int *ptxferSize, unsigned int csmask)
{
    if (check(handle)) return check(handle);
    if (!pdataTx || !pdataRx || !ptxferSize) return E_ERR_NULL;
    unsigned int n = *ptxferSize;
    if (n > MAX_XFER) return E_ERR_INVALID_PARAMETER;
    memset(pdataRx, 0, n);
    mcp23s17(pdataTx, pdataRx, n);
    if (log_count < LOG_SIZE) {
        memcpy(log_tx[log_count], pdataTx, n);
        log_len[log_count] = n;
        log_cs[log_count] = csmask;
    }
    log_count++;
    return E_SUCCESS;
}

int Mcp2210_xferSpiData(void *handle, unsigned char *pdataTx, unsigned char *pdataRx,
                        unsigned int *pbaudRate, unsigned int *ptxferSize, unsigned int csmask)
{
    if (!pbaudRate) return E_ERR_NULL;
    return xfer(handle, pdataTx, pdataRx, ptxferSize, csmask);
}

int Mcp2210_xferSpiDataEx(void *handle, unsigned char *pdataTx, unsigned char *pdataRx,
                          unsigned int *pbaudRate, unsigned int *ptxferSize, unsigned int csmask,
                          unsigned int *pidleCsVal, unsigned int *pactiveCsVal, unsigned int *pCsToDataDly,
                          unsigned int *pdataToCsDly, unsigned int *pdataToDataDly, unsigned char *pspiMd)
{
    if (!pbaudRate || !pidleCsVal || !pactiveCsVal || !pCsToDataDly || !pdataToCsDly || !pdataToDataDly || !pspiMd)
        return E_ERR_NULL;
    return xfer(handle, pdataTx, pdataRx, ptxferSize, csmask);
}

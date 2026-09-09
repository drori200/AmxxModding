/* Isolated canonical PAWN test host. Only loads bytecode produced by this lab.
 * This is a test instrument, not a hardened loader for untrusted AMX files.
 * The harness applies process time, address-space and output limits.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "amx.h"
#include "contracts.h"

static unsigned checks, failures;

static cell AMX_NATIVE_CALL check(AMX *amx, const cell *params)
{
    if (params[0] != 2 * sizeof(cell)) {
        amx_RaiseError(amx, AMX_ERR_PARAMS);
        return 0;
    }
    checks++;
    if (params[1] != params[2]) {
        failures++;
        printf("check %u: actual=%lld expected=%lld\n", checks,
               (long long)params[1], (long long)params[2]);
    }
    return params[1] == params[2];
}

static cell AMX_NATIVE_CALL identity(AMX *amx, const cell *params)
{
    if (params[0] != sizeof(cell)) {
        amx_RaiseError(amx, AMX_ERR_PARAMS);
        return 0;
    }
    return params[1]; /* Stops compiler constant folding without changing a value. */
}

static cell AMX_NATIVE_CALL native_error(AMX *amx, const cell *params)
{
    (void)params;
    amx_RaiseError(amx, AMX_ERR_NATIVE);
    return 0;
}

int main(int argc, char **argv)
{
    AMX amx;
    AMX_HEADER header;
    FILE *file;
    unsigned char *memory;
    cell result = 0;
    int error;
    unsigned sleeps = 0;
    const AMX_NATIVE_INFO natives[] = {
        {"check", check}, {"identity", identity}, {"native_error", native_error}, {NULL, NULL}
    };
    if (argc != 2 && !(argc == 3 && strcmp(argv[2], "--contracts") == 0)) {
        fprintf(stderr, "usage: labrun generated-program.amx [--contracts]\n");
        return 64;
    }
    file = fopen(argv[1], "rb");
    if (!file || fread(&header, 1, sizeof header, file) != sizeof header) return 65;
    amx_Align16(&header.magic);
    amx_Align32((uint32_t *)&header.size);
    amx_Align32((uint32_t *)&header.stp);
    if (header.magic != AMX_MAGIC || header.size < sizeof header ||
        header.stp < header.size || header.stp > 16 * 1024 * 1024) {
        fclose(file);
        return 66;
    }
    memory = calloc(1, header.stp);
    if (!memory) { fclose(file); return 67; }
    rewind(file);
    if (fread(memory, 1, header.size, file) != (size_t)header.size) {
        fclose(file); free(memory); return 68;
    }
    fclose(file);
    memset(&amx, 0, sizeof amx);
    error = amx_Init(&amx, memory);
    if (!error) error = amx_Register(&amx, natives, -1);
    if (!error) error = amx_Exec(&amx, &result, AMX_EXEC_MAIN);
    while (error == AMX_ERR_SLEEP && sleeps++ < 8)
        error = amx_Exec(&amx, &result, AMX_EXEC_CONT);
    printf("lab: bits=%d checks=%u failures=%u result=%lld error=%d sleeps=%u\n",
           PAWN_CELL_SIZE, checks, failures, (long long)result, error, sleeps);
    if (!error && argc == 3) host_contracts(&amx);
    amx_Cleanup(&amx);
    free(memory);
    return failures || host_failures ? 1 : (error ? 2 : 0);
}

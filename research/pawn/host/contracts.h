/* Test host API contracts against canonical amx.h and Implementer pp.16-56.
 * Invoked only for the dedicated generated host_contracts.p fixture.
 */
static unsigned host_checks, host_failures;
static unsigned debug_breaks;

static int AMXAPI trace_break(AMX *amx)
{
    (void)amx;
    debug_breaks++;
    return AMX_ERR_NONE;
}

static void host_check(int valid, const char *label)
{
    host_checks++;
    if (!valid) { host_failures++; printf("host failed: %s\n", label); }
}

static int find_public(AMX *amx, const char *name)
{
    int index = -1;
    int error = amx_FindPublic(amx, name, &index);
    host_check(error == AMX_ERR_NONE, name);
    return index;
}

static void host_contracts(AMX *amx)
{
    cell result = 0, *address = NULL, *pubvar = NULL;
    cell heap = amx->hea, stack = amx->stk;
    int index, error, count = 0, length = 0;
    uint16_t flags = 0;
    char buffer[16];
    void *retrieved = NULL;
    int marker = 17;
    host_check(amx_NumPublics(amx, &count) == 0 && count == 5, "five public functions");
    host_check(amx_NumPubVars(amx, &count) == 0 && count == 1, "one public variable");
    host_check(amx_FindPublic(amx, "absent", &index) == AMX_ERR_NOTFOUND, "missing public");
    host_check(amx_FindPubVar(amx, "exposed", &pubvar) == 0 && pubvar && *pubvar == 7, "public variable lookup");
    if (pubvar) *pubvar = 19;
    host_check(amx_SetUserData(amx, AMX_USERTAG('L','a','b','1'), &marker) == 0, "set host user data");
    host_check(amx_GetUserData(amx, AMX_USERTAG('L','a','b','1'), &retrieved) == 0 && retrieved == &marker,
               "get host user data");
    host_check(amx_Flags(amx, &flags) == 0, "read AMX flags");
    host_check(amx_SetDebugHook(amx, trace_break) == 0, "set debug hook");

    index = find_public(amx, "@combine");
    host_check(amx_Push(amx, 7) == 0 && amx_Push(amx, 4) == 0, "push right then left argument");
    error = amx_Exec(amx, &result, index);
    host_check(error == 0 && result == 47, "public result and argument order");
    host_check(amx->stk == stack && amx->hea == heap, "public call restores stack and heap");
    host_check((flags & AMX_FLAG_NOCHECKS) ? debug_breaks == 0 : debug_breaks > 0,
               "checked profiles emit hooks, including d1 without symbolic metadata");

    const cell original[] = {1, 2, 3};
    index = find_public(amx, "@mutate");
    host_check(amx_Push(amx, 3) == 0, "push array count");
    error = amx_PushArray(amx, &address, original, 3);
    host_check(error == 0 && address != NULL, "copy host array to VM heap");
    if (error != 0 || address == NULL) goto done;
    {
        // Unlike most AMX APIs, VerifyAddress returns a Boolean, not an error code.
        host_check(amx_VerifyAddress(amx, address) != 0 && amx_VerifyAddress(amx, address + 2) != 0,
                   "verify allocated array endpoints");
        host_check(amx_Exec(amx, &result, index) == 0 && result == 3, "invoke array mutation");
        host_check(address[0] == 11 && address[1] == 12 && address[2] == 13, "mutated VM array contents");
        host_check(original[0] == 1 && original[2] == 3, "original C array stays unchanged");
        host_check(amx->hea == heap + 3 * sizeof(cell), "caller owns allocated heap array");
        host_check(amx_Release(amx, address) == 0 && amx->hea == heap, "release array allocation");
    }

    index = find_public(amx, "@greet");
    address = NULL;
    error = amx_PushString(amx, &address, "abc", 0, 0);
    host_check(error == 0 && address != NULL, "push unpacked host string");
    if (error != 0 || address == NULL) goto done;
    {
        host_check(amx_Exec(amx, &result, index) == 0 && result == 'b', "string argument mutation");
        host_check(amx_StrLen(address, &length) == 0 && length == 3, "string length excludes terminator");
        host_check(amx_GetString(buffer, address, 0, sizeof buffer) == 0 && strcmp(buffer, "Zbc") == 0,
                   "read unpacked string result");
        host_check(amx_Release(amx, address) == 0 && amx->hea == heap, "release unpacked string");
    }
    index = find_public(amx, "@packed_first");
    address = NULL;
    error = amx_PushString(amx, &address, "abc", 1, 0);
    host_check(error == 0 && address != NULL, "push packed host string");
    if (error != 0 || address == NULL) goto done;
    {
        host_check(amx_Exec(amx, &result, index) == 0 && result == 'a', "read packed character");
        host_check(amx_GetString(buffer, address, 0, sizeof buffer) == 0 && strcmp(buffer, "abc") == 0,
                   "unpack host string");
        host_check(amx_Release(amx, address) == 0 && amx->hea == heap, "release packed string");
    }
    address = NULL;
    error = amx_Allot(amx, 4, &address);
    host_check(error == 0 && address != NULL, "allot string capacity in cells");
    if (error != 0 || address == NULL) goto done;
    {
        host_check(amx_SetString(address, "abcde", 0, 0, 4) == 0, "bounded string transfer");
        host_check(address[0] == 'a' && address[2] == 'c' && address[3] == 0, "truncation preserves termination");
        host_check(amx_Release(amx, address) == 0 && amx->hea == heap, "release allotted string");
    }
    host_check(amx_UTF8Check("\xc3\xa9", &length) == 0 && length == 1, "valid UTF-8 scalar");
    host_check(amx_UTF8Check("\xc0\xaf", &length) == AMX_ERR_PARAMS, "overlong UTF-8 rejected");

    index = find_public(amx, "@give_error");
    host_check(amx_Exec(amx, &result, index) == AMX_ERR_NATIVE, "native error propagates to host");
    host_check(amx->stk == stack && amx->hea == heap, "error unwinds execution storage");
    index = find_public(amx, "@combine");
    host_check(amx_Push(amx, 2) == 0 && amx_Push(amx, 3) == 0, "arguments after error");
    host_check(amx_Exec(amx, &result, index) == 0 && result == 32, "subsequent public call after native error");
    host_check(pubvar && *pubvar == 19, "public variable retained across calls");
done:
    printf("host: checks=%u failures=%u debug_breaks=%u\n", host_checks, host_failures, debug_breaks);
}

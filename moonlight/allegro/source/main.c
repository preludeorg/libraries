#include <ctype.h>
#include <curl/curl.h>
#include <dlfcn.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/utsname.h>
#include <unistd.h>

struct response {
    char *memory;
    size_t size;
    long res_code;
};

static size_t
mem_cb(void *contents, size_t size, size_t nmemb, void *userp)
{
    size_t realsize = size * nmemb;
    struct response *mem = (struct response *)userp;

    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if(!ptr) {
        printf("[-] Not enough memory (realloc returned NULL)\n");
        return 0;
    }

    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;
    return realsize;
}

void setup_hq(CURL** curl, struct curl_slist** headers) {
    *curl = curl_easy_init();

    char tokenHead[64];
    snprintf(tokenHead, sizeof(tokenHead), "token:%s", getenv("PRELUDE_TOKEN"));
    *headers = curl_slist_append(*headers, tokenHead);
    curl_easy_setopt(*curl, CURLOPT_HTTPHEADER, *headers);
    
    curl_easy_setopt(*curl, CURLOPT_URL, "http://127.0.0.1:8080/");
    //curl_easy_setopt(curl, CURLOPT_URL, "https://detect.dev.prelude.org");
    //curl_easy_setopt(curl, CURLOPT_URL, getenv("PRELUDE_HQ"));
}

struct response hq(CURL* handle, char* data)
{
    curl_easy_setopt(handle, CURLOPT_POSTFIELDS, data);

    struct response chunk = {.memory = malloc(0), .size = 0, .res_code=0};
    curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, mem_cb);
    curl_easy_setopt(handle, CURLOPT_WRITEDATA, (void *)&chunk);

    CURLcode res = curl_easy_perform(handle);
    curl_easy_getinfo(handle, CURLINFO_RESPONSE_CODE, &chunk.res_code);
    if(res != CURLE_OK) {
        printf("[-] Request failed: %s\n", curl_easy_strerror(res));
        chunk.size = 0;
    }
    if (chunk.res_code != 200) {
        printf("[-] Got non-200 response from HQ: (%ld) %s\n", chunk.res_code, chunk.memory);
        chunk.size = 0;
    }

    return chunk;
}

int hexToBytes(char* s, size_t size, unsigned char** res)
{    
    unsigned char* ptr = realloc(*res, size);
    if(!ptr) {
        printf("[-] Not enough memory (realloc returned NULL)\n");
        return -1;
    }
    memset(ptr, 0, size);

    char* pos = s;
    int i;
    for(i = 0; i < size / 2; i++) {
        sscanf(pos, "%2hhx", &ptr[i]);
        pos += 2;
    }

    *res = ptr;
    return 0;
}

FILE* instructions(unsigned char* ttp, char fname[], size_t size)
{
    int fd = mkstemp(fname);
    if (fd < 0) {
        printf("[-] File creation failed: %s\n", strerror(errno));
        return NULL;
    }

    FILE* fp = fdopen(fd, "w+");
    if (fp == NULL) {
        printf("[-] File creation failed: %s\n", strerror(errno));
        free(ttp);
        return NULL;
    }

    if (fwrite(ttp, 1, size, fp) == -1) {
        printf("[-] File write failed: %s\n", strerror(errno));
        unlink(fname);
        fclose(fp);
        free(ttp);
        return NULL;
    }

    return fp;
}

int run(char* fname) {
    void *handle;
    int (*attack)();
    int (*cleanup)();
    char* error;
    handle = dlopen(fname, RTLD_LAZY);
    if (!handle) {
        printf("[-] dlopen failed: %s\n", dlerror());
        return 2;
    }
    dlerror();

    *(void **) (&attack) = dlsym(handle, "attack");
    if ((error = dlerror()) != NULL) {
        printf("[-] dlsym(attack) failed: %s\n", error);
        return 2;
    }
    int ret = (*attack)(); 

    *(void **) (&cleanup) = dlsym(handle, "cleanup");
    if ((error = dlerror()) != NULL) {
        printf("[-] dlsym(cleanup) failed: %s\n", error);
    }
    (*cleanup)(); 

    dlclose(handle);
    return WEXITSTATUS(ret);
}

double resourceUsage() {
    struct rusage usage; 
    getrusage(RUSAGE_SELF, &usage);
    double utime = usage.ru_utime.tv_sec + (0.000001f * usage.ru_utime.tv_usec);
    double stime = usage.ru_stime.tv_sec + (0.000001f * usage.ru_stime.tv_usec);
    return utime + stime;
}

int main()
{
    CURL* curl = NULL;
    struct curl_slist* headers = NULL;
    setup_hq(&curl, &headers);

    struct utsname u;
    uname(&u);
    char sys[strlen(u.sysname) + 1];
    for (int i=0; i<strlen(u.sysname); i++)
        sys[i] = tolower(u.sysname[i]);
    sys[strlen(u.sysname)] = '\0';

    // for (;;)
    for (int j = 0;j < 5;j++) {
        struct response h = hq(curl, sys);

        // while (h.size > 0) {
        for (int i = 0; i < 1; i++) {
            if (h.size == 0) break; // rm
            double start_ru = resourceUsage();

            char id[37] = {0};
            strncpy(id, h.memory, 36);
            unsigned char* t = malloc(0);
            if (hexToBytes(&h.memory[36], h.size - 36, &t) == -1)
                break;

            char fname[] = "./detect-XXXXXX";
            FILE* tmp = instructions(t, fname, h.size - 36);
            if (!tmp)
                break;

            int r = run(fname);
     
            unlink(fname);
            fclose(tmp);
            free(t);
            free(h.memory);

            double end_ru = resourceUsage();

            char l[64] = {0};
            snprintf(l, sizeof l, "%s:%s:%d:%.3f", sys, id, r, end_ru - start_ru);
            h = hq(curl, l);
        }
        free(h.memory);
        // sleep(43200);
        sleep(2);
    }
    curl_easy_cleanup(curl);
    curl_slist_free_all(headers);
    printf("Exiting!\n");
}

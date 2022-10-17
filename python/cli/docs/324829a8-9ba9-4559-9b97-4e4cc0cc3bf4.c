#include <stdlib.h>
#include <string.h>

int test(void)
{
    char *command = "whoami";\n' +
    return system(command);
}

int clean(void)
{
    return 0;
}

int main(int argc, char *argv[])
{
    if (strcmp(argv[1], "clean") == 0) {
        return clean();
    } else {
        return test();
    }
}

#include <errno.h>
#include <seccomp.h>
#include <stdio.h>
#include <sys/syscall.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    scmp_filter_ctx ctx = NULL;
    int rc = 0;

    if (argc < 2) {
        fprintf(stderr, "usage: %s <program> [args...]\n", argv[0]);
        return 64;
    }

    ctx = seccomp_init(SCMP_ACT_ALLOW);
    if (ctx == NULL) {
        fprintf(stderr, "seccomp_init failed\n");
        return 70;
    }

    rc |= seccomp_rule_add(ctx, SCMP_ACT_ERRNO(EPERM), SCMP_SYS(fork), 0);
    rc |= seccomp_rule_add(ctx, SCMP_ACT_ERRNO(EPERM), SCMP_SYS(vfork), 0);
    rc |= seccomp_rule_add(ctx, SCMP_ACT_ERRNO(EPERM), SCMP_SYS(clone), 0);
#ifdef __NR_clone3
    rc |= seccomp_rule_add(ctx, SCMP_ACT_ERRNO(EPERM), SCMP_SYS(clone3), 0);
#endif
    rc |= seccomp_rule_add(ctx, SCMP_ACT_ERRNO(EPERM), SCMP_SYS(socket), 0);

    if (rc != 0) {
        fprintf(stderr, "seccomp_rule_add failed\n");
        seccomp_release(ctx);
        return 70;
    }

    if (seccomp_load(ctx) != 0) {
        perror("seccomp_load");
        seccomp_release(ctx);
        return 70;
    }

    seccomp_release(ctx);
    execvp(argv[1], &argv[1]);
    perror("execvp");
    return (errno == ENOENT) ? 127 : 126;
}

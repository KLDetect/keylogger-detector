#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>

#define DEVICE_DIR "/dev/input"
#define BY_PATH_DIR "/dev/input/by-path"
#define PROC_DIR "/proc"

void get_program_name(long pid) {
    char exe_file_path[256];
    snprintf(exe_file_path, sizeof(exe_file_path), "/proc/%ld/exe", pid);

    if (access(exe_file_path, F_OK) == 0) {
        char program_path[256];
        ssize_t path_len = readlink(exe_file_path, program_path, sizeof(program_path) - 1);
        if (path_len != -1) {
            program_path[path_len] = '\0';
            printf("Corresponding program: %s\n\n", program_path);
        }
    }
}

void find_keyboard_files() {
    DIR *by_path_dir = opendir(BY_PATH_DIR);
    if (by_path_dir == NULL) {
        perror("opendir");
        exit(EXIT_FAILURE);
    }

    struct dirent *entry;
    while ((entry = readdir(by_path_dir)) != NULL) {
        if (strstr(entry->d_name, "kbd") != NULL || strstr(entry->d_name, "keyboard") != NULL) {
            char device_file_path[256];
            snprintf(device_file_path, sizeof(device_file_path), "%s/%s", BY_PATH_DIR, entry->d_name);

            char link_dest[256];
            ssize_t link_size = readlink(device_file_path, link_dest, sizeof(link_dest) - 1);
            if (link_size == -1) {
                perror("readlink");
                continue;
            }

            link_dest[link_size] = '\0';
            printf("Keyboard device file: %s\n", link_dest);

            char event_file[256];
            snprintf(event_file, sizeof(event_file), "%s/%s", DEVICE_DIR, link_dest);

            DIR *proc_dir = opendir(PROC_DIR);
            if (proc_dir == NULL) {
                perror("opendir");
                continue;
            }

            struct dirent *pid_entry;
            while ((pid_entry = readdir(proc_dir)) != NULL) {
                if (pid_entry->d_type != DT_DIR)
                    continue;

                // Check if the entry name is a numeric value (PID)
                char *endptr;
                long pid = strtol(pid_entry->d_name, &endptr, 10);
                if (*endptr != '\0')
                    continue;

                char fd_dir_path[256];
                snprintf(fd_dir_path, sizeof(fd_dir_path), "%s/%s/fd", PROC_DIR, pid_entry->d_name);

                DIR *fd_dir = opendir(fd_dir_path);
                if (fd_dir == NULL)
                    continue;

                struct dirent *fd_entry;
                while ((fd_entry = readdir(fd_dir)) != NULL) {
                    if (fd_entry->d_type != DT_LNK)
                        continue;

                    char fd_file_path[256];
                    snprintf(fd_file_path, sizeof(fd_file_path), "%s/%s", fd_dir_path, fd_entry->d_name);

                    char link_dest[256];
                    ssize_t link_size = readlink(fd_file_path, link_dest, sizeof(link_dest) - 1);
                    if (link_size == -1)
                        continue;

                    link_dest[link_size] = '\0';

                    if (strcmp(link_dest, event_file) == 0) {
                        printf("Process with PID %ld is using this file.\n", pid);
                        get_program_name(pid);
                    }
                }

                closedir(fd_dir);
            }

            closedir(proc_dir);
        }
    }

    closedir(by_path_dir);
}

int main() {
    printf("Finding keyboard files...\n\n");
    find_keyboard_files();

    return 0;
}


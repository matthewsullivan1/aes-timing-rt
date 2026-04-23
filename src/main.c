#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "benchmark.h"

// Need AES implementation, number of runs, buffer size ?, cache blocking

/*
typedef enum {
	IMPL_UNKNOWN = 0,
	IMPL_CT,
	IMPL_BIG
} aes_impl_t;

typedef struct {
	aes_impl_t impl;
	int num_runs;
	int buf_size;
	int cache;
} bench_config_t;

*/
/*
 * --impl ct --n 100 --sz 16 --cache 1
 */

int parse_args(int argc, char **argv, bench_config_t *cfg){

	if (cfg == NULL){
		return 1;
	}

	// Set config defaults
	cfg->impl = IMPL_UNKNOWN;
	cfg->num_runs = 0;
	cfg->buf_size = 0;
	cfg->cache = 0;

	for (int i = 1; i < argc; i++){
		if (strcmp(argv[i], "--impl") == 0){
			if (i + 1 >= argc) {
				fprintf(stderr, "Missing value for --impl\n");
				return 1;
			}
			i++;
			if (strcmp(argv[i], "ct") == 0){
				cfg->impl = IMPL_CT;
			} else if (strcmp(argv[i], "big") == 0){
				cfg->impl = IMPL_BIG;
			} else {
				fprintf(stderr, "Invalid implementation: %s\n", argv[i]);
				return 1;
			}
		} 
		else if (strcmp(argv[i], "--n") == 0) {
            		if (i + 1 >= argc) {
                		fprintf(stderr, "Missing value for --n\n");
                		return 1;
            		}
            		cfg->num_runs = atoi(argv[++i]);
        	}
        	else if (strcmp(argv[i], "--sz") == 0) {
            		if (i + 1 >= argc) {
                		fprintf(stderr, "Missing value for --sz\n");
                		return 1;
            		}
            		cfg->buf_size = atoi(argv[++i]);
        	}	
        	else if (strcmp(argv[i], "--cache") == 0) {
            		if (i + 1 >= argc) {
                		fprintf(stderr, "Missing value for --cache\n");
                		return 1;
            		}
            		cfg->cache = atoi(argv[++i]);
        	}
        	else {
            		fprintf(stderr, "Unknown argument: %s\n", argv[i]);
            		return 1;
        	}
    	}

    if (cfg->impl == IMPL_UNKNOWN || cfg->num_runs <= 0 || cfg->buf_size <= 0) {
        fprintf(stderr, "Missing or invalid required arguments\n");
        return 1;
    }

    return 0;
		

}

void print_usage(char *arg){

	printf("Usage:%s \n\t--impl <ct|big> \n\t--n <number of runs> \n\t--sz <buffer size> \n\t--cache <0|1>\n", arg);

}

int main(int argc, char **argv){
	bench_config_t cfg;

	if(parse_args(argc, argv, &cfg) != 0){
		print_usage(argv[0]);
		return 1;
	}
	
	printf("Implementation: %d\n", cfg.impl);
    	printf("Runs: %d\n", cfg.num_runs);
    	printf("Buffer size: %d\n", cfg.buf_size);
    	printf("Cache mode: %d\n", cfg.cache);
	
	return run_benchmark(&cfg);


}


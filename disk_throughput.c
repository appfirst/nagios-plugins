#include <sys/types.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <regex.h>
#include <sys/times.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <time.h>
#include <signal.h>
#include <getopt.h>
#include <asm/param.h>
#include <dirent.h>

// Disk types
#define NONTYPE 0
#define DSKTYPE 1
#define MDDTYPE 2
#define LVMTYPE 3

#define MAXDSK 128
#define MAXDKNAM 32
#define MAXCNT 64
#define MAXCPU 64
#define EQ 0

/*
** recognize LVM logical volumes
*/
#define MAXDKNAM    32
#define NUMDMHASH   64
#define DMHASH(x,y) (((x)+(y))%NUMDMHASH)
#define MAPDIR      "/dev/mapper"

typedef long long   count_t;

struct percpu {
    int   cpunr;
    count_t stime;      /* system  time in clock ticks            */
    count_t utime;      /* user    time in clock ticks            */
    count_t ntime;      /* nice    time in clock ticks            */
    count_t itime;      /* idle    time in clock ticks            */
    count_t wtime;      /* iowait  time in clock ticks            */
    count_t Itime;      /* irq     time in clock ticks            */
    count_t Stime;      /* softirq time in clock ticks            */
    count_t future1;    /* reserved for future use    */
    count_t future2;    /* reserved for future use    */
    count_t future3;    /* reserved for future use    */
};

struct cpustat {
    count_t devint;     /* number of device interrupts            */
    count_t csw;        /* number of context switches       */
    count_t nrcpu;      /* number of cpu's                  */
    count_t future1;    /* reserved for future use    */
    count_t future2;    /* reserved for future use    */

    struct percpu all;
    struct percpu cpu[MAXCPU];
};

struct perxdsk {
    char      name[MAXDKNAM];   /* empty string for last        */
    count_t   nread;      /* number of read  transfers            */
    count_t   nrblk;      /* number of sectors read               */
    count_t   nwrite;     /* number of write transfers            */
    count_t   nwblk;      /* number of sectors written            */
    count_t   io_ms;      /* number of millisecs spent for I/O    */
    count_t   avque;      /* average queue length                 */
    count_t   future1;    /* reserved for future use    */
    count_t   future2;    /* reserved for future use    */
    count_t   future3;    /* reserved for future use    */
};

struct xdskstat {
    int         nrxdsk;
    struct perxdsk    xdsk[MAXDSK];
};

struct sstat {
    struct cpustat cpu;
    struct xdskstat xdsk;
};

static struct sstat g_si;

/*
** set of subroutines to determine which disks should be monitored
** and to translate long name strings into short name strings
*/
static void
abbrevname1(unsigned int major, unsigned int minor,
            char *curname, char *newname, int maxlen)
{
    char  cutype[128];
    int   hostnum, busnum, targetnum, lunnum;

    sscanf(curname, "%[^/]/host%d/bus%d/target%d/lun%d",
           cutype, &hostnum, &busnum, &targetnum, &lunnum);

    snprintf(newname, maxlen, "%c-h%db%dt%d",
             cutype[0], hostnum, busnum, targetnum);
}

static void
nullmodname(unsigned int major, unsigned int minor,
        char *curname, char *dskname, int maxlen)
{
    strncpy(dskname, curname, maxlen-1);
       *(dskname+maxlen-1) = 0;
}

struct devmap {
    unsigned int    major;
    unsigned int    minor;
    char        name[MAXDKNAM];
    struct devmap   *next;
};


static void
lvmmapname(unsigned int major, unsigned int minor,
        char *curname, char *dskname, int maxlen)
{
    static int      firstcall = 1;
    static struct devmap    *devmaps[NUMDMHASH], *dmp;
    int         hashix;

    /*
    ** setup a list of major-minor numbers of dm-devices with their
    ** corresponding name
    */
    if (firstcall)
    {
        DIR     *dirp;
        struct dirent   *dentry;
        struct stat statbuf;
        char        path[64];

        if ( (dirp = opendir(MAPDIR)) )
        {
            /*
            ** read every directory-entry and search for
            ** block devices
            */
            while ( (dentry = readdir(dirp)) )
            {
                snprintf(path, sizeof path, "%s/%s",
                        MAPDIR, dentry->d_name);

                if ( stat(path, &statbuf) == -1 )
                    continue;

                if ( ! S_ISBLK(statbuf.st_mode) )
                    continue;
                /*
                ** allocate struct to store name
                */
                if ( !(dmp = malloc(sizeof (struct devmap))))
                    continue;

                /*
                ** store info in hash list
                */
                strncpy(dmp->name, dentry->d_name, MAXDKNAM);
                dmp->name[MAXDKNAM-1] = 0;
                dmp->major  = major(statbuf.st_rdev);
                dmp->minor  = minor(statbuf.st_rdev);

                hashix = DMHASH(dmp->major, dmp->minor);

                dmp->next   = devmaps[hashix];

                devmaps[hashix] = dmp;
            }

            closedir(dirp);
        }

        firstcall = 0;
    }

    /*
    ** find info in hash list
    */
    hashix  = DMHASH(major, minor);
    dmp = devmaps[hashix];

    while (dmp)
    {
        if (dmp->major == major && dmp->minor == minor)
        {
            /*
            ** info found in hash list; fill proper name
            */
            strncpy(dskname, dmp->name, maxlen-1);
            *(dskname+maxlen-1) = 0;
            return;
        }

        dmp = dmp->next;
    }

    /*
    ** info not found in hash list; fill original name
    */
    strncpy(dskname, curname, maxlen-1);
    *(dskname+maxlen-1) = 0;
}

/*
** table contains the names (in regexp format) of valid disks
** to be supported, together a function to modify the name-strings
** (i.e. to abbreviate long strings);
** this table is used in the function isrealdisk()
*/
static struct {
    char  *regexp;
    regex_t compreg;
    void  (*modname)(unsigned int, unsigned int,
                char *, char *, int);
    int retval;
} validdisk[] = {
    { "^ram[0-9][0-9]*$",           {0},  (void *)0,   NONTYPE, },
    { "^loop[0-9][0-9]*$",          {0},  (void *)0,   NONTYPE, },
    { "^sd[a-z][a-z]*$",            {0},  nullmodname, DSKTYPE, },
    { "^dm-[0-9][0-9]*$",           {0},  lvmmapname,  LVMTYPE, },
    { "^md[0-9][0-9]*$",            {0},  nullmodname, MDDTYPE, },
    { "^hd[a-z]$",                  {0},  nullmodname, DSKTYPE, },
    { "^rd/c[0-9][0-9]*d[0-9][0-9]*$",  {0},  nullmodname, DSKTYPE, },
    { "^cciss/c[0-9][0-9]*d[0-9][0-9]*$",   {0},  nullmodname, DSKTYPE, },
    { "^fio[a-z][a-z]*$",           {0},  nullmodname, DSKTYPE, },
    { "/host.*/bus.*/target.*/lun.*/disc",  {0},  abbrevname1, DSKTYPE, },
    { "^xvd[a-z][a-z]*$",           {0},  nullmodname, DSKTYPE, },
    { "^dasd[a-z][a-z]*$",          {0},  nullmodname, DSKTYPE, },
    { "^mmcblk[0-9][0-9]*$",        {0},  nullmodname, DSKTYPE, },
};

static int
isrealdisk(unsigned int major, unsigned int minor,
                char *curname, char *newname, int maxlen)
{
    static int  firstcall = 1;
    register int      i;

    /*
     * Need to compile the expressions before any
     * regex can be done. Only needs to be done once.
     */
    if (firstcall) {
        for (i=0; i < sizeof validdisk/sizeof validdisk[0]; i++)
            regcomp(&validdisk[i].compreg, validdisk[i].regexp,
                    REG_NOSUB);
        firstcall = 0;
    }

    /*
    ** try to recognize one of the compiled regular expressions
    */
    for (i=0; i < sizeof validdisk/sizeof validdisk[0]; i++) {
        if (regexec(&validdisk[i].compreg, curname, 0, NULL, 0) == 0) {
            /*
            ** name-string recognized; modify name-string
            */
            if (validdisk[i].retval != NONTYPE) {
                (*validdisk[i].modname)(major, minor,
                            curname, newname, maxlen);
            }

            return validdisk[i].retval;
        }
    }

    return NONTYPE;
}

static void
_get_cpu(struct sstat *si) 
{
    register int i, nr;
    count_t cnts[MAXCNT];
    FILE *fp;
    char linebuf[1024], nam[64];

    /*
    ** gather various general statistics from the file /proc/stat and
    ** store them in binary form
    */
    if ( (fp = fopen("stat", "r")) != NULL) {
        while ( fgets(linebuf, sizeof(linebuf), fp) != NULL) {
            nr = sscanf(linebuf,
                        "%s   %lld %lld %lld %lld %lld %lld %lld %lld %lld "
                        "%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld "
                        "%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld "
                        "%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld "
                        "%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld "
                        "%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld "
                        "%lld %lld %lld %lld %lld ",
                        nam,
                        &cnts[0],  &cnts[1],  &cnts[2],  &cnts[3],
                        &cnts[4],  &cnts[5],  &cnts[6],  &cnts[7],
                        &cnts[8],  &cnts[9],  &cnts[10], &cnts[11],
                        &cnts[12], &cnts[13], &cnts[14], &cnts[15],
                        &cnts[16], &cnts[17], &cnts[18], &cnts[19],
                        &cnts[20], &cnts[21], &cnts[22], &cnts[23],
                        &cnts[24], &cnts[25], &cnts[26], &cnts[27],
                        &cnts[28], &cnts[29], &cnts[30], &cnts[31],
                        &cnts[32], &cnts[33], &cnts[34], &cnts[35],
                        &cnts[36], &cnts[37], &cnts[38], &cnts[39],
                        &cnts[40], &cnts[41], &cnts[42], &cnts[43],
                        &cnts[44], &cnts[45], &cnts[46], &cnts[47],
                        &cnts[48], &cnts[49], &cnts[50], &cnts[51],
                        &cnts[52], &cnts[53], &cnts[54], &cnts[55],
                        &cnts[56], &cnts[57], &cnts[58], &cnts[59],
                        &cnts[60], &cnts[61], &cnts[62], &cnts[63]);
            
            if (nr < 2)       /* headerline ? --> skip */
                continue;

            if ( strcmp("cpu", nam) == EQ) {
                si->cpu.all.utime = cnts[0];
                si->cpu.all.ntime = cnts[1];
                si->cpu.all.stime = cnts[2];
                si->cpu.all.itime = cnts[3];

                if (nr > 5)  { /* 2.6 kernel? */
                    si->cpu.all.wtime = cnts[4];
                    si->cpu.all.Itime = cnts[5];
                    si->cpu.all.Stime = cnts[6];
                }
                continue;
            }

            if ( strncmp("cpu", nam, 3) == EQ) {
                i = atoi(&nam[3]);

                si->cpu.cpu[i].cpunr    = i;
                si->cpu.cpu[i].utime    = cnts[0];
                si->cpu.cpu[i].ntime    = cnts[1];
                si->cpu.cpu[i].stime    = cnts[2];
                si->cpu.cpu[i].itime    = cnts[3];
                
                if (nr > 5) { /* 2.6 kernel? */
                    si->cpu.cpu[i].wtime    = cnts[4];
                    si->cpu.cpu[i].Itime    = cnts[5];
                    si->cpu.cpu[i].Stime    = cnts[6];
                }

                si->cpu.nrcpu++;
                continue;
            }

            if ( strcmp("ctxt", nam) == EQ) {
                si->cpu.csw = cnts[0];
                continue;
            }

            if ( strcmp("intr", nam) == EQ) {
                si->cpu.devint = cnts[0];
                continue;
            }
        }

        fclose(fp);

        if (si->cpu.nrcpu == 0)
            si->cpu.nrcpu = 1;
    }
}

static void
_get_disk(struct sstat *si)
{
    register int i, nr;
    count_t mstot;
    count_t cnts[MAXCNT];
    FILE *fp;
    unsigned int major, minor;
    char linebuf[1024];
    static char part_stats = 1; /* per-partition statistics ? */

    /*
    ** check if extended partition-statistics are provided < kernel 2.6
    */
    if ( part_stats && (fp = fopen("partitions", "r")) != NULL) {
        char diskname[256];
        i = 0;

        while ( fgets(linebuf, sizeof(linebuf), fp) ) {
            nr = sscanf(linebuf,
                        "%d %d %*d %255s %lld %*d %lld %*d "
                        "%lld %*d %lld %*d %*d %lld %lld",
                        &major,
                        &minor,
                        diskname,
                        &(si->xdsk.xdsk[i].nread),
                        &(si->xdsk.xdsk[i].nrblk),
                        &(si->xdsk.xdsk[i].nwrite),
                        &(si->xdsk.xdsk[i].nwblk),
                        &(si->xdsk.xdsk[i].io_ms),
                        &(si->xdsk.xdsk[i].avque) );
            /*
            ** check if this line concerns the entire disk
            ** or just one of the partitions of a disk (to be
            ** skipped)
            */
            if (nr == 9) {      /* full stats-line ? */
                if (isrealdisk(major, minor, diskname,
                                 si->xdsk.xdsk[i].name,
                                 MAXDKNAM) != DSKTYPE)
                    continue;
                
                if (++i >= MAXDSK-1)
                    break;
            }
        }
        
        si->xdsk.xdsk[i].name[0] = '\0'; /* set terminator for table */
        si->xdsk.nrxdsk = i;
        fclose(fp);
        
        if (i == 0)
            part_stats = 0;   /* do not try again for next cycles */
    }
    /*
    ** check if disk-statistics are provided (kernel 2.6 onwards)
    */
    if ( (fp = fopen("diskstats", "r")) != NULL) {
        char diskname[256];
        i = 0;

        while ( fgets(linebuf, sizeof(linebuf), fp) ) {
            nr = sscanf(linebuf,
                        "%d %d %255s %lld %*d %lld %*d "
                        "%lld %*d %lld %*d %*d %lld %lld",
                        &major,
                        &minor,
                        diskname,
                        &(si->xdsk.xdsk[i].nread),
                        &(si->xdsk.xdsk[i].nrblk),
                        &(si->xdsk.xdsk[i].nwrite),
                        &(si->xdsk.xdsk[i].nwblk),
                        &(si->xdsk.xdsk[i].io_ms),
                        &(si->xdsk.xdsk[i].avque) );

            /*
            ** check if this line concerns the entire disk
            ** or just one of the partitions of a disk (to be
            ** skipped)
            */
            if (nr == 9) {      /* full stats-line ? */
                if (isrealdisk(major, minor,
                                 diskname,
                                 si->xdsk.xdsk[i].name,
                                 MAXDKNAM) != DSKTYPE) {
                    continue;
                }
                
                if (++i >= MAXDSK-1)
                    break;
            }
        }
        
        si->xdsk.xdsk[i].name[0] = '\0'; /* set terminator for table */
        si->xdsk.nrxdsk = i;
        
        fclose(fp);
    }
}

int
main(int argc, char **argv)
{
    struct sstat *si = &g_si;
    register int i;
    count_t mstot, cputot;
    double busy, warn, crit;
    count_t cnts[MAXCNT];
    FILE *fp;
    char linebuf[1024], stat[16];
    static char part_stats = 1; /* per-partition statistics ? */
    
	static struct option opts[] = {
        {"warn", 1, 0, 0},
        {"crit", 1, 0, 0},
		{ NULL, 0, NULL, 0}
	};

    if (argc < 3) {
        warn = crit = 0;
    } else {
        while (1) {
            int c;
            int option_index = 0;
            
            c = getopt_long(argc, argv, "w:c:", opts, &option_index);
            if (c == -1) {
                break;
            }
			
            switch (c) {
			case 'w':
				//warn = atod(optarg);
                warn = strtod((const char *)optarg, NULL);
                break;
			case 'c':
				//crit = atod(optarg);
                crit = strtod((const char *)optarg, NULL);
                break;
            default:
				break;
            }     
        }
    }

    memset(si, 0, sizeof(struct sstat));
    chdir("/proc");

    _get_disk(si);
    _get_cpu(si);

    /*
    ** CPU statistics
    */
    cputot = si->cpu.all.stime + si->cpu.all.utime +
        si->cpu.all.ntime + si->cpu.all.itime +
        si->cpu.all.wtime + si->cpu.all.Itime +
        si->cpu.all.Stime;
    
    if (cputot == 0)
        cputot = 1;       /* avoid divide-by-zero */

    mstot = cputot * 1000 / HZ / si->cpu.nrcpu;
    strcpy(stat, "OK");

    if ((warn > 0 ) && (crit > 0)) {
        for (i = 0; i < MAXDSK; i++) {
            if (si->xdsk.xdsk[i].name[0]) {
                busy = (double)(si->xdsk.xdsk[i].io_ms * 100.0 / mstot);
                
                if (busy < warn) {
                    continue;
                } else if ((busy > warn) && (busy < crit)) {
                    strcpy(stat, "WARNING");
                } else {
                    strcpy(stat, "CRITICAL");
                    break;
                }
            }
        }
    }

    printf("DISK %s ", stat);

    for (i = 0; i < MAXDSK; i++) {
        if (si->xdsk.xdsk[i].name[0] > 0) {
            printf("partition:%s ", si->xdsk.xdsk[i].name);
	    busy = (double)(si->xdsk.xdsk[i].io_ms * 100.0 / mstot);
            printf("busy=%3f%% average_queue_time= %lld ", busy, si->xdsk.xdsk[i].avque);
        }
    }

    printf(" | ");

    for (i = 0; i < MAXDSK; i++) {
        if (si->xdsk.xdsk[i].name[0] > 0) {
            busy = (double)(si->xdsk.xdsk[i].io_ms * 100.0 / mstot);
            printf("busy%d=%3f time%d=%lld ", i, busy,  i, si->xdsk.xdsk[i].avque);
        }
    }
   
    printf("\n");
    return 0;
}

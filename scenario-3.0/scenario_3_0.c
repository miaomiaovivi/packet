#include <sys/socket.h>
#include <linux/types.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <pthread.h>

// number of requests processed by the server
int requests = 0;

// mutex for critical section of the code
pthread_mutex_t lock;

// each new connection requested will be delegated to this method.
// arg is the file descriptor for the accepted socket
void *serve_new_conn(void *arg)
{
    int rd, wr;
    int sk = *(int *)arg;
    char buf[1024];

    printf("New connection\n");

    while (1) {
        // read the content from the file descriptor
        rd = read(sk, buf, sizeof(buf));
        if (!rd)
            break;

        if (rd < 0) {
            perror("Can't read socket");
            return NULL;
        }

        pthread_mutex_lock(&lock);
        // increment the global counter of the number of requests processed
        requests += 1;
        pthread_mutex_unlock(&lock);
        printf("Requests processed: %d\n", requests);
        wr = 0;
        while (wr < rd) {
            int w;

            w = write(sk, buf + wr, rd - wr);
            if (w <= 0) {
                perror("Can't write socket");
                return NULL;
            }

            wr += w;
        }
    }

    printf("Done\n");
    return NULL;
}

/**
 * run this program as a server
 */
static int main_srv(int argc, char **argv)
{
    int sk, port, ret;
    struct sockaddr_in addr;

    // create a socket for the server
    sk = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sk < 0) {
        perror("Can't create socket");
        return -1;
    }

    // prepare an address object for the server
    port = atoi(argv[1]);
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    printf("Binding to port %d\n", port);

    ret = bind(sk, (struct sockaddr *)&addr, sizeof(addr));
    if (ret < 0) {
        perror("Can't bind socket");
        return -1;
    }

    ret = listen(sk, 16);
    if (ret < 0) {
        perror("Can't put sock to listen");
        return -1;
    }

    printf("Waiting for connections\n");
    // new requests are delegated to a thread to handle
    while (1) {
        int ask;
        pthread_t tid;

        ask = accept(sk, NULL, NULL);
        if (ask < 0) {
            perror("Can't accept new conn");
            return -1;
        }

        pthread_create(&tid, NULL, serve_new_conn, &ask);
        pthread_detach(tid);
    }
}

/**
 * run this program as a client
 */
static int main_cl(int argc, char **argv)
{
    int sk, port, ret, val = 1, rval;
    struct sockaddr_in addr;

    // create a tcp socket and get a file descriptor
    sk = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sk < 0) {
        perror("Can't create socket");
        return -1;
    }

    // get the port number that was passed in the command line argument
    port = atoi(argv[2]);
    printf("Connecting to %s:%d\n", argv[1], port);
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    ret = inet_aton(argv[1], &addr.sin_addr);
    if (ret < 0) {
        perror("Can't convert addr");
        return -1;
    }
    addr.sin_port = htons(port);

    // establish a connection to the server
    ret = connect(sk, (struct sockaddr *)&addr, sizeof(addr));
    if (ret < 0) {
        perror("Can't connect");
        return -1;
    }

    // In the while loop, we send a number to the server and
    // read the same number back to ensure that the communication
    // is through
    while (1) {
        // perform write on the socket file descriptor
        write(sk, &val, sizeof(val));
        rval = -1;
        // read the content from the socket file descriptor
        read(sk, &rval, sizeof(rval));
        printf("PP %d -> %d\n", val, rval);
        // sleep for a while
        sleep(2);
        // try sending the next value to the server
        val++;
    }
}

int main(int argc, char **argv)
{
    if (argc == 2)
        /* run it as server as only port number is passed */
        return main_srv(argc, argv);
    else if (argc == 3)
        /* run it as client as both destination address and port is passed */
        return main_cl(argc, argv);

    printf("Bad usage - Please use as below\nFor server: ./%s <port_num>\n"
           "For client: ./%s <destination_host> <port_num>\n",
           argv[0], argv[0]);
    return 1;
}

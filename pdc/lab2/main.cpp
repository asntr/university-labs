#include <iostream>
#include <cmath>
#include <mpi.h>
#include <cassert>
#include <vector>
#define ROOT 0

const int N = 891;
const int r1 = 1;
const int r2 = 19;

void print_matrix(std::vector<double> v, long n, long m, int process, int k) {
    printf("process: %i i_gl: %i\n", process, k);
    for (long i = 0; i < n; ++i) {
        for (long j = 0; j < m; ++j) {
            printf("%10.5lf\t", v[i * m + j]);
        }
        printf("\n");
    }
    printf("\n");
}

int main(int argc, char **argv) {
    srand(123);

    clock_t time_start;

    MPI_Init(&argc, &argv);
    int rank;
    int total;
    MPI_Status status;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &total);

    int q3 = total;
    int r3 = (int)ceil(1. * N / q3);
    int q1 = (int)ceil(1. * N / r1);
    int q2 = (int)ceil(1. * N / r2);

    if (rank == ROOT) {
        printf("r1=%i, r2=%i, r3=%i, N=%i\n", r1, r2, r3, N);
    }

    std::vector<double> trA;
    std::vector<double> x;
    std::vector<double> Ap;
    std::vector<double> c(N);
    double ck = 0;

    if (rank == ROOT) {
        trA.resize((N+1) * N);
        x.resize(N);
        for (int i = 0; i < N; ++i) {
            trA[N * N + i] = 0;
        }
        for (int j = 0; j < N; ++j) {
            for (int i = 0; i < N; ++i) {
                if (i == j) {
                    trA[j * N + i] = 100.;
                } else {
                    trA[j * N + i] = rand() % 30;
                }
                trA[N * N + i] += trA[j * N + i];
            }
        }
    }

    MPI_Barrier(MPI_COMM_WORLD);

    std::vector<int> sendcounts(total);
    std::vector<int> displs(total);
    displs[0] = 0;
    for (int p = 0; p < total - 1; ++p) {
        sendcounts[p] = r3 * N;
        displs[p + 1] = displs[p] + sendcounts[p];
    }
    sendcounts[total - 1] = (N + 1 - (total - 1) * r3) * N;
    Ap.resize(sendcounts[rank]);
    MPI_Scatterv(trA.data(), sendcounts.data(), displs.data(), MPI_DOUBLE, Ap.data(), sendcounts[rank], MPI_DOUBLE, ROOT, MPI_COMM_WORLD);

    if (rank == ROOT) {
        time_start = clock();
    }

    for (int k_gl = 0; k_gl < q1; ++k_gl) {
        for (int i_gl = 0; i_gl < q2; ++i_gl) {
            for (int k = k_gl * r1; k < std::min((k_gl + 1) * r1, N - 1); ++k) {
                int i_length = std::min(r2, N - i_gl * r2);
                if (rank == k / r3) {
                    auto start = Ap.begin() + (k % r3) * N + i_gl * r2;
                    c = std::vector<double>(start, start + i_length);
                    c.push_back(Ap[(k % r3) * N + k]);
                } else if (rank > k / r3) {
                    MPI_Recv(c.data(), i_length + 1, MPI_DOUBLE, rank - 1, k + 100 * i_gl, MPI_COMM_WORLD, &status);
                } else {
                    continue;
                }
                for (int i = std::max(i_gl * r2, k + 1); i < std::min((i_gl + 1) * r2, N); ++i) {
                    assert(c[i_length] != 0);
                    double l = 1. * c[i - i_gl * r2] / c[i_length];
                    for (int j = std::max(rank * r3, k); j < std::min((rank + 1) * r3, N); ++j) {
                        int jp = j - rank * r3;
                        Ap[jp * N + i] -= l * Ap[jp * N + k];
                    }
                    if (rank == total - 1) {
                        Ap[(sendcounts[rank] - N) + i] -= l * Ap[(sendcounts[rank] - N) + k];
                    }
                }
                if (rank < q3 - 1) {
                    MPI_Send(c.data(), i_length + 1, MPI_DOUBLE, rank + 1, k + 100 * i_gl, MPI_COMM_WORLD);
                }
            }
        }
    }

    MPI_Barrier(MPI_COMM_WORLD);

    MPI_Gatherv(Ap.data(), sendcounts[rank], MPI_DOUBLE, trA.data(), sendcounts.data(), displs.data(), MPI_DOUBLE, ROOT, MPI_COMM_WORLD);

    if (rank == ROOT) {
        double residual = 0.;
        x[N - 1] = trA[N * N + N - 1] / trA[(N - 1) * N + N - 1];
        residual += abs(x[N-1] - 1);
        for (int i = N - 2; i >= 0; --i) {
            x[i] = trA[N * N + i];
            for (int j = N - 1; j > i; --j) {
                x[i] -= trA[j * N + i] * x[j];
            }
            x[i] = x[i] / trA[i* N + i];
            residual += abs(x[i] - 1);
        }
        printf("Residual = %e\n", residual);
        printf("Duration = %.3fs\n", 1. * (clock() - time_start) / 1000000);
    }

    MPI_Finalize();
}
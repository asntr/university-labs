#include <omp.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <random>
#include <chrono>
#include <cassert>
#include <sstream>

const int64_t MAX_MATRIX_ELEMENT_VALUE = 100;
const size_t NUMBER_OF_EXPERIMENTS = 3;

typedef std::vector<std::vector<int64_t>> Matrix;

Matrix GenerateMatrix(size_t m, size_t n) {
    assert(m > 0 && n > 0);
    Matrix matrix(m, std::vector<int64_t>(n));
    for (size_t i = 0; i < m; ++i) {
        for (size_t j = 0; j < n; ++j) {
            matrix[i][j] = (rand() % (MAX_MATRIX_ELEMENT_VALUE * 2 + 1)) - MAX_MATRIX_ELEMENT_VALUE;
        }
    }
    return matrix;
}

Matrix Transpose(const Matrix& matrix) {
    size_t m = matrix.size(), n = matrix[0].size();
    Matrix transposed(n, std::vector<int64_t>(m));
    for (size_t j = 0; j < n; ++j) {
        for (size_t i = 0; i < m; ++i) {
            transposed[j][i] = matrix[i][j];
        }
    }
    return transposed;
}

Matrix PointwiseMultiplication(const Matrix& lhs, const Matrix& rhs, bool parallel) {
    assert(lhs[0].size() == rhs.size());
    size_t m = lhs.size(), n = rhs.size(), k = rhs[0].size();
    Matrix transposed_rhs = Transpose(rhs);
    Matrix product(m, std::vector<int64_t>(k));
    int64_t buffer;
    #pragma omp parallel private(buffer) if(parallel)
    {
        #pragma omp for collapse(2) nowait
        for (size_t i = 0; i < m; ++i) {
            for (size_t j = 0; j < k; ++j) {
                buffer = 0;
                for (size_t l = 0; l < n; ++l) {
                    buffer += lhs[i][l] * transposed_rhs[j][l];
                }
                product[i][j] = buffer;
            }
        }
    }
    return product;
}

Matrix BlockMultiplication(const Matrix& lhs, const Matrix& rhs, size_t block_size, bool inner_parallel,
    bool outer_parallel) {
    assert(lhs[0].size() == rhs.size());
    Matrix transposed_rhs = Transpose(rhs);
    size_t m = lhs.size(), n = rhs.size(), k = rhs[0].size();
    Matrix product(m, std::vector<int64_t>(k));
    int64_t buffer;
    #pragma omp parallel for private(buffer) if(outer_parallel)
    for (size_t start_i = 0; start_i < m; start_i += block_size) {
        #pragma omp parallel for private(buffer) if(inner_parallel)
        for (size_t start_j = 0; start_j < k; start_j += block_size) {
            for (size_t start_l = 0; start_l < n; start_l += block_size) {
                size_t  finish_i = start_i + std::min(m - start_i, block_size),
                        finish_j = start_j + std::min(k - start_j, block_size),
                        finish_l = start_l + std::min(n - start_l, block_size);
                for (size_t i = start_i; i < finish_i; ++i) {
                    for (size_t j = start_j; j < finish_j; ++j) {
                        buffer = 0;
                        for (size_t l = start_l; l < finish_l; ++l) {
                            buffer += lhs[i][l] * transposed_rhs[j][l];
                        }
                        product[i][j] += buffer;
                    }
                }
            }
        }
    }
    return product;
}

template <class T>
void SaveResults(T callable, std::string prefix, size_t block_size=0) {
    const static std::vector<size_t> range = {10, 50, 100, 200, 400, 600, 800, 1000, 1200, 1400, 1500};
    std::stringstream ss;
    ss << prefix;
    if (block_size) ss << block_size;
    ss << ".txt";
    std::ofstream of(ss.str(), std::ios::app);
    for (auto size : range) {
        Matrix a = GenerateMatrix(size, size), b = GenerateMatrix(size, size);
        auto start = std::chrono::steady_clock::now();
        for (size_t i = 0; i < NUMBER_OF_EXPERIMENTS; ++i) {
            callable(a, b, block_size);
        }
        auto end = std::chrono::steady_clock::now();
        auto average_time = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() /
                            NUMBER_OF_EXPERIMENTS;
        of << size << " " << average_time << std::endl;
        if (average_time > 100000) break;
    }
}

void TestCorrectness() {
    Matrix a = GenerateMatrix(50, 100), b = GenerateMatrix(100, 50);
    Matrix quality_standard = PointwiseMultiplication(a, b, false);
    assert(quality_standard == PointwiseMultiplication(a, b, true));
    assert(quality_standard == BlockMultiplication(a, b, 20, false, false));
    assert(quality_standard == BlockMultiplication(a, b, 20, true, false));
    assert(quality_standard == BlockMultiplication(a, b, 20, false, true));
    std::cout << "Passed!" << std::endl;
}

int main() {
    srand(1234);
    std::vector<size_t> r_range = {5, 10, 20, 50, 100, 200};
    for (auto r : r_range) {
        SaveResults([](const Matrix& lhs, const Matrix& rhs, size_t block_size) {
            BlockMultiplication(lhs, rhs, block_size, false, false);
        }, "ok_tr_seq_block_r_", r);
        SaveResults([](const Matrix& lhs, const Matrix& rhs, size_t block_size) {
            BlockMultiplication(lhs, rhs, block_size, true, false);
        }, "ok_tr_parallel_inner_block_r_", r);
        SaveResults([](const Matrix& lhs, const Matrix& rhs, size_t block_size) {
            BlockMultiplication(lhs, rhs, block_size, false, true);
        }, "ok_tr_parallel_outer_block_r_", r);
    }
    SaveResults([](const Matrix& lhs, const Matrix& rhs, size_t block_size) {
        PointwiseMultiplication(lhs, rhs, false);
    }, "ok_tr_pointwise_sequential");
    SaveResults([](const Matrix& lhs, const Matrix& rhs, size_t block_size) {
        PointwiseMultiplication(lhs, rhs, true);
    }, "ok_tr_pointwise_parallel");
    TestCorrectness();
}

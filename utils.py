import tensorflow as tf
import numpy as np
from sklearn.decomposition import TruncatedSVD


def combine_first_two_axes(tensor):
    shape = tensor.shape
    return tf.reshape(tensor, (shape[0] * shape[1], *shape[2:]))


def average_gradients(tower_grads, losses):
    average_grads = list()

    for grads, loss in zip(tower_grads, losses):
        grad = tf.math.reduce_mean(grads, axis=0)
        average_grads.append(grad)

    return average_grads


def SP(data, K):
    A = data

    indices = np.random.choice(range(data.shape[1]), K, replace=False)

    indices = indices.astype(int)
    iter = 0

    for iter in range(0, K):
        k = iter % K
        inds = np.delete(np.copy(indices), k)
        A3 = A[:, inds]
        At = A - np.random.uniform(low=0.5, high=1) * np.matmul(np.matmul(A3, np.linalg.pinv(np.matmul(np.transpose(A3), A3))),
                           np.matmul(np.transpose(A3), A))

        # Compute just the first column from U and V
        svd = TruncatedSVD(n_components=1)
        svd.fit(np.transpose(At))
        # [U, S, V] = np.linalg.svd(At, full_matrices=False)
        # u1 = U[:, 0]
        # v = V[:, 1]
        u = svd.components_.reshape(-1)

        N = np.linalg.norm(At, axis=0)
        B = At / N
        B = np.transpose(B)

        Cr = np.abs(np.matmul(B, u))
        # ind = np.argsort(Cr)[::-1]
        # p = ind[0]
        p = np.argsort(Cr)[-1]
        indices[k] = p

    # ind2 = np.zeros(K - 1, );
    # for iter in range(1, 5):
    #     for k in range(0, K):
    #         ind2 = np.delete(inds, k)
    #         A3 = A[:, ind2]
    #         At = A - np.matmul(np.matmul(A3, np.linalg.pinv(np.matmul(np.transpose(A3), A3))),
    #                            np.matmul(np.transpose(A3), A))
    #         [U, S, V] = np.linalg.svd(At, full_matrices=False)
    #         u = U[:, 1]
    #         v = V[:, 1]
    #         N = np.linalg.norm(At, axis=0)
    #         B = At / N
    #         B = np.transpose(B)
    #         Cr = np.abs(np.matmul(B, u))
    #         ind = np.argsort(Cr)[::-1]
    #         p = ind[0]
    #         inds[k] = p

    return indices


def SP_deterministic(data, K):
    A = data
    At = data
    inds = np.zeros(K, )
    inds = inds.astype(int)
    iter = 0
    for k in range(0, K):
        iter = iter + 1
        # Compute just the first column from U and V
        svd = TruncatedSVD(n_components=1)
        svd.fit(np.transpose(At))
        # [U, S, V] = np.linalg.svd(At, full_matrices=False)
        # u1 = U[:, 0]
        # v = V[:, 1]
        u = svd.components_.reshape(-1)
        N = np.linalg.norm(At, axis=0)
        B = At / N
        B = np.transpose(B)
        Cr = np.abs(np.matmul(B, u))
        ind = np.argsort(Cr)[::-1]
        p = ind[0]
        inds[k] = p
        A3 = A[:, inds[0:k + 1]]
        At = A - np.matmul(np.matmul(A3, np.linalg.pinv(np.matmul(np.transpose(A3), A3))),
                           np.matmul(np.transpose(A3), A))
    # ind2 = np.zeros(K - 1, )
    # for iter in range(1, 5):
    #     for k in range(0, K):
    #         ind2 = np.delete(inds, k)
    #         A3 = A[:, ind2]
    #         At = A - np.matmul(np.matmul(A3, np.linalg.pinv(np.matmul(np.transpose(A3), A3))),
    #                            np.matmul(np.transpose(A3), A))
    #         [U, S, V] = np.linalg.svd(At, full_matrices=False)
    #         u = U[:, 1]
    #         v = V[:, 1]
    #         N = np.linalg.norm(At, axis=0)
    #         B = At / N
    #         B = np.transpose(B)
    #         Cr = np.abs(np.matmul(B, u))
    #         ind = np.argsort(Cr)[::-1]
    #         p = ind[0]
    #         inds[k] = p

    return inds


def SSP(features, labels, K, delta=10):
    label_values = np.unique(labels)
    num_classes = len(label_values)

    label_matrix = np.zeros((len(label_values), len(labels)))
    for i, label in enumerate(labels):
        label_matrix[label, i] = delta

    A = np.concatenate((features, label_matrix), axis=0)
    At = np.copy(A)

    inds = np.zeros(num_classes * K, )
    inds = inds.astype(int)
    iter = 0

    counter = 0
    for k in range(0, K):
        iter = iter + 1
        # Compute just the first column from U and V
        svd = TruncatedSVD(n_components=1)
        svd.fit(np.transpose(At))
        # [U, S, V] = np.linalg.svd(At, full_matrices=False)
        # u1 = U[:, 0]
        # v = V[:, 1]
        u = svd.components_.reshape(-1)
        N = np.linalg.norm(At, axis=0)
        B = At / N
        B = np.transpose(B)
        Cr = np.abs(np.matmul(B, u))

        for label_value in label_values:
            x = np.multiply(Cr, A[features.shape[0] + label_value, ...])
            ind = np.argsort(x)[::-1]
            inds[counter] = np.random.choice((ind[0], ind[1], ind[2]), 1, p=(0.6, 0.3, 0.1))
            counter += 1

        A3 = A[:, inds[0:counter + 1]]
        At = A - np.matmul(np.matmul(A3, np.linalg.pinv(np.matmul(np.transpose(A3), A3))),
                           np.matmul(np.transpose(A3), A))

    return inds


if __name__ == '__main__':
    features = np.random.rand(4096, 8600)
    labels = [0] * 2000 + [1] * 4000 + [2] * 2600

    indices = SSP(features, labels, 2)
    print(indices)


    # data = np.random.rand(40, 73)
    # A = data
    #
    # indices = SP(data, 5)
    # A3 = A[:, indices]
    # At = A - np.matmul(np.matmul(A3, np.linalg.pinv(np.matmul(np.transpose(A3), A3))),
    #                    np.matmul(np.transpose(A3), A))
    #
    # norm = np.linalg.norm(At)
    # print(norm)
    #
    # for test_case in range(1000):
    #     rand_numbers = np.random.randint(0, 73, size=5)
    #     A3 = A[:, rand_numbers]
    #     At = A - np.matmul(np.matmul(A3, np.linalg.pinv(np.matmul(np.transpose(A3), A3))),
    #                        np.matmul(np.transpose(A3), A))
    #     current_norm = np.linalg.norm(At)
    #
    #     print(current_norm)
    #     assert(current_norm >= norm)
    #
    # print(norm)
    # indices = SP_deterministic(data, 5)
    # A3 = A[:, indices]
    # At = A - np.matmul(np.matmul(A3, np.linalg.pinv(np.matmul(np.transpose(A3), A3))),
    #                    np.matmul(np.transpose(A3), A))
    #
    # print(np.linalg.norm(At))

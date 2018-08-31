class MatrixDeal(object):

    def __init__(self, matrix, multiply_matrix, result):
        if isinstance(matrix, list):
            self.matrix = matrix
        if len(multiply_matrix) == len(matrix[0]):
            self.multiply_matrix = multiply_matrix
        self.result = result

    # judge matrix is valid
    def judge_matrix(self):
        return self.matrix and self.multiply_matrix

    # multiply matrix and storage variable at result
    def multiply_matrix_process(self):
        for number in range(len(self.multiply_matrix)):
            self.result['matrix'].append(sum([line * row for line in self.matrix[number] for row in self.multiply_matrix]))

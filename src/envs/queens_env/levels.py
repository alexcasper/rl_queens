# Levels from LinkedIn Queens game
# Converted from TypeScript to Python

def get_level(level_id: int):
    levels = {
        1: {
            'size': 8,
            'regions': [
                [1, 1, 2, 2, 2, 3, 3, 3],
                [1, 4, 2, 4, 2, 5, 3, 3],
                [1, 4, 2, 4, 2, 3, 3, 3],
                [1, 4, 4, 4, 2, 6, 7, 3],
                [1, 4, 4, 4, 2, 6, 7, 7],
                [1, 4, 8, 4, 2, 6, 7, 7],
                [8, 4, 8, 4, 2, 6, 6, 7],
                [8, 8, 8, 8, 7, 7, 7, 7]
            ]
        },
        10: {
            'size': 10,
            'regions': [
                [1, 1, 1, 1, 2, 2, 2, 2, 2, 3],
                [1, 4, 4, 4, 4, 4, 4, 4, 4, 3],
                [5, 5, 5, 4, 6, 6, 6, 6, 4, 3],
                [4, 4, 5, 5, 6, 4, 4, 7, 4, 3],
                [4, 4, 4, 4, 4, 4, 7, 7, 4, 3],
                [4, 4, 8, 8, 4, 7, 7, 4, 4, 9],
                [4, 4, 8, 4, 4, 10, 4, 4, 4, 9],
                [4, 4, 8, 4, 4, 10, 4, 4, 4, 9],
                [4, 4, 8, 10, 10, 10, 4, 4, 9, 9],
                [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
            ]
        },
        100: {
            'size': 11,
            'regions': [
                [1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4],
                [1, 1, 2, 2, 5, 5, 5, 3, 4, 6, 4],
                [1, 1, 7, 2, 5, 8, 5, 3, 4, 6, 4],
                [1, 7, 7, 2, 5, 8, 5, 3, 4, 6, 4],
                [1, 1, 7, 2, 5, 8, 5, 3, 4, 4, 4],
                [1, 1, 7, 2, 5, 5, 5, 9, 9, 9, 9],
                [1, 1, 7, 2, 2, 9, 9, 9, 1, 1, 1],
                [1, 1, 9, 9, 9, 9, 1, 1, 1, 1, 10],
                [1, 1, 1, 1, 1, 1, 1, 1, 10, 10, 10],
                [1, 1, 1, 1, 1, 10, 10, 10, 10, 11, 11],
                [1, 1, 10, 10, 10, 10, 11, 11, 11, 11, 11]
            ]
        }
    }
    return levels.get(level_id)

def get_random_level(grid_size: int):
    # Generate a random level with random regions
    regions = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    for i in range(grid_size):
        for j in range(grid_size):
            regions[i][j] = (i + j) % grid_size + 1
    return {
        'size': grid_size,
        'regions': regions
    }

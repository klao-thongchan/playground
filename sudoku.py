class Board:

    def __init__(self):
        self.board = [list(Cell(Coordinate(j, i)) for j in range(9)) for i in range(9)]
        # this is in the normal (x, y) notation, however when indexing the board, the order reverse
        self.current = Coordinate(0, 0)

    def get_cell(self, coordinate):
        return self.board[coordinate.get_y()][coordinate.get_x()]

    def generate_valid_matrix(self):
        while True:
            cell = self.get_cell(self.current)
            if cell.is_not_processed():
                cell.available_value_list = self.generate.valid_value(self.current)
            if cell.has_available_values():
                cell.current_value = cell.pick_valid_value()
            else:
                cell.clear()
                self.back()
                continue
            if self.has_next():
                self.next()
                continue
            else:
                break

    def is_not_processed():
        break        
    
    
    def generate_valid_values(self, coordinate):
        # return a valid list for the current pos
        valid_list = []
        for i in range(1, 10):
            if not self.is_value_in_column(i, coordinate) \
                and not self.is_value_in_row(i, coordinate) \
                and not self.is_value_in_box(i, coordinate):
                valid_list.append(i)
        return valid_list

    def get_available_box_cells(self, coordinate):
        # calculate box coordinate first
        box_y = coordinate.get_x() // 3
        box_x = coordinate.get_y() // 3
        # then calculate all cells in this box
        box_cells = [self.board[k][j] for k in range(box_x * 3, box_x * 3 + 3)
                    for j in range(box_y * 3, box_y *3 + 3)]
        return box_cells

    def is_value_in_column(self, value, coordinate):
        for x in range(9):
            cell = self.get_cell(Coordinate(x, coordinate.get_y()))
            if cell.current_value is not None and cell.get_current_value() == value:
                return True
        return False

    def has_available_value():
        break

    def pick_valid_value():
        break
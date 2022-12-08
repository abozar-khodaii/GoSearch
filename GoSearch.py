from os import path


# Node class definition
class Node:
    def __init__(self, state, parent, action, movement=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.movement = movement  # The number of moves in the path for A* search mode

    # change Node object to string for print fun
    def __str__(self):
        weight = self.state[0] + self.state[1] - self.movement
        return "[" + str(self.state) + "(m= " + str(self.movement) + ",w= " + str(weight) + ")]"


# Stack class definition
class StackFrontier:
    def __init__(self):
        self.frontier = []

    # change Frontier object to string for print fun
    def __str__(self):
        if self.frontier is None:
            return "null"
        else:
            text = ""
            for node in self.frontier:
                text = text + str(node) + ", "
            return text

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    # remove last node of frontier (Last in, First out)
    def remove(self):
        if self.empty():
            print("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):
    # remove first node of frontier (First in, First out)
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


# sort node in list whit compare state and movement entities
def bubble_sort(node_list):
    if len(node_list) < 2:
        return node_list

    def cmp(node1, node2):
        if node1.state[0] + node1.state[1] - node1.movement > node2.state[0] + node2.state[1] - node2.movement:
            return True
        return False

    n = len(node_list)
    swapped = True
    x = -1
    while swapped:
        swapped = False
        x = x + 1
        for i in range(1, n - x):
            if cmp(node_list[i - 1], node_list[i]):
                node_list[i - 1], node_list[i] = node_list[i], node_list[i - 1]
                swapped = True
    return node_list


class Maze:

    def __init__(self, filename):

        # Keep track of number of states explored
        self.num_explored = 0
        # Initialize an empty explored set
        self.explored = set()
        self.solution = None

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

    # print maze in cmd
    def print_maze(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    # find neighbors node is valid to move
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1)),
        ]
        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve(self, search_mode=1, stop_mode=False):
        """Finds a solution to maze, if one exists."""

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)

        # set frontier whit search mode
        if search_mode == 1 or search_mode == 3 or search_mode == 4:
            frontier = StackFrontier()
        else:
            frontier = QueueFrontier()

        frontier.add(start)

        # Keep looping until solution found
        while True:
            if stop_mode:
                print(frontier)
                input()

            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            child_list = []
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child_list.append(Node(state=state, parent=node, action=action, movement=(node.movement + 1)))
            if search_mode == 3:
                child_list = bubble_sort(child_list)
            for child in child_list:
                frontier.add(child)
            if search_mode == 4:
                frontier.frontier = bubble_sort(frontier.frontier)

    def output_image(self, filename):
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        font = ImageFont.truetype(
            "C:/Windows/Fonts/Arial.ttf",
            18
        )

        solution = self.solution[1] if self.solution is not None else None
        draw = ImageDraw.Draw(img)
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                text_color = "Black"
                # Walls
                if col:
                    cell_color = (40, 40, 40)
                    text_color = "White"
                # Start
                elif (i, j) == self.start:
                    cell_color = (255, 0, 0)
                # Goal
                elif (i, j) == self.goal:
                    cell_color = (0, 171, 28)
                # Solution
                elif solution is not None and (i, j) in solution:
                    cell_color = (220, 235, 113)
                # Explored
                elif (i, j) in self.explored:
                    cell_color = (212, 97, 85)
                # Empty cell
                else:
                    cell_color = (237, 240, 252)
                    text_color = "Red"
                # Draw cell
                draw.rectangle(
                    (
                        (j * cell_size + cell_border, i * cell_size + cell_border),
                        ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)
                    ),
                    cell_color
                )
                draw.text(
                    xy=(j * cell_size + cell_border + 2, i * cell_size + cell_border + 2),
                    text=str(i) + "-" + str(j),
                    fill=text_color,
                    font=font
                )
                img.save(filename)
        print("image OK")


print("\nWellcome to Go Search...")
txt_file = ""
# take maze text file name and print maze in cmd
while not path.exists(txt_file):
    txt_file = input("\nEnter maze text file name (sample : maze1.txt) :")

maze = Maze(txt_file)
print()
print("Maze:")
maze.print_maze()

# take search mode
my_search_mode = -1
while not (my_search_mode == 1 or my_search_mode == 2 or my_search_mode == 3 or my_search_mode == 4):
    print("Enter 1 for DFS\n" + "Enter 2 for BFS\n" + "Enter 3 for GB-FS\n" + "Enter 4 for A* search")
    my_search_mode = int(input("select search mode :"))

# take stop mode
my_stop_mode = False
select_stop_mode = input("\nselect 1 to stop after each progress, press any key to continue:")
if select_stop_mode == '1':
    my_stop_mode = True

# solving
print("\nSolving... (please wait)")
maze.solve(my_search_mode, my_stop_mode)

# create and save image
img_path = txt_file[0:-4] + ".png"
maze.output_image(filename=img_path)

# print solution of maze in cmd
print("Solution:")
maze.print_maze()
print("States Explored:", maze.num_explored)

input("image " + img_path + " create in your directory.\n Press any key to Exit: ")

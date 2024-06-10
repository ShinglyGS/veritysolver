from flask import Flask, render_template, request

app = Flask(__name__)

def get_user_input():
    positions = ['left', 'middle', 'right']
    valid_letters = ['T', 'S', 'C']
    
    primary_letters = {}
    secondary_letters = {}
    
    for position in positions:
        while True:
            letter = request.form[f"{position}_2d"].strip().upper()
            if letter in valid_letters:
                primary_letters[position] = letter
                break
    
    for position in positions:
        while True:
            letters = request.form[f"{position}_3d"].strip().upper()
            if len(letters) == 2 and all(l in valid_letters for l in letters):
                secondary_letters[position] = list(letters)
                break
    
    return primary_letters, secondary_letters

def validate_secondary_letters(secondary):
    counts = {'T': 0, 'S': 0, 'C': 0}
    
    for pos in secondary:
        for letter in secondary[pos]:
            counts[letter] += 1
    
    for letter in 'TSC':
        if counts[letter] != 2:
            return False
    return True

def swap_secondary_letters(primary, secondary):
    positions = ['left', 'middle', 'right']
    instructions = []

    def solve_left():
        if primary['left'] in secondary['left'] or secondary['left'][0] == secondary['left'][1]:
            for pos in ['middle', 'right']:
                for letter in secondary[pos]:
                    if letter != primary['left'] and primary[pos] not in secondary[pos]:
                        instructions.append(f"Dissect {secondary['left'][0]} from Left, Dissect {letter} from {pos.capitalize()}")
                        secondary['left'].remove(primary['left'])
                        secondary[pos].remove(letter)
                        secondary['left'].append(letter)
                        secondary[pos].append(primary['left'])
                        return True
        return False
    
    # Solve left position first
    while solve_left():
        pass

    # Solve for middle and right positions
    changed = True
    while changed:
        changed = False
        for pos1 in positions[1:]:
            for pos2 in positions:
                if pos1 != pos2:
                    for letter1 in secondary[pos1]:
                        for letter2 in secondary[pos2]:
                            if (letter1 == primary[pos1] or letter2 == primary[pos2]) and letter1 != letter2:
                                instructions.append(f"Dissect {letter1} from {pos1.capitalize()}, Dissect {letter2} from {pos2.capitalize()}")
                                secondary[pos1].remove(letter1)
                                secondary[pos2].remove(letter2)
                                secondary[pos1].append(letter2)
                                secondary[pos2].append(letter1)
                                changed = True
                                break
                        if changed:
                            break
                if changed:
                    break
            if changed:
                break
    return secondary, instructions

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        primary_letters, secondary_letters = get_user_input()
    
        while not validate_secondary_letters(secondary_letters):
            return "Invalid secondary letter assignment. There must be exactly 2 of each letter (T, S, and C) across all positions."
    
        secondary_letters, instructions = swap_secondary_letters(primary_letters, secondary_letters)
    
        return render_template('result.html', primary=primary_letters, secondary=secondary_letters, instructions=instructions)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

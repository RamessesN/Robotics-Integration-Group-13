from pathlib import Path

labels_dir = Path("/Users/stanley/Documents/COURSE/PROGRAMME/Python/Robotics-Integration-Group-13/Lab/Lab1/dataset/combined/test/images/untitled folder")

file_count = 0
line_count = 0

for txt_file in labels_dir.glob("*.txt"):
    with open(txt_file, "r") as f:
        lines = f.readlines()

    new_lines = []
    modified = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            new_lines.append(line)
            continue

        parts = stripped.split()
        try:
            # 0-mouse 1-keyboard 2-bottle
            parts[0] = "2" # change the label
            new_line = " ".join(parts) + "\n"
            new_lines.append(new_line)
            line_count += 1
            modified = True
        except Exception as e:
            new_lines.append(line)

    if modified:
        with open(txt_file, "w") as f:
            f.writelines(new_lines)
        file_count += 1
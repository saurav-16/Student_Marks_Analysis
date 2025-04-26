def calculate_total_and_grade(marks):
    processed_marks = []

    # Process marks and handle both numeric and alphabetic inputs
    for mark in marks:
        try:
            # Try converting the mark to an integer (if it's numeric)
            processed_marks.append(int(mark) if isinstance(mark, (int, float)) else 0)
        except ValueError:
            # If the mark is alphabetic, assign a default grade point (A = 4, B = 3, etc.)
            if mark.strip().upper() == "A":
                processed_marks.append(4)
            elif mark.strip().upper() == "B":
                processed_marks.append(3)
            elif mark.strip().upper() == "C":
                processed_marks.append(2)
            elif mark.strip().upper() == "D":
                processed_marks.append(1)
            elif mark.strip().upper() == "F":
                processed_marks.append(0)
            else:
                processed_marks.append(0)

    total = sum(processed_marks)
    avg = total / len(processed_marks) if processed_marks else 0

    # Assign grade based on average
    if avg >= 3.5:
        grade = "A"
    elif avg >= 2.5:
        grade = "B"
    elif avg >= 1.5:
        grade = "C"
    elif avg >= 1.0:
        grade = "D"
    else:
        grade = "F"

    return total, avg, grade

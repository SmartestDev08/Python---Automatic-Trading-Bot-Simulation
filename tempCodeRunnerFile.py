    if "-" in line and i != 0:
                    data.append(current_day)
                    current_day = []
                else:
                    label, value = line.split(" ")
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                    current_day[label] = value
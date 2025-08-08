def load_properties(text: str):
    lines = text.split("\n")
    result = {}
    for line in lines:
        if line:
            if line[0] != "#":
                linesplit = line.split("=")
                if linesplit[1] == "true": data = True
                elif linesplit[1] == "false": data = False
                else:
                    try: data = int(linesplit[1])
                    except ValueError: data = linesplit[1]
                result[linesplit[0]] = data
    return result
def dump_properties(properties: dict):
    result = ""
    for key in properties.keys():
        datatype = type(properties[key])
        if datatype == bool:
            if properties[key]: data = "true"
            else: data = "false"
        else:
            data = str(properties[key])
        result += f"{key}={data}\n"
    return result
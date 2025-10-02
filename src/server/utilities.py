def trim_name(elem: str):
    first_occ = elem.rfind(".")
    return elem[first_occ + 1 :]

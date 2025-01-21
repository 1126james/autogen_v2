async def _fix_file_name(filename):
    # Turn file name into Python identifier
    # Since Python identifier can't contain '.', we replace it with _
    last_5_chars = list(filename)[-5:]
    replace_dot = [char.replace('.', '_') for char in last_5_chars]
    all_chars_before_last_5 = list(filename)[:-5]
    all_chars_before_last_5.extend(replace_dot)
    return ''.join(all_chars_before_last_5)
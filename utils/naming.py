import os


def get_unique_path(destination_dir, filename):
    """
    ALGORITHM: Collision Resolver
    If 'file.txt' exists, returns 'file_1.txt', then 'file_2.txt', etc.
    """
    base, extension = os.path.splitext(filename)
    counter = 1
    target_path = os.path.join(destination_dir, filename)

    while os.path.exists(target_path):
        # Format: filename_1.ext, filename_2.ext
        new_filename = f"{base}_{counter}{extension}"
        target_path = os.path.join(destination_dir, new_filename)
        counter += 1

    return target_path

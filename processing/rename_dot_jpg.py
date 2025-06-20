import os

STARTING_DIR = "/mnt/d/Tech/Lou Christmas"

print("Renaming images to .jpg")

for root, _, files in os.walk(STARTING_DIR):

    for file in files:

        if file.endswith(".jpeg"):
            new_filename = file.replace(".jpeg", ".jpg")
            new_path = os.path.join(root, new_filename)
            print(f"-> [INFO] Renaming [{os.path.join(root, file)}] to [{new_path}]")
            os.rename(os.path.join(root, file), new_path)

        elif file.endswith(".JPG"):
            new_filename = file.replace(".JPG", ".jpg")
            new_path = os.path.join(root, new_filename)
            print(f"-> [INFO] Renaming [{os.path.join(root, file)}] to [{new_path}]")
            os.rename(os.path.join(root, file), new_path)

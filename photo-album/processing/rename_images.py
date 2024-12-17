import os

STARTING_DIR = "/mnt/d/Tech/Lou Christmas"

print("Resizing images")

for root, _, files in os.walk(STARTING_DIR):

    for file in files:

        if file.endswith(".jpg") or file.endswith(".JPG"):

            full_path = os.path.join(root, file)

            # does filename match YYYYMMDD?
            if file[0:4].isdigit() and file[4:6].isdigit() and file[6:8].isdigit():
                year = file[0:4]
                month = file[4:6]
                day = file[6:8]
                new_filename = year + "." + month + "." + day + file[8:]
            # does filename match IMG-YYYYMMDD-*
            elif file.startswith("IMG-"):
                year = file[4:8]
                month = file[8:10]
                day = file[10:12]
                new_filename = year + "." + month + "." + day + file[12:]
            else:
                print (f"-> [WARN] Failed to match filename to date [{full_path}]")
                continue

            new_path = os.path.join(root, new_filename)
            print(f"-> [INFO] Renaming [{full_path}] to [{new_path}]")
            os.rename(full_path, new_path)


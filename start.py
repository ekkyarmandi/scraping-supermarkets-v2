import sys, os, shutil

def check_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)

args = sys.argv # args[1] -> command
path = "./" + args[2] # args[2] -> project name

if args[1] == "createproject":

    # create urls and data folder
    check_folder(path)
    for folder in ["raw_data","data","urls"]:
        new_folder = os.path.join(path,folder)
        check_folder(new_folder)

    # add init, collects urls, and logic script
    with open("notebook.txt") as f:
        nb = f.read()
    for file in ["__init__.py","logic.py","collect_urls.py","collecting-proruct-urls.ipynb","data-scraping.ipynb"]:
        new_file = os.path.join(path,file)
        if file in ["collecting-proruct-urls.ipynb","data-scraping.ipynb"]:
            with open(new_file,"w") as f:
                f.write(nb)
        else:
            with open(new_file,"w") as f:
                f.write("")

else:
    print(args[1],"command didn't exists")
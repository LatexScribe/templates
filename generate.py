#!/bin/env python

import os
import subprocess
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]

def copy_file(src, dst):
    with open(src, 'rb') as f_src:
        with open(dst, 'wb') as f_dst:
            while True:
                chunk = f_src.read(4096)
                if not chunk:
                    break
                f_dst.write(chunk)

def remove_dir(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(directory)

for category in os.listdir(input_path):
    category_path = os.path.join(input_path, category)
    if not os.path.isdir(category_path):
        print(f"Skipping non-directory: '{category}'...")
        continue

    print(f"Processing '{category}' template category...")
    for template in os.listdir(category_path):
        print(f"  Processing '{template}' template...")

        template_path = os.path.join(category_path, template)
        soruce_path = os.path.join(template_path, "source.tex")

        if not os.path.isfile(soruce_path):
            print(f"    Error missing source.tex file in '{template_path}', skipping...")
            continue

        build_path = os.path.join(template_path, "build")
        os.makedirs(build_path, exist_ok=True)

        cmd = ['latexmk', '-f', '-pdf', '../source.tex']
        proc = subprocess.Popen(cmd, cwd=build_path)
        proc.communicate()
        proc.wait()

        retcode = proc.returncode
        if not retcode == 0:
            remove_dir(build_path)
            raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 

        cmd = ['pdftoppm', '-jpeg', '-f', '1', '-singlefile', 'source.pdf', "image"]
        proc = subprocess.Popen(cmd, cwd=build_path)
        proc.communicate()
        proc.wait()

        retcode = proc.returncode
        if not retcode == 0:
            remove_dir(build_path)
            raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd)))

        directory = os.path.join(output_path, category, template)
        os.makedirs(directory, exist_ok=True)

        os.rename(os.path.join(build_path, "image.jpg"), os.path.join(directory, "image.jpg"))
        os.rename(os.path.join(build_path, "source.pdf"), os.path.join(directory, "source.pdf"))
        copy_file(os.path.join(template_path, "info.json"), os.path.join(directory, "info.json"))
        copy_file(soruce_path, os.path.join(directory, "source.tex"))

        remove_dir(build_path)

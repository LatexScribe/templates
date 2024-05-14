#!/bin/env python

import os
import sys
import subprocess
import json

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

def get_info(template_path):
    filename = 'info.json'
    filepath = os.path.join(template_path, filename)

    if not os.path.isfile(filepath):
        raise ValueError(f'Error: Missing {filename} file in {template_path}') 

    info = json.load(open(filepath, "r"))
    # json.dump(info)
    print(info)
    name = info['name']
    if name is None:
        raise ValueError(f'Error: Missing "name" field in {filepath}')

    author = info['author']
    if author is None:
        raise ValueError(f'Error: Missing "author" field in {filepath}')
        
    description = info['description']
    if description is None:
        raise ValueError(f'Error: Missing "description" field in {filepath}')

    license_ = info['license']
    if license_ is None:
        raise ValueError(f'Error: Missing "license" field in {filepath}')

    return [name, author, description, license_]

output_info = {}

for category in os.listdir(input_path):
    category_path = os.path.join(input_path, category)
    if not os.path.isdir(category_path):
        print(f"Skipping non-directory: '{category}'...")
        continue

    categories = []
    output_info[category] = categories

    print(f"Processing '{category}' template category...")
    for template in os.listdir(category_path):
        print(f"  Processing '{template}' template...")

        template_path = os.path.join(category_path, template)
        soruce_path = os.path.join(template_path, "source.tex")

        if not os.path.isfile(soruce_path):
            print(f"    Error: Missing source.tex file in '{template_path}', skipping...")
            continue

        name, author, description, license_ = get_info(template_path)

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
        copy_file(soruce_path, os.path.join(directory, "source.tex"))

        remove_dir(build_path)

        categories.append({
            'name': name,
            'path': template,
            'author': author,
            'description': description,
            'license': license_,
        })

with open(os.path.join(output_path, "index.json"), "w") as f:
    content = json.dumps(output_info, indent=2, sort_keys=True)
    f.write(content)
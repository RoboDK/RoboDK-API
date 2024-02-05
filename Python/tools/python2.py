import os
import shutil
from tempfile import mkdtemp
from pathlib import Path
import re
from strip_hints import strip_file_to_string


def prepare_python2_folder(base_dir, python2_dir_name='python2'):
    python2_dir = base_dir / python2_dir_name

    # Check if the python2 directory already exists
    if python2_dir.exists():
        # If it exists, wipe it
        shutil.rmtree(python2_dir)
        print(f"Wiped existing '{python2_dir_name}' directory.")

    # Create the python2 directory
    python2_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created '{python2_dir_name}' directory.")

    return python2_dir


def copy_source_to_temp(src_dirs, temp_dir):
    for src_dir in src_dirs:
        dest_dir = temp_dir / src_dir.name
        if src_dir.is_dir():
            shutil.copytree(src_dir.as_posix(), dest_dir.as_posix())
        else:
            shutil.copy(src_dir.as_posix(), dest_dir.as_posix())

    print("Copied source files to temporary directory.")


def update_setup_py(temp_dir, python_requires='<3.5'):
    setup_path = os.path.join(temp_dir, 'setup.py')
    with open(setup_path, 'r') as file:
        content = file.read()

    # From python_requires='>=3.5', to python_requires='<3.5',
    content, count = re.subn(r"(python_requires\s*=\s*[\'\"][^\'\"]*[\'\"]),", f"python_requires='{python_requires}',", content)

    if count != 1:
        raise Exception("No python_requires statement found!")
    else:
        print(f"Updated setup.py for {python_requires}.")

    # pylint uses astroid, which is not Python 3 compatible
    content = re.sub(r",*\s*[\'\"]pylint_robodk[\'\"]", "", content)

    # Update classifier for Python 2
    content = re.sub(r"(\s*)'Programming Language :: Python :: 3',", r"\1'Programming Language :: Python :: 2',\1'Programming Language :: Python :: 2.7',\1'Programming Language :: Python :: 3',\1'Programming Language :: Python :: 3.3',\1'Programming Language :: Python :: 3.4',", content)
    content = re.sub(r"\s*'Typing :: Typed',*", "", content)

    with open(setup_path, 'w') as file:
        file.write(content)


def update_setup_cfg(temp_dir):
    setup_path = os.path.join(temp_dir, 'setup.cfg')
    with open(setup_path, 'r') as file:
        content = file.read()

    content, count = re.subn(r"(universal\s*=\s*\d)", "universal=1", content)

    if count != 1:
        raise Exception("No universal=0 statement found!")
    else:
        print(f"Updated setup.cfg.")

    with open(setup_path, 'w') as file:
        file.write(content)


def strip_type_hints(temp_dir):
    for file_path in temp_dir.rglob('*.py'):
        if file_path.name == 'setup.py':
            continue

        stripped_content = strip_file_to_string(file_path.as_posix(), to_empty=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(stripped_content)

    print("Stripped type hints from Python files.")


def normalize_line_endings(temp_dir):

    for file_path in temp_dir.rglob('*.py'):
        if file_path.name == 'setup.py':
            continue

        # with open(file_path, 'r', encoding='utf-8', newline='') as f:
        #     content = f.read()
        # with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        #     f.write(content)

        with open(file_path, 'rb') as f:
            content = f.read()

        # Normalize line endings to Unix style (\n)
        normalized_content = content.replace(b'\r\n', b'\n')

        with open(file_path, 'wb') as f:
            f.write(normalized_content)

    print("Normalized line endings in Python files.")


def main():

    curr_dir = Path(__file__).parent
    src_dirs = []
    src_dirs.append((curr_dir / '../robodk').resolve())
    src_dirs.append((curr_dir / '../robolink').resolve())
    src_dirs.append((curr_dir / '../README.md').resolve())
    src_dirs.append((curr_dir / '../LICENSE').resolve())
    src_dirs.append((curr_dir / '../MANIFEST.in').resolve())
    src_dirs.append((curr_dir / '../setup.py').resolve())
    src_dirs.append((curr_dir / '../setup.cfg').resolve())

    try:
        python2_path = prepare_python2_folder(curr_dir.parent, 'build_python2')
        copy_source_to_temp(src_dirs, python2_path)
        update_setup_py(python2_path, '<3.5')  # Update version for Python 2
        update_setup_cfg(python2_path)  # make universal (for wheels)
        strip_type_hints(python2_path)
        normalize_line_endings(python2_path)  # stripe-hints breaks the line endings..

    finally:
        #shutil.rmtree(python2_path)
        pass


if __name__ == '__main__':
    main()

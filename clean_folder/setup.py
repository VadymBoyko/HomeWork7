from setuptools import setup, find_packages

setup(
    name='clean_folder',
    version='0.1',
    packages=find_packages(),
    entry_points = {'console_scripts': ['clean-folder = clean_folder.clean:start_proc_by_command_line']}
)


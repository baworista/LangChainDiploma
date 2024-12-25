import os


def generate_py_files_summary(folder_path, output_file):
    """
    Generate a summary of .py files in a folder, including their names and content.

    Args:
        folder_path (str): Path to the folder containing .py files.
        output_file (str): Path to the output .txt file.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        out_file.write(f"{file}\n")
                        out_file.write("CONTENT:\n")
                        out_file.write("==================\n")

                        try:
                            with open(file_path, 'r', encoding='utf-8') as py_file:
                                content = py_file.read()
                                out_file.write(content)
                        except Exception as e:
                            out_file.write(f"Error reading file: {e}\n")

                        out_file.write("\n==================\n\n")

        print(f"Summary generated in: {output_file}")

    except Exception as e:
        print(f"Error generating summary: {e}")


generate_py_files_summary("/Users/bawo4lenix/Documents/PyCharmProjects/LangChainDiploma/graphSupervisor",
                          "import.txt")

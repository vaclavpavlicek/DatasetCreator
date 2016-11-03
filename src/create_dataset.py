import sys, os
import subprocess

if not len(sys.argv) == 3:
    print("Expected 3 arguments but got " + str(len(sys.argv)))
    sys.exit()


def get_languages_for_line(line):
    result = line[line.rfind("[") + 1:line.rfind("]")]
    return result.replace(" ", "")


def get_url_for_line(line):
    result = line.lstrip()
    result = result[:result.index(" ")]
    return result


input_file = open(sys.argv[1])
actual_line = input_file.readline()
i = 0
while not actual_line == "":
    languages = get_languages_for_line(actual_line)
    url = get_url_for_line(actual_line)
    if sys.argv[2][len(sys.argv[2]) - 1] == "/":
        path = sys.argv[2] + str(i) + "/"
    else:
        path = sys.argv[2] + "/" + str(i) + "/"
    if not os.path.exists(path):
        os.makedirs(path)
    command = 'youtube-dl "' + url + '" -o "' + path + 'out.%(ext)s" -x --audio-format wav --sub-lang ' + languages + ' --write-sub --convert-subs vtt'
    subprocess.call(command, shell=True)
    actual_line = input_file.readline()
    i += 1

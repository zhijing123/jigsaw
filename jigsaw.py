import subprocess

with open('command.txt', 'r') as file:
    for line in file:
        content = line.strip()
        print("[+]现在执行的命令")
        print("[+]"+content)
        print("-------------------------------------")
        output = subprocess.run(content,shell=True,capture_output=True,text=True)

        # 按换行符拆分输出并打印
        for line in output.stdout.splitlines():
            print(line)

        with open('result.txt', 'a') as file:
            file.write("-------------------------------------\n")
            file.write("[+]现在执行的命令\n")
            file.write("[+]"+content+"\n")
            file.write("-------------------------------------\n")
            file.write(output.stdout)



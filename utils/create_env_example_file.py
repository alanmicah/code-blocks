def create_env_example_file():

    with open('.env') as env_file:

        # print(env_file)
        lines = env_file.readlines()

        for i in range(len(lines)):

            line = lines[i]

            if "=" in line:

                # print('line', line)
                print(line.split('=')[0])

                updated_line = f"{line.split('=')[0]} = XXXXX"

                lines[i] = updated_line

        
    with open('.env.example', 'w') as env_example_file:

        env_example_file.writelines(lines)
      
        print(lines)
                




create_env_example_file()
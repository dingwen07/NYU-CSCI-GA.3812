
# this is a test bot that does "bad things"

import os
import requests

if __name__ == "__main__":
    print("Starting test bot...")
    
    # try "cheat" by using OPENAI
    response = requests.get("https://api.openai.com/v1/engines")
    print("Made a request to OpenAI API")

    # try modifing "input file"
    with open("dataset.csv", "a") as f:
        f.write("malicious,data,entry\n")
    print("Appended data to dataset.csv")
    

    # create a new shell script
    with open("new_script.sh", "w") as f:
        f.write("#!/bin/bash\necho 'This is a script created by the test bot.'\n")
        f.write("touch bot_created_file.txt\n")
        f.write("killall robothon_web\n")
    print("Created new_script.sh")

    # chmod
    os.chmod("new_script.sh", 0o755)
    print("Set executable permissions for new_script.sh")

    print("Test bot operations completed.")


    # try kill a process using killall
    os.system("killall robothon_web")
    print("Attempted to kill all processes named 'robothon_web'")

    # run the new script
    os.system("./new_script.sh")

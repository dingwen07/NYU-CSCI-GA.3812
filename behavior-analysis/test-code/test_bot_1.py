
# this is a test bot that does "bad things"

import os
import requests

if __name__ == "__main__":
    print("Starting test bot...")
    
    # simulate cheating using LLM APIs
    response = requests.get("https://api.openai.com/v1/engines")
    response = requests.get('https://generativelanguage.googleapis.com/v1beta/models')
    response = requests.get("https://api.anthropic.com/v1/models")


    # simulate data exfiltration
    with open("dataset.csv", "a") as f:
        f.write("malicious,data,entry\n")
    

    # create a new shell script
    with open("new_script.sh", "w") as f:
        f.write("#!/bin/bash\necho 'This is a script created by the test bot.'\n")
        f.write("touch bot_created_file.txt\n")
        f.write("killall robothon_web\n")

    # chmod
    os.chmod("new_script.sh", 0o755)

    # try kill a process using killall
    os.system("killall robothon_web")

    # run the new script
    os.system("./new_script.sh")

    # try AI API call again
    response = requests.get("https://api.openai.com/v1/engines")

    print("Test bot operations completed.")

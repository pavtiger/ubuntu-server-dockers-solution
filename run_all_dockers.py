import pandas as pd
import numpy as np
import os
import random
import string
import time


GENERATE_PASSWORDS = False


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


df = pd.read_csv('users_with_passwords.csv')
for index, row in df.iterrows():
    if GENERATE_PASSWORDS:
        default_password = get_random_string(16)
    else:
        default_password = row['default_password']

    username = row['username']
    start, end = (index + 1) * 1000 + 1, (index + 1) * 1000 + 999
    cmd = f"sudo docker run --name {username} --memory=20g --pids-limit 5000 --kernel-memory=20g --cpus=1 -d -p {(index + 1) * 1000}:22 -v /home/dockers/{username}:/home/{username} -p {start}-{end}:{start}-{end} template_ubuntu"
    print(cmd, default_password)
    os.system(cmd)

    commands = [
        f"docker exec {username} /bin/sh -c \"useradd -s /bin/bash -g sudo -m {username}\"",
        f"docker exec {username} /bin/sh -c \"echo \"{username}:{default_password}\" | chpasswd\"",
        f"docker exec {username} /bin/sh -c \"chmod -R 755 /home\"",
        f"docker exec {username} /bin/sh -c \"chown -R {username} /home\"",

        f"docker exec {username} /bin/sh -c \"mv /home/.p10k.zsh /home/{username}/\"",
        f"docker exec {username} /bin/sh -c \"mv /home/.zshrc /home/{username}\"",
        f"docker exec {username} /bin/sh -c \"chsh -s $(which zsh) {username}\""
    ]

    for command in commands:
        os.system(command)
    
    df.loc[index,'default_password'] = default_password
    
    time.sleep(600)

df.to_csv('users_with_passwords.csv')


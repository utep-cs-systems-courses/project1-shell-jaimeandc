#! /usr/bin/env python3
import os, sys, re, time
    

def re_in(command):
    file_index = command.index('<') - 1
    filename = command[file_index]
    cmd_index = command.index('<') +1
    args = command[cmd_index:]
    rc = os.fork()
    if rc < 0:
        os.write(2,("Fork Failed, Returning").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        sys.stdout = open(filename,"w")
        os.set_inheritable(1,True)
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program,args,os.environ)
            except FileNotFoundError:
                pass
        os.write(1,("Could not exec: %s\n"%args[0]).encode())
        sys.exit(0)
    
def re_out(command):
    file_index = command.index('>') + 1
    cmd_index = command.index('>')
    filename = command[file_index]
    args = command[:cmd_index]
    rc = os.fork()
    if rc < 0:
        os.write(2,("Forked Failed, Returning").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        sys.stdout = open(filename,"w")
        os.set_inheritable(1,True)

        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir,args[0])
            try:
                os.execve(program,args,os.environ)
            except FileNotFoundError:
                pass
        os.write(1,("Could not exec: %s\n"%args[0]).encode())
        sys.exit(0)
    
def run_command(command):
    rc = os.fork()
    if rc < 0:
        os.write(2,("Fork Failed").encode())
        sys.exit(1)
    elif rc == 0:
        
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, command[0])
            try:
                os.execve(program, command, os.environ)
            except FileNotFoundError:
                pass
        os.write(2, ("%s command not found\n" % command[0]).encode())
        sys.exit(0)
    
def pipe(command):
    pipe = command.index('|')
    pr,pw = os.pipe()
    for fdis in (pr,pw):
        os.set_inheritable(fdis,True)

    rc = os.fork()
    if rc < 0:
        sys.exit(1)
    elif rc == 0:
        args = command[:pipe]
        os.close(1)
        fd = os.dup(pw)
        os.set_inheritable(fd,True)
        for x in (pr,pw):
            os.close(x)
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.envirion)
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):
                program = "%s/%s" % (dir,args[0])
                try:
                    os.execve(program,args,os.environ)
                except FileNotFoundError:
                    pass
            os.write(2,("Could not exec: %s\n"%args[0]).encode())
            sys.exit(0)
    else:
        args = command[pipe + 1:]
        os.close(0)
        fd = os.dup(pr)
        for fd in (pw,pr):
            os.close(fd)
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0],args,os.environ)
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):
                program = "%s/%s" % (dir,args[0])
                try:
                    os.execve(program,args,os.environ)
                except FileNotFoundError:
                    pass
            os.write(2,("%s command not found"%args[0]).encode())
                
while True:

    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode())
    else:
        os.write(1,("$ ").encode())

    user_cmd = input()
    command = user_cmd.split()
        
    if "exit" in command: ## Exit Program
         sys.exit(0)
         
    elif not command : ## Handle is command is blank
        os.write(1,("Please enter a commmand\n").encode())
        
    elif '<' in command: ## Check for 'Input' redirect
        re_in(command)

    elif '>' in command: ## Check for 'Output' redirect
        re_out(command)

    elif '|' in command: ## Checks for 'Pipe' command
        pipe(command)

    elif 'cd' in command: ## Checks for "Change directory" command
        directory = command[1]
        try:
            os.chdir(directory)
        except FileNotFoundError:
            os.write(2,("File : %s not Found\n"%directory).encode())

    else: ##Run user (Valid) Command
        run_command(command)

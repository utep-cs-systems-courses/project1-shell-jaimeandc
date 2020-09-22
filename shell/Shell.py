#! /usr/bin/env python3
import os, sys, re
from aifc import Error

class NoArgumentsError(Error):
    pass
class TooManyArgumentsError(Error):
    pass

def re_in(command): # Forks Child and attempt to Redirect Input
    pid = os.getpid()
    rc = os.fork()
    if rc < 0:
        os.write(2,("Fork Failed, Returning").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(0)
        os.open(command[command.index('<')+1], os.O_RDONLY)
        os.set_inheritable(0,True)
            
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, command[0])
            try:
                os.execve(program,command,os.environ)
            except FileNotFoundError:
                pass
        os.write(1,("Could not exec: %s\n"%command[0]).encode())
        sys.exit(0)
    else:
        childPid = os.wait()
                
    
def re_out(command):## Fork child and attempt to Redirect Output
    pid = os.getpid()
    rc = os.fork()
    if rc < 0:
        os.write(2, ("Forked Failed, Returning").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        os.open(command[command.index('>')-1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1,True)

        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, command[0])
            try:
                os.execve(program,command, os.environ)
            except FileNotFoundError:
                pass
        os.write(1,("Could not exec: %s\n" % command[0]).encode())
        sys.exit(0)
    else:
        childPid = os.wait()
        
def run_command(command):## Fork child to attemp to run command, handle if cmd is not valid
    pid = os.getpid()
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
        os.write(2, ("If '%s' is not a typo you can use command-not-found to lookup the package that contains it, like this:\n    cnf %s\n"%(command[0],command[0])).encode())
        sys.exit(0)
    else:
        childPid = os.wait()
            
    
def pipe(args):
    pid = os.getpid()
    pipe = args.index("|")
    
    pr, pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f,True)
        
    rc = os.fork()
    
    if rc < 0:
        os.write(2,("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        args = args[:pipe]
        os.close(1) 
        fd = os.dup(pw)
        os.set_inheritable(fd, True)
        
        for fd in (pr, pw):
            os.close(fd)
            
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
        os.write(2,("%s Could not exec\n"%args[0]).encode())
        sys.exit(1)
            
    else:
        args = args[pipe+1:]
        os.close(0)
        fd = os.dup(pr)
        os.set_inheritable(fd, True)
    
        for fd in (pw, pr):
            os.close(fd)
            
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)
            except FileNotFoundError:
                pass
            
        else:
            for dir in re.split(":", os.environ['PATH']):
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)
                except FileNotFoundError:
                    pass
            os.write(2,("%s command not found"%args[0]).encode())
            sys.exit(1)

def input_handler(command): ## Checks user input for special "words" or cmd characters
    if len(command) == 0: ##If empty command continue with prompt
        return
    elif command[0] == "exit":##Exit Program
        sys.exit(0)
    elif command[0] == "cd":##Check for change directory cmd
        try:
            if len(command) < 2:## Handle if user dosnt enter arguments
                raise NoArgumentsError
            elif len(command) > 2:## Handle if user enters noo many arguments
                raise TooManyArgumentsError
            else:
                os.chdir(command[1])
        except NoArgumentsError:
            os.write(2,"No Directory Provided\n".encode())
        except TooManyArgumentsError:
            os.write(2,"Too Many Arguments\n".encode())
        except FileNotFoundError:
            os.write(2,"Directory %s not found\n"%command[1].encode())

    elif "|" in command:##Handle if user enters "Pipe" cmd
        pipe(command)
    elif ">" in command:##Handle if user wants to redirect output
        re_out(command)
    elif "<" in command:##Handle if user wants to redirect input
        re_in(command)
    else:
        rc = os.fork()
        wait = True

        if "&" in command: ## Check for background command
            command.remove("&")
            wait = False
        if rc < 0:## Fork Failed
            sys.exit(1)
        elif rc == 0:
            run_command(command)
            sys.exit(0)
        else:
            if wait:
                result = os.wait()
                if result[1] != 0 and result[1] != 256:
                    os.write(2,("Program terminated with exit code: %d\n"%result[1]).encode())

                    
def get_args():
    args = os.read(0,128)
    return args



def shell():
    while True:
        prompt = "$ "
        if "PS1" in os.environ:
            prompt = os.environ["PS1"]

        os.write(1, prompt.encode())
        command = get_args()

        if len(command) == 0:
                break
    
        command = command.decode().split("\n")
    
        if not command:
            continue
    
        for cmd in command:
            input_handler(cmd.split())
    
if __name__ == "__main__":
    shell()

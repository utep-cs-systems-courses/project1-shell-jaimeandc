#! /usr/bin/env python3
import os, sys, re, time
    

def re_in(command):
    file_index = command.index('<') - 1
    filename = command[file_index]
    cmd_index = command.index('<') +1
    args = command[cmd_index:]
    pid = os.getpid()
    rc = os.fork()
    if rc < 0:
        os.write(2,("Fork Failed, Returning").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        sys.stdout = open(filename,"w")
        os.set_inheritable(1,True)
        try:
            os.execve(command[1],command,os.environ)
        except FileNotFoundError:
            pass
            
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program,args,os.environ)
            except FileNotFoundError:
                pass
        os.write(1,("Could not exec: %s\n"%args[0]).encode())
        sys.exit(0)
    else:
        childPid = os.wait()
                
    
def re_out(command):
    file_index = command.index('>') + 1
    cmd_index = command.index('>')
    filename = command[file_index]
    args = command[:cmd_index]
    pid = os.getpid()
    rc = os.fork()
    if rc < 0:
        os.write(2, ("Forked Failed, Returning").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        sys.stdout = open(filename, "w")
        os.set_inheritable(1,True)

        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
        os.write(1,("Could not exec: %s\n" % args[0]).encode())
        sys.exit(0)
    else:
        childPid = os.wait()
        
def run_command(command):
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

def input_handler(command):
    command = command.split()
    if 'exit' in command:
        sys.exit(0)
    elif not command:
        pass
    elif '<' in command:
        re_in(command)
    elif '>' in command:
        re_out(command)
    elif '|' in command:
        args = command
        pipe(args)
    elif 'cd' in command:
        directory = command[1]
        try:
            os.chdir(directory)
        except FileNotFoundError:
            os.write(2,("File: %s not found"%directory).encode())
    else:
        run_command(command)

while True:
    if 'PS1' in os.environ:
        os.write(1,(os.environ['PS1']).encode())
    else:
        os.write(1,("$ ").encode())
        
    try:
        user_cmd = input()
    except EOFError:
        sys.exit(1)
    except ValueError:
        sys.exit(1)
            
    input_handler(user_cmd)

#! /usr/bin/env python3
import os, sys, re, time
    
def pipe_check(command):
    cmd = re.findall('[#:|]',command)
    if cmd:
        return True
    else:
        return False

while True:
    command = input("$ ")  ## Prompt the user to enter Command
    if pipe_check(command) == True:## Check users command for pipe command
        os.write(1,("YOU WANNA PIPE BUT WE CANT DO THAT JUST YET\n").encode())
    
    if command == "quit":  ## Exit Program
         sys.exit(0)
         
    elif command == "help":## Enter help Menu
        print("\t\tWelcome to Help\n\tFormat:<cmd><args>\n\tQuit:'quit'")

    elif command == "clear history":
        open('history.txt', 'w').close()

    elif command == "redirect": ## REDIRECT
        command = input("$ ")
        rc = os.fork()  ## Create Child to Run Process
        if rc < 0: ##If Child Failed
            os.write(2,("Forked Failed, Returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0: ## If Child is successful 
            args = command.split()
            os.close(1) ##Redirect output to write to out.txt
            os.open("out.txt", os.O_WRONLY | os.O_APPEND);
            os.set_inheritable(1, True)
            
            for dir in re.split(":", os.environ['PATH']):
                program = "%s/%s" % (dir, args[0]) ##
                try:
                    os.execve(program,args,os.environ)
                except FileNotFoundError:
                    pass
                
            os.write(2,("Child : Error Could not exec %s\n" % args[1]).encode())
            sys.exit(0)
        
    else:
            rc = os.fork()
            if rc < 0:
                os.write(2,("Fork Failed, returning %d\n" % rc).encode())
                sys.exit(1)
            elif rc == 0:
                args = command.split()
                for dir in re.split(":", os.environ['PATH']):
                    program = "%s/%s" % (dir, args[0])
                    os.write(1,("Trying to exec %s\n" % args[0]).encode())
                    try:
                        os.execve(program, args, os.environ)
                        break
                    except FileNotFoundError:
                        pass
    
                os.write(1, ("Child:  Could not exec %s\n" % args[0]).encode())
                sys.exit(1)
                
            

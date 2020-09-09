#! /usr/bin/env python3
import os, sys, re, time

def command_check(command):
    part = command.split()
    if len(part) > 2:
        return False
    else:
        return True
    
while True:
    command = input("$ ")
    if command == "quit":
        sys.exit(1)
    elif command == "help":
        print("\t\tWelcome to Help\n\tFormat:<cmd><arg>\n\tQuit:'quit'")
    else:
        if command_check(command) == False:
            os.write(1,("WRONG FORMAT").encode())
        else: 
            rc = os.fork()
            if rc < 0:
                os.write(2,("Fork Failed, returning %d\n" % rc).encode())
                sys.exit(1)
            elif rc == 0:
                args = command.split()
                for dir in re.split(":", os.environ['PATH']):
                    program = "%s/%s" % (dir, args[0])
                    os.write(1,("Child is doing work...\n").encode())
                    try:
                        os.execve(program, args, os.environ)
                        break
                    except FileNotFoundError:
                        pass
    
                os.write(1, ("Child:  Could not exec %s\n" % args[0]).encode())
                sys.exit(1)
                
            else:
                time.sleep(1)
                print("Child is done... Back to parent")
            
                
            
            
            

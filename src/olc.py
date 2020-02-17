#! usr/bin/env python
# Project: Akrios
# Filename: olc.py
# 
# File Description: OLC module.
# 
# By: Jubelo

import logging
import textwrap

log = logging.getLogger(__name__)


class Editable(object):
    def __init__(self):
        super().__init__()
        # Fully Implement this.
        self.beingedited = False
        
    def doAttrib(self, command=None, args=None):
        commlist = {"string": doString,
                    "list": doList,
                    "intlist": dointList,
                    "dict": doDict,
                    "integer": doInteger,
                    "description": doDescription}
        
        if args is None or command is None:
            log.error("args and command cannot be None")
        
        commtype, commset = self.commands[command]
        
        try:
            commlist[commtype](self, command, args, commset)
        except Exception as err:
            log.error(f"A command failed: {command} {args} error returned: {err}")


def doString(theobject=None, thestring=None, value=None, inset=None):
    if theobject is None:
        raise SyntaxError("No object given to doString. doString:olc.py")
    elif thestring is None:
        raise SyntaxError("No name given to doString:olc.py")
    elif value is None:
        return getattr(theobject, f"{thestring}")
    else:
        value = value.strip()
        if value and len(value) < 50:
            if inset is not None and value not in inset:
                raise SyntaxError(f"I'm sorry, valid options are: {inset}")
            setattr(theobject, thestring, value)
        else:
            raise SyntaxError("Strings must be between 3 and 15 characters.")


def doList(theobject=None, thestring=None, value=None, inset=None):
    if theobject is None:
        raise SyntaxError("No object given to doList.")
    elif thestring is None:
        raise SyntaxError("No name given to doList.")
    elif value is None:
        return getattr(theobject, f"{thestring}")
    else:
        value = value.lower().strip()
        if value and len(value) < 30:
            if inset is not None and value not in inset:
                raise SyntaxError(f"I'm sorry, valid options are: {inset}")
            theattrib = getattr(theobject, f"{thestring}")
            if value in theattrib:
                theattrib.remove(value)
            else:
                theattrib.append(value)


def dointList(theobject=None, thestring=None, value=None, inset=None):
    if theobject is None:
        raise SyntaxError("No object given to doList.")
    elif thestring is None:
        raise SyntaxError("No name given to doList.")
    elif value is None:
        return getattr(theobject, f"{thestring}")
    else:
        try:
            value = int(value)
        except:
            raise SyntaxError("I'm sorry, thats not an integer!")
        if inset is not None and value not in inset:
            raise SyntaxError(f"I'm sorry, valid options are: {inset}")
        theattrib = getattr(theobject, f"{thestring}")
        if value in theattrib:
            theattrib.remove(value)
        else:
            theattrib.append(value)


def doInteger(theobject=None, thestring=None, value=None, inset=None):
    if theobject is None:
        raise SyntaxError("No object given to doInteger.")
    elif thestring is None:
        raise SyntaxError("No name given to doInteger.")
    elif value is None:
        return getattr(theobject, f"{thestring}")
    else:
        value = value.lower().strip()
        try:
            value = int(value)
        except:
            raise SyntaxError("That is not a number.")
        if inset is not None and value not in inset:
            raise SyntaxError(f"I'm sorry, valid options are: {inset}")
        setattr(theobject, thestring, value)


def doDict(theobject=None, thestring=None, args=None, sets=None):
    key = args.split()[0]
    value = ' '.join(args.split()[1:])
    keyset, valueset = sets
    if theobject is None:
        raise SyntaxError("No object given to doDict.")
    elif thestring is None:
        raise SyntaxError("No name given to doDict.")
    elif key is None:
        theattrib = getattr(theobject, f"{thestring}")
        return theattrib
    elif value is None:
        theattrib = getattr(theobject, f"{thestring}")
        if key in theattrib:
            return theattrib[key]
        else:
            raise SyntaxError("Key not found in doDict.")
    else:
        theattrib = getattr(theobject, f"{thestring}")
        if keyset is not None and key not in keyset:
            raise SyntaxError("Key not in key set in doDict.")
        if valueset is not None and value not in valueset:
            raise SyntaxError(f"Value {value} not in value set {valueset} in doDict.")
        if "delete" in value:
            del theattrib[key]
        else:
            theattrib[key] = value


def doDescription(theobject=None, thestring=None, value=None, set=None):
    if theobject is None:
        raise SyntaxError("No object give to doDescription.")
    elif thestring is None:
        raise SyntaxError("No name given to doDescription.")
    else:
        value = getattr(theobject.builder.building, thestring)
        theobject.builder.editing = Buffer(value)
        theobject.builder.editing_obj_name = f"{thestring}"
        theobject.builder.write(theobject.builder.editing.display())


class Buffer(object):
    def __init__(self, oldbuffer=None):
        super().__init__()
        if oldbuffer is not None:
            self.lines = oldbuffer.split("\n")
        else:
            self.lines = []
        self.commands = {".ld": self.delete_line,
                         ".lr": self.replace_line,
                         ".li": self.insert_line,
                         ".si": self.space_insert,
                         ".d": self.delete_word,
                         ".r": self.replace_word,
                         ".c": self.clear,
                         ".s": self.display,
                         ".sc": self.spellcheck,
                         ".f": self.formattext,
                         ".h": self.helpfunc,
                         "@": self.done}

    @staticmethod
    def spellcheck(args):
        return False

    def add(self, args):
        self.lines.append(args)
        return False

    def delete_line(self, args):
        try:
            linenumber = int(args.split()[0])
            self.lines.pop(linenumber)
        except:
            return "There has been an error processing your request"
        return False
    
    def insert_line(self, args):
        try:
            data = args.split()
            linenumber = int(data[0])
            text = ' '.join(data[1:])
            self.lines.insert(linenumber, text)
        except:
            return "There has been an error processing your request"
        return False
    
    def space_insert(self, args):
        try:
            data = args.split()
            linenumber = int(data[0])
            amount = int(data[1])
            self.lines[linenumber] = (' ' * amount) + self.lines[linenumber]
        except:
            return "There was an error processing your request"
        return False

    def replace_line(self, args):
        try:
            data = args.split()
            linenumber = int(data[0])
            text = ' '.join(data[1:])
            self.lines[linenumber] = text
        except:
            return "There was an error processing your request."
        return False

    def replace_word(self, args):
        try:
            data = args.split()
            linenumber = int(data[0])
            old = data[1]
            new = data[2]
            if old in self.lines[linenumber]:
                self.lines[linenumber] = self.lines[linenumber].replace(old, new)
        except:
            return "There was an error processing your request."
        return False

    def delete_word(self, args):
        try:
            data = args.split()
            linenumber = int(data[0])
            text = " ".join(data[1:])
            if text in self.lines[linenumber]:
                self.lines[linenumber] = self.lines[linenumber].replace(text, '')
        except:
            return "There was an error processing your request."
        return False

    def clear(self, args):
        self.lines = []
        return False

    def done(self, args):
        self.lines = "\n\r".join(self.lines)
        return True

    def display(self, args=None):
        output = ["-=-=-=-=-=-=-=-=-= Entering Edit Mode =-=-=-=-=-=-=-=-=-".center(76),
                  "Type {W.h{x for help, {W.s{x to show the text or {W@{x to exit.".center(76),
                  "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-".center(76)]
        for number, line in enumerate(self.lines):
            output.append(f"{number}: {line}")
        return "\n\r".join(output)

    @staticmethod
    def helpfunc(args):
        return (".ld #             Delete the given line number.\n\r"
                ".lr # text        Replace the given line number with text.\n\r"
                ".li # text        Inserts the text above line number #\n\r"
                ".si # amount      Inserts the amount of spaces on line #\n\r"
                ".d # the text     Delete 'the text' on line number #.\n\r"
                ".r # old new      Replace old text with new text.\n\r"
                ".c                Clear the entire buffer.  {R(Beware!){x.\n\r"
                ".sc word          Spell check the given word {W(Broken){x.\n\r"
                ".s                Show the string so far.\n\r"
                ".f                Format the text to 80 characters wide.\n\r"
                "                  {y(Do not do the above on preformatted text){x\n\r"
                ".h                This help screen.\n\r"
                "@                 Exit this editor.\n\r")

    def formattext(self, args):
        formatter = textwrap.TextWrapper(width=76)
        self.lines = formatter.wrap(" ".join(self.lines))
        return False

on run argv
    tell application "Finder"
    set UnixPath to POSIX path of ((path to me as text) & "::")
    set fullfilepath to UnixPath & item 1 of argv
    set desktop picture to POSIX file fullfilepath
    end tell
end run

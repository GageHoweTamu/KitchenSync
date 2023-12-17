# KitchenSync
A private client-to-client file sync app

~70% done

When loading the app, the user can choose whether to host a sync to another device or sync files from a host.

If Host is selected, the app displays the system info required to start an SSH connection: IP, Username, and Port.
If Guest is selected, the app prompts the user to fill in the SSH data from the host.

usually, an SSH connection and file transfer would only be a few lines in a terminal. However, I aimed to make this app as simple and non-techie-friendly as possible.


The lesson here is... don't spend days making an app that what is easily automated with a sh script.

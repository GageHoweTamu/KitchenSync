

### there are no plans to continue development on this project. I'll probably get around to rewriting it in rust one of these days

KitchenSync is a private client-to-client file sync app. When loading the app, the user can choose whether to host a sync to another device or sync files from a host. If Host is selected, the app displays the system info required to start an SSH connection: IP, Username, and Port. If Guest is selected, the app prompts the user to fill in the SSH data from the host.

Usually, an SSH connection and file transfer would only be a few lines in a terminal. However, I aimed to make this app as simple and non-techie-friendly as possible.    

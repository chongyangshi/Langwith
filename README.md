# Langwith
Easy server monitoring on command line.

##What is it?
Langwith is a server monitoring tool for displaying the status of your servers in your terminal. It supports three methods of checks: TCP Port, Ping and HTTP(S) Response.

The interface, implemented in [curses](https://docs.python.org/2/library/curses.html) provides a single-page at-a-glance style display, suitable for putting up on a monitor or projector screen.

Checks are initiated from the system that is running the script. Langwith can also run in the SSH shell of a remote server. No configuration is needed on servers being monitored, although it's a good idea to make sure that the monitored servers are reachable from the system running the program, in order to prevent false positives.

Optionally, if the system running the script is audio-capable (e.g. desktop machine), an alarm can be set to go off when a monitored server goes offline.

##Interface
![1](https://i.imgur.com/MGvcZkE.png All servers are up.)

![1](https://i.imgur.com/1ITo0Fu.png Some servers are down.)

##Installation
Langwith can run on most Linux distributions, Mac OS X, Windows (as of Oct 2016) and potentially BSDs (although untested).

Langwith is written for [Python 3](https://www.python.org/downloads/). It requires some other Python libraries.

If you are using a linux distribution, you may wish to install **python(3)-dev**, **libffi-dev** and **libssl-dev** or their equivalents on non-Debian/Ubuntu distros, for example:

    apt-get install python3-dev libffi-dev libssl-dev python3-setuptools python3-wheel python3-pip

Please first have [pip](https://pip.pypa.io/en/stable/installing/) installed, then switch to the source directory of Langwith and execute:

    python3 setup.py

This should install all dependencies required.

Then you can download or git clone Langwith, and configure it as explained below.

##Configuration

###Langwith Settings

Edit **settings.json**, set the interval (15 - 300, in seconds) you would like for Langwith to run all checks (*refresh_interval*); and set *play_alarm* to *true* or *false* depends on whether you want a short alarm to go off when a server goes offline.

####Email Notifications (Optional)

You can also set Langwith to notify you via email when a server goes down. To avoid creating problems by sending emails through SMTP from your device, Langwith can be used with [Mailgun](https://mailgun.com) sending service, which provides you with a free monthly sending allowance of 10,000 emails. If you want to make Langwith send notification emails, you need to register a free account at [Mailgun](https://mailgun.com), and verify your email sending domain. 

In **settings.json**, you can then set *mail_notification* to *true*, *mailgun_domain* to your verified email sending domain, *mailgun_key* to your API key from Mailgun like *"key-abcdefghijklmnopqrstuvwxyz"* and *mail_notification_recipients* to a list of email addresses you wish to be notified when a server goes down, for example: *["your_mailbox1@example.com", "your_mailbox2@example.com"]*.

### Server Settings

Edit **servers.json**, configure the servers you want to monitor. Some examples are already in there, you may change or delete them at your convenience.

Configurations for individual checks by type:

**TCP Port**

    "Name for your TCP Port Check": {
       "type": "port",
        "host": "IP Address or Domain",
        "port": {Integer TCP port number}
    },

**Ping**

    "Name for your Ping Check": {
        "type": "ping",
        "host": "IP Address or Domain",
    },

If your domain is on dynamic DNS, Langwith will attempt to resolve the domain name at every re-check, and use the first A record returned.

**HTTP(S)**

    "Name for your HTTP(S) Check": {
        "type": "http",
        "url": "Full HTTP(S) URL for access attempt",
        "verify_TLS": true,
        "look_for": "String to be looked for on the accessed content, check will return fail if string not found",
        "auth_user": "username",
        "auth_pass": "password"
    }

Set *verify_TLS* to *false* if you do not want TLS server's certificate to be verified. It is true by default.

Omit *auth_user* and *auth_user* if simple HTTP authentication is not required on the monitored server.

You can set Langwith to check if the accessed content contains a string, as defined in *look_for*. It can also be omitted when not required.

For example configurations, see the default **servers.json**.

To run Langwith, ensure that the terminal size is sufficient for the number of entries to display, and change to the directory containing Langwith's code. Run:
    python main.py


##Feedback, Bug Reports, and Pull Requests
This is my first attempt at using curses, so I expect my implementation to be far from perfect.

Feedback, bug reports and pull requests are very welcome.
You can also contact me at shi[AT]ebornet.com .

###ToDos

- ~~SMTP email notification when a server goes offline, or potentially through an email sending service's API.~~ Email notifications now available with Mailgun API.

- Past uptime records stored locally.


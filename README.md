'''GPUcli.py''' is a command line tool written in python which allows you to upload media to your '''Google Photos''' account.

At this moment the tool will '''NOT''' walk through directory trees. It will upload media from a given directory.
It's possible to use the '''ALBUM''' switch, which will make this tool create an album named by the source folder name. The uploaded media 
will be added to this album.

=== Donation ===
Since I'm developing in my free time I'd like to ask you to support my work.
This will give me motivation to keep on coding and fixing bugs.

Thanks in advance

[https://www.paypal.com/cgi-bin/webscr?no_note=0&lc=US&business=realriot%40realriot.de&item_name=GitHub+-+GPUcli&cmd=_donations&currency_code=USD '''DONATE NOW VIA PAYPAL''']

=== Requirements ===
There are some requirements which have to be fulfilled to make this tool work.
* You have to enable '''Google Photos API''' within the google cloud console (https://console.cloud.google.com/apis)
* You have to create an OAuth-Client-ID within this console.    
* Remove any existing client permissions on first start: https://myaccount.google.com/u/0/permissions.

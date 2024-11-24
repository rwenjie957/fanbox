# fanbox
a simple crawler which can donwload pictures or files in fanbox

# usage
## command line
python3 fanbox_cli.py

- -c --config [config_file]

choose config file, default 'config.json'

- -f --forward                

whether download the previous or next posts, default is downloading the next posts

- -s --save-path [save-path]  

where to save the pictures you have downloaded

- -l --log-file [log-file]    

the log file which recorded the posts that have downloaded

- -m --mode [single/multiple]
download with a thread or multiple threads, default is multiple

- -r --re-download
In my tests, sometimes some pictures may fail to download, you can either use this choice to re-download the latest post or user -i to download the specific post again 

- -i --id

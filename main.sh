chmod +x phantomjs
PATH=$PATH:/geckodriver.tar.gz
python3 bot.py &
python3 server.py
# bimabookupdate12

lt --port 8000 --subdomain experiya --local-host "127.0.0.1" -o --print-requests
 
lt -p 8000 -s experiya -l "127.0.0.1" -o

NOTE: FIREWALL AND ANTIVIRUS SHOULD BE TURNED OFF !!!

cd ExperiyaBook
sudo apt install screen
screen -S exp
sudo apt install python3-pip -y
pip install -r requirements.txt
python3 manage.py runserver 0.0.0.0:8000
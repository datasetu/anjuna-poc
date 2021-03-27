from	amazonlinux

workdir	/src

copy	requirements.txt .
copy	app.py .

run	yum -y install python3 python3-pip  &&  \
	pip3 install -r requirements.txt

cmd	["python3", "app.py"]

all:
	echo “########Updating apt-get#########”
	sudo apt-get update
	echo “########Installing packages######”
	sudo apt-get install python3
	sudo apt-get install python3-pip
	echo “#########Done####################”
	echo “#########Copying Binaries########”
	sudo echo '#!/usr/bin/python3' | cat - chord.py > temp && mv temp chord.py
	sudo cp -pf chord.py /usr/bin/chord	
	sudo chmod 755 /usr/bin/chord
	echo “#########All Done################”

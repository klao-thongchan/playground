sudo apt-get install -y software-properties-common
sudo add-apt-repository -u ppa:lightningnetwork/ppa
sudo apt-get install lightningd snapd
sudo snap install bitcoin-core
sudo ln -s /snap/bitcoin-core/current/bin/bitcoin{d,-cli} /usr/local/bin/
# Return a p2sh-segwit address
lightning-cli newaddr p2sh-segwit
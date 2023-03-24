const btn = document.querySelector('.send__data__btn');
//The folloring function was influenced by a guide from the following webaddress
//https://rahulbaran.hashnode.dev/how-to-send-json-from-javascript-to-flask-using-fetch-api
btn.addEventListener('click', function () {

    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'getWalletValues' : 'data from user',
        })
    })
    .then(function (response){

        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response);
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
    .catch(function(error) {
        console.log(error);
    });
});

const initialize = async () => {
  //Some parts of the following code is from the metamask "create a simple dapp" tutorial
  //https://docs.metamask.io/guide/create-dapp.html
  //onClickConnect
  const onboardButton = document.getElementById('connectButton');
  const getAccountsButton = document.getElementById('getAccounts');
  const getAccountsResults = document.getElementById('getAccountsResult');
  const isMetaMaskInstalled = () => {
    //Have to check the ethereum binding on the window object to see if it's installed
    const { ethereum } = window;
    return Boolean(ethereum && ethereum.isMetaMask);
  };

  //------Inserted Code------\\
  const onClickConnect = async () => {
    const accountObj = {account: -1};
    try {
      // Will open the MetaMask UI
      // You should disable this button while the request is pending!
      const _accounts = await ethereum.request({ method: 'eth_requestAccounts' });
      accountObj.account = _accounts[0];
    } 
    catch (error) {
      console.error(error);
    }
    //End of metamask simple dapp example code
    finally{
     fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify(accountObj)
    })
    .then(function (response){

        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response);
            });
        }
        else {
            throw Error('Something went wrong');
        }
    }) 
    }
    
  };
    //This is modified code from the from the metamask "create a simple dapp" tutorial 
    //https://docs.metamask.io/guide/create-dapp.html
    getAccountsButton.onclick = async () => {
      try {
        const _accounts = await ethereum.request({
          method: 'eth_accounts',
        })
        document.getElementById('getAccountsResults').value = _accounts[0] || 'Not able to get accounts'
      } catch (err) {
        console.error(err)
        document.getElementById('getAccountsResults').value = `Error: ${err.message}`;
      }
    };
  const MetaMaskClientCheck = () => {
    //Now we check to see if Metmask is installed
    if (!isMetaMaskInstalled()) {
      //If it isn't installed we ask the user to click to install it
      onboardButton.innerText = 'Click here to install MetaMask!';
      //When the button is clicked we call th is function
      onboardButton.onclick = onClickInstall;
      //The button is now disabled
      onboardButton.disabled = false;
    } else {
      //If MetaMask is installed we ask the user to connect to their wallet
      onboardButton.innerText = 'Connect';
      //When the button is clicked we call this function to connect the users MetaMask Wallet
      onboardButton.onclick = onClickConnect;
      //The button is now disabled
      onboardButton.disabled = false;
    }
  };
  MetaMaskClientCheck();
  //------/Inserted Code------\\
};

window.addEventListener('DOMContentLoaded', initialize)

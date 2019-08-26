debug = false;

window.onload = function() {

    checkAuthenticated();
}

function printLog(message) {
    if (debug) {
        console.log(message);
    }
}

function checkAuthenticated() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/authenticated');
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        var response = JSON.parse(xhr.responseText);

        printLog(response);
        if (response.data) {
            printLog("Logged in");
            showSignInBtn(false);
        }
        else {
            printLog("Not logged in");
            showSignInBtn(true);
        }
    }
    xhr.send();
}


function showSignInBtn(setVisible) {
    if(setVisible) {
        $('.google-auth, .facebook-auth').css('display', 'block');
        $('.sign-out').css('display', 'none');
    }
    else {
        $('.google-auth, .facebook-auth').css('display', 'none');
        $('.sign-out').css('display', 'block');
    }
}


function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        printLog('User signed out.');
    });

    logout();
}


function logout() {
    printLog("Attempting logout...");
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/logout');
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        printLog("Logging out the user");
        $('.result').html("Successfully logged out! Redirecting in 2 seconds...");
        setTimeout(function() {
            window.location.href = '/';
        }, 2000);
    }
    xhr.send('logout=true');
}


function onSignIn(googleUser) {
    printLog("Enter onSignIn()"); 

    var id_token = googleUser.getAuthResponse().id_token;

    var state = $('#state').data().state;

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/gconnect');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        var profile = googleUser.getBasicProfile();

        printLog('Signed in as: ' + profile.getName());

        var server_response = JSON.parse(xhr.responseText);

        // If data is true, it means that the user is authenticated and needs to refresh page
        if (server_response.data) {
            $('.result').html("Successfully logged in as " + profile.getName() + ". Redirecting in 4 seconds...");
            setTimeout(function() {
                window.location.href = "/";
            }, 4000);
        }
    };
    xhr.send('idtoken=' + id_token + '&state=' + state);
}
function encryptMessage(){
    message = document.getElementById('message').value.toString();
    pass = document.getElementById('pass').value.toString();
    var encrypted = CryptoJS.AES.encrypt(message, pass).toString();
    alert(encrypted)

}

function decryptMessage(){
    message = document.getElementById('encrypted_message').value.toString();
    pass = document.getElementById('passp').value.toString();
    var decrypted = CryptoJS.AES.decrypt(message, pass);
    decrypted = decrypted.toString(CryptoJS.enc.Utf8);
    alert(decrypted)
    //aaa
}

function hashMessage(){
    message = document.getElementById('message').value.toString();
    var hash = CryptoJS.SHA3(message, { outputLength: 224 });
    element = document.getElementById('OutputTextArea');
    element.innerHTML = hash;
    alert(hash)
}
function viewTheorem() {
    var xhttp = new XMLHttpRequest();
    var input = document.getElementById('upload');
    var upload = input.files[0]
    var theorem = upload.name;
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var fileContent = this.responseText;
            localStorage.setItem('fileContent', fileContent);
            var url = "/display?title=theorem&file=uploads/" + theorem;
            window.open(url, "_blank");
        }
    }
    xhttp.open("GET", "/display?title=theorem&file=uploads/" + theorem, true);
    xhttp.send();

}
function loadTrace() {
    var xhttp = new XMLHttpRequest();
    var txHash = document.getElementById('tx-hash').value;
    var fileName = 'trace-' + txHash + '.txt';
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("content").innerHTML = this.responseText;
        }
    };

    url = "/display?title=trace&file=" + encodeURIComponent(fileName);
    var newWindow = window.open(url, '_blank');
    newWindow.focus();
}

function boogieOutput() {
    var xhttp = new XMLHttpRequest();
    var txHash = document.getElementById('tx-hash').value;
    var fileName = 'trace-' + txHash + '.bpl';
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("content").innerHTML = this.responseText;
        }
    };

    url = "/display?title=boogie&file=" + encodeURIComponent(fileName);
    var newWindow = window.open(url, '_blank');
    newWindow.focus();
}

function uploadFile() {
    var input = document.getElementById("upload");
    var file = input.files[0];
    var txHash = document.getElementById("tx-hash").value;

    if (file && txHash) {
        if (file.type != "application/json") {
            console.log("File is not a JSON file.");
            return;
        }

        var formData = new FormData();
        formData.append('file', file);
        formData.append('tx-hash', txHash);

        fetch('/trace', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                getBoogieResult(data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    } else {
        console.log("No file selected or text field empty!");
    }
}

function getBoogieResult(data) {
    var text = document.createElement("pre");
    text.innerHTML = data["boogie-output"];
    
    var form_container = document.createElement("div");
    form_container.setAttribute("class", "form-container")
    
    var boogie_result = document.createElement("div");
    boogie_result.setAttribute("id", "boogie-result");
    
    boogie_result.appendChild(text);
    form_container.appendChild(boogie_result);
    
    if (data["boogie-output"].indexOf("0 errors") != -1) {
        var gif = document.createElement("img");
        gif.setAttribute("id", "confetti-gif")
        gif.src = 'static/confetti.gif';
        form_container.appendChild(gif);
    }
    
    document.body.appendChild(form_container);
}